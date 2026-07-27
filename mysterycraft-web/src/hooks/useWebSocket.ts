import { useEffect, useRef } from "react";
import type { MonitorEvent } from "../types";
import { useDispatch } from "../context/AppContext";
import { fetchFiles, getSessionPath } from "../services/api";

export function useWebSocket(threadId: string | null) {
    const dispatch = useDispatch();
    const wsRef = useRef<WebSocket | null>(null);

    useEffect(() => {
        if (!threadId) return;

        dispatch({ type: "SET_CONNECTION_STATUS", status: "connecting" });

        const protocol = location.protocol === "https:" ? "wss:" : "ws:";
        const wsUrl = `${protocol}//${location.host}/ws/${threadId}`;
        const ws = new WebSocket(wsUrl);
        wsRef.current = ws;

        ws.onopen = () => {
            dispatch({ type: "SET_CONNECTION_STATUS", status: "connected" });
        };

        ws.onmessage = (e) => {
            try {
                const data = JSON.parse(e.data);
                if (data.type === "monitor_event") {
                    dispatch({ type: "ADD_EVENT", event: data as MonitorEvent });

                    // 检测任务完成
                    if (data.event === "task_result") {
                        dispatch({ type: "SET_LOADING", isLoading: false });
                        // 通过 threadId 拿到 session_dir，然后拉文件列表
                        getSessionPath(threadId).then((dir) => {
                            if (dir) {
                                dispatch({ type: "SET_SESSION_DIR", dir });
                                fetchFiles(dir).then((files) => {
                                    dispatch({ type: "SET_FILES", files });
                                });
                            }
                        });
                    }
                    // 捕获 session_dir
                    if (data.event === "session_created" && data.data?.path) {
                        dispatch({ type: "SET_SESSION_DIR", dir: data.data.path as string });
                    }
                }
            } catch {
                // 心跳 pong 等非 JSON 消息忽略
            }
        };

        ws.onerror = () => {
            dispatch({ type: "SET_CONNECTION_STATUS", status: "disconnected" });
        };

        ws.onclose = () => {
            dispatch({ type: "SET_CONNECTION_STATUS", status: "disconnected" });
        };

        return () => {
            ws.close();
            wsRef.current = null;
        };
    }, [threadId, dispatch]);

    return wsRef;
}
