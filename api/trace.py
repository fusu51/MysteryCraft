"""结构化日志 + span 计时 + trace_id 透传"""
import logging
import time
import json
import functools
from contextlib import contextmanager
from typing import Optional
from api.log_config import get_logger

logger = get_logger("mysterycraft")

# ===== 终端颜色 =====
C = {
    "TOOL":  "\033[33m",   # 黄
    "AGENT": "\033[35m",   # 紫
    "TASK":  "\033[36m",   # 青
    "ERROR": "\033[31m",   # 红
    "OK":    "\033[32m",   # 绿
    "DIM":   "\033[90m",   # 灰
    "RST":   "\033[0m",
}


def _fmt_ts() -> str:
    return time.strftime("%H:%M:%S")


def _short_id(trace_id: str) -> str:
    return trace_id[:8] if trace_id else "--------"


# ===== 对外 API =====

def log_event(
        trace_id: str,
        category: str,         # TOOL / AGENT / TASK / ERROR
        message: str,
        detail: Optional[dict] = None,
        level: str = "INFO",
):
    """记录一条结构化日志，同时输出终端(彩色)和文件(JSON)"""
    ts = _fmt_ts()
    tid = _short_id(trace_id)
    color = C.get(category, "")

    # 终端
    line = f"[{ts}] {color}{tid} │ {category:<5}{C['RST']} │ {message}"
    if level == "ERROR":
        logger.error(line)
    elif level == "WARNING":
        logger.warning(line)
    else:
        logger.info(line)

    # 文件 (logger.info 会同时写到 RotatingFileHandler)
    # 用 extra 把结构化字段挂上
    extra = {
        "ts": ts,
        "trace": trace_id,
        "category": category,
        "message": message,
        "detail": detail or {},
    }
    # 复用同一个 logger，但 handler 配置的 formatter 是 %(message)s，
    # 所以文件里我们直接写 JSON 字符串
    file_record = json.dumps(extra, ensure_ascii=False)
    # 获取 mysterycraft logger 对应的 file handler
    root = logging.getLogger("mysterycraft")
    for h in root.handlers:
        if hasattr(h, "baseFilename"):  # RotatingFileHandler
            h.handle(logging.LogRecord(
                name="mysterycraft",
                level=getattr(logging, level),
                pathname="", lineno=0,
                msg=file_record, args=(),
                exc_info=None
            ))


@contextmanager
def log_span(trace_id: str, category: str, action: str, **meta):
    """上下文管理器：自动计时，输出开始/结束两条日志"""
    _t0 = time.perf_counter()
    log_event(trace_id, category, f"{action} 开始", detail=meta)

    try:
        yield
        dt = time.perf_counter() - _t0
        log_event(trace_id, category, f"{action} 完成", detail={**meta, "duration": round(dt, 2)})
    except Exception as e:
        dt = time.perf_counter() - _t0
        log_event(trace_id, "ERROR", f"{action} 失败: {e}", detail={**meta, "duration": round(dt, 2)}, level="ERROR")
        raise


def log_tool_start(trace_id: str, tool_name: str, args: dict):
    log_event(trace_id, "TOOL", f"{tool_name}", detail={"args": args})


def log_tool_end(trace_id: str, tool_name: str, duration: float, result_len: int):
    log_event(trace_id, "TOOL", f"{tool_name} 完成", detail={"duration": round(duration, 2), "result_chars": result_len})


def log_agent_call(trace_id: str, agent_name: str, description_len: int):
    log_event(trace_id, "AGENT", f"{agent_name} 调用", detail={"desc_len": description_len})


def log_agent_return(trace_id: str, agent_name: str, duration: float, result_len: int):
    log_event(trace_id, "AGENT", f"{agent_name} 返回", detail={"duration": round(duration, 2), "result_chars": result_len})


def log_task_done(trace_id: str, total_sec: float, file_count: int):
    m, s = divmod(int(total_sec), 60)
    log_event(trace_id, "TASK", f"任务完成 ({m}m{s}s, {file_count} 个文件)")
