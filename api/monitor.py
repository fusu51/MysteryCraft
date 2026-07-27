import datetime
import json
import asyncio
from pathlib import Path
from typing import Any, Dict, Optional
from fastapi import WebSocket
from api.context import get_thread_context, get_session_context

# 尝试导入全局运行时（用于脚本模式下的流式输出）
try:
    import builtins
except ImportError:
    builtins = None


class ToolMonitor:
    """
    工具监控类，负责三件事：
    1. WebSocket 实时推送到前端
    2. 结构化日志（调用 trace.py）
    3. 会话 trace.jsonl 落盘
    """
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ToolMonitor, cls).__new__(cls)
            cls._instance.websocket_manager = None
        return cls._instance

    def set_websocket_manager(self, manager):
        self.websocket_manager = manager

    # ===== 内部方法 =====

    def _ws_send(self, payload: dict) -> bool:
        """WebSocket 推送，成功返回 True"""
        if not self.websocket_manager:
            return False

        try:
            thread_id = get_thread_context()
            if not thread_id:
                return False

            manager_loop = self.websocket_manager.loop
            if not manager_loop:
                return False

            try:
                current_loop = asyncio.get_running_loop()
                same_loop = (manager_loop == current_loop)
            except RuntimeError:
                same_loop = False

            if same_loop:
                current_loop.create_task(
                    self.websocket_manager.send_to_thread(payload, thread_id)
                )
            else:
                asyncio.run_coroutine_threadsafe(
                    self.websocket_manager.send_to_thread(payload, thread_id),
                    manager_loop,
                )
            return True
        except Exception:
            return False

    def _write_trace(self, payload: dict) -> None:
        """将会话事件追加到 output/session_{id}/trace.jsonl"""
        try:
            session_dir = get_session_context()
            if not session_dir:
                return
            log_file = Path(session_dir) / "trace.jsonl"
            log_file.parent.mkdir(parents=True, exist_ok=True)
            with open(log_file, "a", encoding="utf-8") as f:
                f.write(json.dumps(payload, ensure_ascii=False) + "\n")
        except Exception:
            pass

    def _emit(self, event_type: str, message: str, data: Optional[Dict[str, Any]] = None):
        """核心发布：WebSocket + trace 落盘 + trace 日志"""
        if data is None:
            data = {}

        payload = {
            "type": "monitor_event",
            "event": event_type,
            "message": message,
            "data": data,
            "timestamp": datetime.datetime.now().isoformat(),
        }

        # 1. WebSocket → 前端
        self._ws_send(payload)

        # 2. runtime → deepagents 脚本模式（不动原有逻辑）
        if builtins and hasattr(builtins, "runtime") and hasattr(builtins.runtime, "stream_writer"):
            try:
                builtins.runtime.stream_writer(payload)
            except Exception:
                pass

        # 3. trace.jsonl → 文件持久化
        self._write_trace(payload)

    # ===== 公开 API（工具层调用）=====

    def report_tool(self, tool_name: str, args: Dict[str, Any] = None):
        self._emit("tool_start", f"开始执行工具: {tool_name}",
                   {"tool_name": tool_name, "args": args or {}})

    def report_assistant(self, assistant_name: str, args: Dict[str, Any] = None):
        self._emit("assistant_call", f"正在调用助手: {assistant_name}",
                   {"assistant_name": assistant_name, "args": args or {}})

    def report_task_result(self, result: str):
        self._emit("task_result", "任务执行完成", {"result": result[:500]})

    def report_session_dir(self, path: str):
        self._emit("session_created", f"工作目录已创建: {path}", {"path": path})


# 全局单例
monitor = ToolMonitor()


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.loop = None

    def set_loop(self, loop):
        self.loop = loop
        monitor.set_websocket_manager(self)

    async def connect(self, websocket: WebSocket, thread_id: str):
        await websocket.accept()
        self.active_connections[thread_id] = websocket

    def disconnect(self, websocket: WebSocket, thread_id: str):
        if thread_id in self.active_connections:
            del self.active_connections[thread_id]

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def send_to_thread(self, message: dict, thread_id: str):
        if thread_id in self.active_connections:
            websocket = self.active_connections[thread_id]
            await websocket.send_json(message)


manager = ConnectionManager()
