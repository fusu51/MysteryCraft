"""
端到端测试脚本 — 测试剧本杀 DM 创作助手全链路

用法:
    # 全部测试
    python tests/test_e2e.py

    # 只测数据库
    python tests/test_e2e.py --db-only

    # 只测 API（需先启动服务）
    python tests/test_e2e.py --api-only
"""
import sys
import json
import asyncio
import argparse
from pathlib import Path

# 确保项目根目录在 sys.path 中
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))

PASS = "✅"
FAIL = "❌"
WARN = "⚠️"


def test_db_tools():
    """测试1：数据库查询工具"""
    print("\n" + "=" * 60)
    print("测试1：数据库查询工具")
    print("=" * 60)

    from tools.script_db_tools import (
        search_character_archetypes,
        search_trick_patterns,
        search_script_templates,
        search_plot_patterns,
    )

    results = []

    # 1.1 角色原型
    r = search_character_archetypes.invoke({"era": "民国", "role_type": "嫌疑人"})
    ok = "表面温和的管家" in r or "风情万种的歌女" in r
    results.append(("角色原型查询（民国+嫌疑人）", ok, r[:100]))

    # 1.2 诡计模式
    r = search_trick_patterns.invoke({"category": "密室", "difficulty": 3})
    ok = "密室" in r
    results.append(("诡计模式查询（密室+难度≤3）", ok, r[:100]))

    # 1.3 剧本模板
    r = search_script_templates.invoke({"template_type": "本格", "player_count": 6})
    ok = "本格" in r
    results.append(("剧本模板查询（本格+6人）", ok, r[:100]))

    # 1.4 剧情模式
    r = search_plot_patterns.invoke({"pattern_type": "封闭空间"})
    ok = "封闭空间" in r or "暴风雪山庄" in r
    results.append(("剧情模式查询（封闭空间）", ok, r[:100]))

    # 1.5 无筛选查询
    r = search_character_archetypes.invoke({"era": "", "role_type": ""})
    ok = len(r) > 100  # 应该返回大量数据
    results.append(("角色原型查询（无筛选，有数据）", ok, f"返回长度: {len(r)}"))

    for name, ok, detail in results:
        icon = PASS if ok else FAIL
        print(f"  {icon} {name} | {detail[:80]}")

    return all(r[1] for r in results)


def test_main_agent_import():
    """测试2：主智能体导入 + 工具注册"""
    print("\n" + "=" * 60)
    print("测试2：主智能体导入")
    print("=" * 60)

    results = []

    # 2.1 导入主智能体
    try:
        from agent.main_agent import main_agent, run_deep_agent
        results.append(("main_agent 导入", True, ""))
    except Exception as e:
        results.append(("main_agent 导入", False, str(e)))
        return False

    # 2.2 导入新工具
    try:
        from tools.script_tools import (
            build_character_sheet,
            generate_clue_cards,
            build_timeline,
            generate_dm_manual,
        )
        results.append(("剧本专用工具导入", True, ""))
    except Exception as e:
        results.append(("剧本专用工具导入", False, str(e)))

    # 2.3 导入子智能体
    subagent_files = [
        ("network_search_agent", "agent.subagents.network_search_agent", "network_search_agent"),
        ("script_structure_agent", "agent.subagents.script_structure_agent", "script_structure_agent"),
        ("logic_validator_agent", "agent.subagents.logic_validator_agent", "logic_validator_agent"),
    ]
    for name, module_path, var_name in subagent_files:
        try:
            mod = __import__(module_path, fromlist=[var_name])
            agent_dict = getattr(mod, var_name)
            agent_name = agent_dict.get("name", "?")
            results.append((f"子智能体 {name}", True, f"name={agent_name}"))
        except Exception as e:
            results.append((f"子智能体 {name}", False, str(e)))

    for name, ok, detail in results:
        icon = PASS if ok else FAIL
        print(f"  {icon} {name} {detail}" if detail else f"  {icon} {name}")

    return all(r[1] for r in results)


