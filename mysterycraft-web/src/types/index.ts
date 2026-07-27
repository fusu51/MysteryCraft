// ====== 后端 API 响应类型 ======

export interface TaskResponse {
    status: "started";
    thread_id: string;
}

// ====== WebSocket 推送事件 ======

export type MonitorEventType =
    | "tool_start"
    | "assistant_call"
    | "task_result"
    | "session_created"
    | "error";

export interface MonitorEvent {
    type: "monitor_event";
    event: MonitorEventType;
    message: string;
    data: Record<string, unknown>;
    timestamp: string;
}

// ====== 文件列表 ======

export interface FileItem {
    name: string;
    type: "file";
    path: string;
    size: number;
    mtime: number;
}

export interface FileListResponse {
    files: FileItem[];
}

// ====== 会话记录（存 localStorage） ======

export interface SessionRecord {
    thread_id: string;
    query: string;
    created_at: string;
    session_dir: string;
}

// ====== 应用状态 ======

export type ConnectionStatus = "disconnected" | "connecting" | "connected";

export interface AppState {
    threadId: string | null;
    sessionDir: string | null;
    connectionStatus: ConnectionStatus;
    events: MonitorEvent[];
    isLoading: boolean;
    files: FileItem[];
    sessions: SessionRecord[];
    activeSession: string | null; // thread_id
}
