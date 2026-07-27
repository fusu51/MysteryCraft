"""剧本数据库工具 — 查询函数 + @tool 包装 + 进度计数"""
import sqlite3
from pathlib import Path
from langchain_core.tools import tool
from api.monitor import monitor
from api.context import get_thread_context

DB_PATH = Path(__file__).resolve().parents[1] / "data" / "script.db"

# 模块级计数器
_db_counter: dict[str, int] = {}
TOTAL_DB_TOOLS = 4


def _next_count(thread_id: str) -> int:
    _db_counter[thread_id] = _db_counter.get(thread_id, 0) + 1
    return _db_counter[thread_id]


def _connect():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn


# ---------- 裸查询函数（不变）----------

def query_characters(era: str = None, role_type: str = None, limit: int = 10) -> str:
    conn = _connect()
    cursor = conn.cursor()
    sql = "SELECT id, name, role_type, personality, description, era_fit FROM character_archetypes WHERE 1=1"
    params = []
    if era:
        sql += " AND (era_fit = ? OR era_fit = '任意')"
        params.append(era)
    if role_type:
        sql += " AND role_type = ?"
        params.append(role_type)
    sql += f" LIMIT {limit}"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return "未找到匹配的角色原型"
    result = "角色原型列表：\n"
    for r in rows:
        result += f"  [{r['role_type']}] {r['name']} — {r['personality']} | {r['description']}（适配：[{r['era_fit']}]）\n"
    return result


def query_tricks(category: str = None, difficulty: int = None, limit: int = 10) -> str:
    conn = _connect()
    cursor = conn.cursor()
    sql = "SELECT id, name, category, difficulty, description, classic_examples FROM trick_patterns WHERE 1=1"
    params = []
    if category:
        sql += " AND category = ?"
        params.append(category)
    if difficulty:
        sql += " AND difficulty <= ?"
        params.append(difficulty)
    sql += f" LIMIT {limit}"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return "未找到匹配的诡计模式"
    result = "诡计模式列表：\n"
    for r in rows:
        result += (f"  [{r['category']}] {r['name']} （难度：{'★'*r['difficulty']}） — {r['description']} | "
                   f"参考：{r['classic_examples']}\n")
    return result


def query_templates(template_type: str = None, player_count: int = None, limit: int = 10) -> str:
    conn = _connect()
    cursor = conn.cursor()
    sql = ("SELECT id, name, template_type, player_count, act_structure, clue_distribution, duration_estimate "
           "FROM script_templates WHERE 1=1")
    params = []
    if template_type:
        sql += " AND template_type = ?"
        params.append(template_type)
    if player_count:
        sql += " AND player_count = ?"
        params.append(player_count)
    sql += f" LIMIT {limit}"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return "未找到匹配的剧本模板"
    result = "剧本结构模板：\n"
    for r in rows:
        result += f"  [{r['template_type']}] {r['name']} ({r['player_count']}人/{r['duration_estimate']})\n"
        result += f"    幕结构: {r['act_structure']}\n    线索策略: {r['clue_distribution']}\n"
    return result


def query_plots(pattern_type: str = None, limit: int = 10) -> str:
    conn = _connect()
    cursor = conn.cursor()
    sql = "SELECT id, name, pattern_type, required_roles, twist_points FROM plot_patterns WHERE 1=1"
    params = []
    if pattern_type:
        sql += " AND pattern_type = ?"
        params.append(pattern_type)
    sql += f" LIMIT {limit}"
    cursor.execute(sql, params)
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        return "未找到匹配的剧情模式"
    result = "剧情模式列表：\n"
    for r in rows:
        result += f"  [{r['pattern_type']}] {r['name']} — 所需角色: {r['required_roles']}\n    反转节点: {r['twist_points']}\n"
    return result


# ---------- @tool 包装（带进度计数）----------

@tool
def search_character_archetypes(era: str = "", role_type: str = "") -> str:
    """从角色原型库中查询可用的角色原型。可筛选时代（era: 民国/现代/古代）和角色类型（role_type: 凶手/侦探/嫌疑人/帮凶）"""
    c = _next_count(get_thread_context() or "unknown")
    monitor.report_tool(f"角色原型查询 ({c}/{TOTAL_DB_TOOLS})", {"era": era, "role_type": role_type})
    return query_characters(era=era or None, role_type=role_type or None)


@tool
def search_trick_patterns(category: str = "", difficulty: int = 0) -> str:
    """从诡计模式库中查询推理诡计。可筛选分类(category: 密室/不在场证明/身份诡计/毒杀/心理诡计)和最大难度(difficulty: 1-5)"""
    c = _next_count(get_thread_context() or "unknown")
    monitor.report_tool(f"诡计模式查询 ({c}/{TOTAL_DB_TOOLS})", {"category": category, "difficulty": difficulty})
    return query_tricks(category=category or None, difficulty=difficulty if difficulty > 0 else None)


@tool
def search_script_templates(template_type: str = "", player_count: int = 0) -> str:
    """从剧本模板库中查询剧本结构模板。可筛选类型(template_type: 本格/变格/阵营/情感/恐怖)和人数(player_count)"""
    c = _next_count(get_thread_context() or "unknown")
    monitor.report_tool(f"剧本模板查询 ({c}/{TOTAL_DB_TOOLS})", {"template_type": template_type, "player_count": player_count})
    return query_templates(template_type=template_type or None, player_count=player_count if player_count > 0 else None)


@tool
def search_plot_patterns(pattern_type: str = "") -> str:
    """从剧情模式库中查询剧情框架。可筛选类型(pattern_type: 封闭空间/连续杀人/遗嘱争夺/身份互换/复仇/心理操纵)"""
    c = _next_count(get_thread_context() or "unknown")
    monitor.report_tool(f"剧情模式查询 ({c}/{TOTAL_DB_TOOLS})", {"pattern_type": pattern_type})
    return query_plots(pattern_type=pattern_type or None)
