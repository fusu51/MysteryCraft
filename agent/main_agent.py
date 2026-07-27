import time
import shutil
from pathlib import Path

from agent.subagents.script_structure_agent import script_structure_agent
from agent.subagents.logic_validator_agent import logic_validator_agent
from agent.subagents.network_search_agent import network_search_agent

import asyncio
import aiosqlite
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from tools.pdf_tools import convert_md_to_pdf
from tools.upload_file_read_tool import read_file_content
from tools.script_tools import build_character_sheet, generate_clue_cards, build_timeline, generate_dm_manual

from deepagents import create_deep_agent

from agent.llm import model
from agent.prompts import main_agent_content

from api.monitor import monitor
from api.context import set_session_context, reset_session_context, set_thread_context
from api.trace import log_event


_project_root = Path(__file__).parents[1]


def _get_checkpointer():
    db_path = _project_root / "data" / "checkpoints.db"
    db_path.parent.mkdir(parents=True, exist_ok=True)
    async def _init():
        conn = await aiosqlite.connect(str(db_path))
        return AsyncSqliteSaver(conn)
    return asyncio.run(_init())


main_agent = create_deep_agent(
    model=model,
    system_prompt=main_agent_content['system_prompt'],
    tools=[convert_md_to_pdf, read_file_content,
           build_character_sheet, generate_clue_cards, build_timeline, generate_dm_manual],
    checkpointer=_get_checkpointer(),
    subagents=[
        script_structure_agent,
        network_search_agent,
        logic_validator_agent,
    ],
)

project_root_path = Path(__file__).parents[1].resolve()


