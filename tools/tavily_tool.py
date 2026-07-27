"""网络搜索工具 — Tavily 封装 + 硬计数器"""
import time
import os
from typing import Literal
from langchain_core.tools import tool
from tavily import TavilyClient
from dotenv import load_dotenv

from api.monitor import monitor
from api.context import get_thread_context

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))

# 模块级计数器（每个 thread 独立计数）
_tavily_counter: dict[str, int] = {}
MAX_SEARCH = 8

# 全局限流：两次搜索间隔 ≥ 2 秒，防止 API 额度瞬间耗尽
_global_last_call = 0.0
_GLOBAL_COOLDOWN = 2.0


@tool
def internet_search(
        query: str,
        topic: Literal["news", "finance", "general"] = "general",
        max_results: int = 5,
        include_raw_content: bool = False,
):
    """
    根据用户问题进行网络信息搜索。

    剧本杀创作时建议的搜索维度：
    1. 时代背景细节 — 搜索服饰/建筑/交通/饮食/社会规则等
    2. 真实案件素材 — 搜索历史上真实犯罪案例
    3. 场景氛围描写 — 搜索特定场景的感官细节

    注意：主要用于搜索公开的网络信息，数据库查询或内部知识库检索请用其他工具。

    :param query: 用户的查询信息
    :param topic: 查询类型 (news/finance/general)
    :param max_results: 返回的最大条数
    :param include_raw_content: 是否返回原始内容（False=精简, True=详细）
    :return: 搜索结果
    """
    thread_id = get_thread_context() or "unknown"
    _tavily_counter.setdefault(thread_id, 0)

    # 硬上限拦截
    if _tavily_counter[thread_id] >= MAX_SEARCH:
        return (
            f"⚠️ 网络搜索已达上限（{MAX_SEARCH}次）。"
            f"已搜索 {_tavily_counter[thread_id]} 次，请基于已有信息继续工作，不要再发起搜索。"
        )

    _tavily_counter[thread_id] += 1
    current = _tavily_counter[thread_id]

    # 全局限流
    global _global_last_call
    elapsed = time.time() - _global_last_call
    if elapsed < _GLOBAL_COOLDOWN:
        time.sleep(_GLOBAL_COOLDOWN - elapsed)
    _global_last_call = time.time()

    _t0 = time.perf_counter()
    monitor.report_tool(
        tool_name=f"网络搜索 ({current}/{MAX_SEARCH})",
        args={"query": query, "topic": topic},
    )

    try:
        result = tavily_client.search(
            query=query, topic=topic,
            max_results=max_results, include_raw_content=include_raw_content,
        )
    except Exception as e:
        return (f"❌ 网络搜索失败: {e}。"
                f"请检查 Tavily API Key 是否有效，或网络是否可达。"
                f"你可以跳过此工具，基于已有信息继续工作。")

    dt = time.perf_counter() - _t0
    result_len = len(str(result))
    monitor.report_tool(
        tool_name=f"网络搜索 ({current}/{MAX_SEARCH}) 完成",
        args={"duration": round(dt, 2), "result_chars": result_len},
    )

    return result
