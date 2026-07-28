import type { TaskResponse, FileListResponse, FileItem } from "../types";

const BASE = "";  // Vite proxy 自动转发 /api → localhost:8000

function getAuthHeader(): Record<string, string> {
    const token = localStorage.getItem("mysterycraft_token");
    return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function submitTask(query: string, threadId?: string): Promise<TaskResponse> {
    const res = await fetch(`${BASE}/api/task`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            ...getAuthHeader(),
        },
        body: JSON.stringify({ query, thread_id: threadId }),
    });

    // 401 认证失败 → 弹出提示
    if (res.status === 401) {
        alert("🔒 需要访问令牌\n\n为控制 API 成本，请联系 WX：19267826845 获取令牌。\n\n获取后在页面右上角 ⚙️ 设置中填入即可使用。");
        throw new Error("NEED_AUTH");
    }

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

export async function convertToPdf(filePath: string): Promise<{status: string; pdf_path?: string; message?: string}> {
    const res = await fetch(`${BASE}/api/convert-pdf?path=${encodeURIComponent(filePath)}`, {
        method: "POST",
    });
    return res.json();
}