async def run_deep_agent(task_query: str, session_id: str):
    """异步流式执行主智能体，全过程 trace 日志"""
    _start = time.perf_counter()

    log_event(session_id, "TASK", f"任务开始 | query={task_query[:50]}...")
    log_event(session_id, "DIM", f"当前会话的main_agent开始执行了！ 会话id:{session_id}")

    # ===== 准备阶段 =====
    session_dir = project_root_path / "output" / f"session_{session_id}"
    session_dir.mkdir(parents=True, exist_ok=True)
    session_dir_str = str(session_dir).replace("\\", "/")
    relative_session_dir_str = str(session_dir.relative_to(project_root_path)).replace("\\", "/")

    # 上传文件处理
    updated_dir_path = project_root_path / "updated" / f"session_{session_id}"
    updated_info_prompt = ""
    if updated_dir_path.exists():
        files = [f.name for f in updated_dir_path.iterdir() if f.is_file()]
        if files:
            for filename in files:
                shutil.copy2(updated_dir_path / filename, session_dir / filename)
            updated_info_prompt = (
                    f"\n    [已上传文件] 已加载到工作目录:\n" +
                    "\n".join([f"    - {f}" for f in files]) +
                    "\n    请优先使用工具（read_file_content）读取并参考这些文件。"
            )
            log_event(session_id, "DIM", f"上传文件: {len(files)} 个")

    # ContextVar 隔离
    session_dir_token = set_session_context(session_dir_str)
    session_id_token = set_thread_context(session_id)
    monitor.report_session_dir(session_dir_str)

    # ===== 执行 =====
    config = {"configurable": {"thread_id": session_id}}

    path_instruction = f"""
    【工作环境指令】
    工作目录: {relative_session_dir_str}
    {updated_info_prompt}

    剧本文件生成规则：
    1. 所有剧本文件必须保存到工作目录：'{relative_session_dir_str}/filename'
    2. 使用以下专用工具生成各类剧本文件：
       - generate_dm_manual   → 组织者手册（DM手册）
       - build_character_sheet → 单个角色的角色剧本（每个角色调用一次）
       - generate_clue_cards   → 线索卡汇总
       - build_timeline        → 案件时间线
    3. 读取已上传的文件时，直接将文件名作为 filename 参数传入 read_file_content 工具，不要带目录前缀。
    4. 一律使用相对路径（仅文件名或 '文件名.md'），禁止使用绝对路径。
    5. 若存在上传文件，请先分析内容再开始创作。
    """

    tool_count = 0
    agent_call_count = 0

    try:
        async for chunk in main_agent.astream(
                {"messages": [{"role": "user", "content": task_query + path_instruction}]},
                config=config,
        ):
            for node_name, state in chunk.items():
                if not state or "messages" not in state:
                    continue
                messages = state["messages"]
                if not (messages and isinstance(messages, list)):
                    continue

                last_msg = messages[-1]

                if node_name == "model":
                    if last_msg.tool_calls:
                        for tool_call in last_msg.tool_calls:
                            tool_name = tool_call.get("name", "?")
                            tool_count += 1

                            if tool_name == "task":
                                # 子智能体调用
                                agent_call_count += 1
                                subagent = tool_call["args"]["subagent_type"]
                                desc_len = len(tool_call["args"].get("description", ""))
                                log_event(session_id, "AGENT", f"{subagent} 调用 (#{agent_call_count})",
                                          detail={"desc_len": desc_len})
                                monitor.report_assistant(subagent, {"description": tool_call["args"]["description"]})
                            else:
                                # 主智能体直接调工具
                                log_event(session_id, "TOOL", f"{tool_name} (#{tool_count})",
                                          detail={"args": tool_call.get("args", {})})

                    elif last_msg.content:
                        # 最终输出
                        content_preview = last_msg.content[:200].replace("\n", " ")
                        log_event(session_id, "TASK", f"Agent 输出: {content_preview}...")
                        monitor.report_task_result(last_msg.content)

                elif node_name == "tools":
                    # 工具执行完毕（仅检测错误）
                    for msg in messages:
                        if hasattr(msg, "content") and isinstance(msg.content, str):
                            if "错误" in msg.content[:50] or "失败" in msg.content[:50]:
                                name = getattr(msg, "name", "?")
                                log_event(session_id, "ERROR", f"工具 {name} 异常: {msg.content[:200]}",
                                          level="ERROR")

    except Exception as e:
        err_msg = str(e)
        err_type = type(e).__name__

        # 分类
        if any(k in err_msg.lower() for k in ("401", "403", "unauthorized", "invalid api key", "authentication")):
            category = "AUTH"
            hint = "API Key 无效或已过期，请检查 .env 中的 OPENAI_API_KEY"
            level = "ERROR"
            recoverable = False
        elif any(k in err_msg.lower() for k in ("429", "rate limit", "too many requests")):
            category = "RATE"
            hint = "API 频率限制，建议稍后重试或降低请求频率"
            level = "WARNING"
            recoverable = True
        elif any(k in err_msg.lower() for k in ("timeout", "timed out", "connection", "network")):
            category = "NETWORK"
            hint = "网络超时，请检查服务器网络连接或 API 端点可达性"
            level = "WARNING"
            recoverable = True
        else:
            category = "UNKNOWN"
            hint = "请查看 trace.jsonl 获取完整错误信息"
            level = "ERROR"
            recoverable = False

        log_event(session_id, category, f"{err_type}: {err_msg[:200]}",
                  detail={"error_type": err_type, "hint": hint, "recoverable": recoverable},
                  level=level)
        monitor._emit("error", f"[{category}] {hint}: {err_msg[:200]}")
    finally:
        reset_session_context(session_dir_token, session_id_token)

        # 统计输出文件
        file_count = 0
        if session_dir.exists():
            file_count = sum(1 for _ in session_dir.rglob("*") if _.is_file())

        total_sec = time.perf_counter() - _start
        log_event(session_id, "TASK", f"任务结束 | "
                                      f"耗时={total_sec:.0f}s | 工具调用={tool_count}次 | 子智能体={agent_call_count}次 | "
                                      f"输出文件={file_count}个")