def test_api_integration():
    """测试3：API 集成测试（需要服务已启动）"""
    print("\n" + "=" * 60)
    print("测试3：API 集成测试")
    print("=" * 60)

    try:
        import httpx
    except ImportError:
        print(f"  {WARN} 需要 httpx 库: pip install httpx")
        return None  # 跳过而非失败

    BASE = "http://localhost:8000"

    # 检查服务是否在运行
    try:
        r = httpx.get(f"{BASE}/docs", timeout=3)
        if r.status_code != 200:
            print(f"  {FAIL} 服务未运行，请先执行: python api/server.py")
            return False
    except Exception:
        print(f"  {FAIL} 无法连接 http://localhost:8000，请先启动服务")
        return False

    results = []

    # 3.1 提交任务
    query = "写一个3人极简推理剧本，民国背景，只需要DM手册，不需要角色剧本不需要线索卡"
    try:
        r = httpx.post(f"{BASE}/api/task", json={"query": query}, timeout=10)
        ok = r.status_code == 200 and "thread_id" in r.json()
        thread_id = r.json().get("thread_id", "") if ok else ""
        results.append(("POST /api/task", ok, f"thread_id={thread_id[:12]}..."))
    except Exception as e:
        results.append(("POST /api/task", False, str(e)))
        thread_id = ""

    # 3.2 检查 WebSocket 端点可达
    try:
        r = httpx.get(f"{BASE}/openapi.json", timeout=3)
        openapi = r.json()
        ws_paths = [p for p in openapi.get("paths", {}).keys() if p.startswith("/ws")]
        results.append(("WebSocket 端点存在", len(ws_paths) > 0, str(ws_paths)))
    except Exception as e:
        results.append(("WebSocket 端点检查", False, str(e)))

    # 3.3 等待并检查输出文件
    if thread_id:
        session_dir = PROJECT_ROOT / "output" / f"session_{thread_id}"
        print(f"  ... 等待 30 秒让 Agent 执行 ...")
        import time
        time.sleep(30)

        files_found = list(session_dir.rglob("*")) if session_dir.exists() else []
        md_files = [f.name for f in files_found if f.suffix == ".md"]
        ok = len(md_files) > 0
        results.append(
            ("输出文件生成", ok,
             f"找到 {len(md_files)} 个 md 文件: {md_files}")
        )
    else:
        results.append(("输出文件检查", False, "无 thread_id，跳过"))

    for name, ok, detail in results:
        icon = PASS if ok else FAIL
        print(f"  {icon} {name} | {detail[:100]}")

    return all(r[1] for r in results)


def test_context_isolation():
    """测试4：ContextVar 协程隔离"""
    print("\n" + "=" * 60)
    print("测试4：ContextVar 隔离测试")
    print("=" * 60)

    from api.context import set_session_context, get_session_context, reset_session_context

    # 设两个不同值，验证相互隔离
    token_a = set_session_context("session_aaa")
    token_b = set_session_context("session_bbb")

    # 当前取到的应该是最后设的
    val = get_session_context()
    ok1 = val == "session_bbb"

    # 恢复后应该变回 aaa
    reset_session_context(token_b)
    val = get_session_context()
    ok2 = val == "session_aaa"

    # 全部恢复
    reset_session_context(token_a)
    val = get_session_context()
    ok3 = val is None

    results = [
        ("设置后取值", ok1, f"期望 session_bbb, 实际 {get_session_context() if not ok1 else val}"),
        ("reset 一层", ok2, f"期望 session_aaa, 实际 {val}"),
        ("reset 全部", ok3, f"期望 None, 实际 {val}"),
    ]
    for name, ok, detail in results:
        icon = PASS if ok else FAIL
        print(f"  {icon} {name} | {detail}")

    return all(r[1] for r in results)


def test_db_data_counts():
    """测试5：验证预置数据量"""
    print("\n" + "=" * 60)
    print("测试5：预置数据量")
    print("=" * 60)

    import sqlite3
    from data.script_db import DB_PATH

    if not DB_PATH.exists():
        print(f"  {FAIL} 数据库不存在: {DB_PATH}")
        print(f"  请先执行: python data/script_db.py")
        return False

    conn = sqlite3.connect(str(DB_PATH))
    cursor = conn.cursor()

    expected = {
        "character_archetypes": 25,
        "trick_patterns": 18,
        "script_templates": 6,
        "plot_patterns": 10,
    }

    all_ok = True
    for table, expected_count in expected.items():
        cursor.execute(f"SELECT COUNT(*) FROM {table}")
        actual = cursor.fetchone()[0]
        ok = actual >= expected_count
        all_ok = all_ok and ok
        icon = PASS if ok else FAIL
        print(f"  {icon} {table}: {actual} 条 (预期 ≥ {expected_count})")

    conn.close()
    return all_ok


def main():
    parser = argparse.ArgumentParser(description="剧本杀 DM 端到端测试")
    parser.add_argument("--db-only", action="store_true", help="只测数据库")
    parser.add_argument("--api-only", action="store_true", help="只测 API 集成")
    parser.add_argument("--quick", action="store_true", help="快速测试（跳过需服务的测试）")
    args = parser.parse_args()

    print("=" * 60)
    print("  剧本杀 DM 创作助手 — 端到端测试")
    print("=" * 60)

    results = {}

    if args.db_only:
        results["DB工具查询"] = test_db_tools()
        results["预置数据量"] = test_db_data_counts()
    elif args.api_only:
        results["API集成"] = test_api_integration()
    elif args.quick:
        results["DB工具查询"] = test_db_tools()
        results["预置数据量"] = test_db_data_counts()
        results["主智能体导入"] = test_main_agent_import()
        results["ContextVar隔离"] = test_context_isolation()
    else:
        results["DB工具查询"] = test_db_tools()
        results["预置数据量"] = test_db_data_counts()
        results["主智能体导入"] = test_main_agent_import()
        results["ContextVar隔离"] = test_context_isolation()
        results["API集成"] = test_api_integration()

    # 汇总
    print("\n" + "=" * 60)
    print("  测试汇总")
    print("=" * 60)
    passed = 0
    failed = 0
    skipped = 0
    for name, r in results.items():
        if r is None:
            icon = WARN
            skipped += 1
        elif r:
            icon = PASS
            passed += 1
        else:
            icon = FAIL
            failed += 1
        print(f"  {icon} {name}")

    print(f"\n{passed} 通过 | {failed} 失败 | {skipped} 跳过")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
