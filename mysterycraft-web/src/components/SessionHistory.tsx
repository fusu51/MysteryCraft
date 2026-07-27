import { useSessions } from "../hooks/useSessions";
import type { SessionRecord } from "../types";

function formatDate(iso: string): string {
    const d = new Date(iso);
    const now = new Date();
    const diff = now.getTime() - d.getTime();
    if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`;
    return d.toLocaleDateString("zh-CN");
}

function truncate(str: string, max: number): string {
    return str.length > max ? str.slice(0, max) + "..." : str;
}

export default function SessionHistory() {
    const { sessions, activeSession, switchSession, clearSessions } = useSessions();

    if (sessions.length === 0) return null;

    return (
        <div className="border-t border-gray-800 px-6 py-3">
            <div className="max-w-6xl mx-auto">
                <div className="flex items-center justify-between mb-2">
                    <h3 className="text-xs font-medium text-gray-500">历史创作</h3>
                    <button
                        onClick={clearSessions}
                        className="text-xs text-gray-600 hover:text-red-400 transition-colors"
                    >
                        清空
                    </button>
                </div>
                <div className="flex gap-2 overflow-x-auto pb-1">
                    {sessions.map((s: SessionRecord) => (
                        <button
                            key={s.thread_id}
                            onClick={() => switchSession(s.thread_id)}
                            className={`flex-shrink-0 px-3 py-1.5 rounded-lg text-xs text-left
                          transition-colors max-w-[240px]
                          ${activeSession === s.thread_id
                                ? "bg-purple-600/30 border border-purple-500/50 text-purple-300"
                                : "bg-gray-800/50 border border-gray-700/50 text-gray-400 hover:bg-gray-800"
                            }`}
                        >
                            <p className="truncate font-medium">{truncate(s.query, 30)}</p>
                            <p className="text-gray-600 mt-0.5">{formatDate(s.created_at)}</p>
                        </button>
                    ))}
                </div>
            </div>
        </div>
    );
}
