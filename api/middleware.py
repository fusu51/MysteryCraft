"""FastAPI 中间件 — 请求计时 + trace_id 注入"""
import time
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from api.context import get_thread_context
from api.trace import log_event


class TraceMiddleware(BaseHTTPMiddleware):
    """每个 HTTP 请求自动记录耗时和状态码"""

    async def dispatch(self, request: Request, call_next):
        _t0 = time.perf_counter()

        response = await call_next(request)

        dt = time.perf_counter() - _t0
        trace_id = get_thread_context() or "unknown"

        # 非 API 请求（静态文件）跳过
        if request.url.path.startswith("/api/"):
            log_event(
                trace_id,
                "HTTP",
                f"{request.method} {request.url.path} {response.status_code}",
                detail={
                    "method": request.method,
                    "path": request.url.path,
                    "status": response.status_code,
                    "duration": round(dt, 3),
                },
            )

        return response
