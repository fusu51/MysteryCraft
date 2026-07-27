import type { TaskResponse, FileListResponse, FileItem } from "../types";

const BASE = "";  // Vite proxy 自动转发 /api → localhost:8000

export async function submitTask(query: string, threadId?: string): Promise<TaskResponse> {
    const res = await fetch(`${BASE}/api/task`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ query, thread_id: threadId }),
    });
    if (!res.ok) throw new Error(`提交任务失败: ${res.status}`);
    return res.json();
}

export async function fetchFiles(sessionPath: string): Promise<FileItem[]> {
    const res = await fetch(`${BASE}/api/files?path=${encodeURIComponent(sessionPath)}`);
    if (!res.ok) throw new Error(`获取文件列表失败: ${res.status}`);
    const data: FileListResponse = await res.json();
    return data.files || [];
}

export function getDownloadUrl(filePath: string): string {
    return `${BASE}/api/download?path=${encodeURIComponent(filePath)}`;
}

export async function getSessionPath(threadId: string): Promise<string | null> {
    const res = await fetch(`${BASE}/api/session-path/${threadId}`);
    if (!res.ok) return null;
    const data = await res.json();
    return data.path || null;
}
