import type { MonitorEvent } from "../types";

const EVENT_STYLE: Record<string, { icon: string; color: string }> = {
    session_created: { icon: "📁", color: "text-blue-400" },
    tool_start:      { icon: "🔧", color: "text-yellow-400" },
    assistant_call:  { icon: "🤖", color: "text-purple-400" },
    task_result:     { icon: "✅", color: "text-green-400" },
    error:           { icon: "❌", color: "text-red-400" },
};

function formatTime(iso: string): string {
    const d = new Date(iso);
    return d.toLocaleTimeString("zh-CN", { hour: "2-digit", minute: "2-digit", second: "2-digit" });
}

function getToolName(event: MonitorEvent): string {
    if (event.data?.tool_name) return event.data.tool_name as string;
    if (event.data?.assistant_name) return event.data.assistant_name as string;
    return "";
}

interface Props {
    event: MonitorEvent;
}

export default function ProgressItem({ event }: Props) {
    const style = EVENT_STYLE[event.event] || { icon: "📌", color: "text-gray-400" };
    const toolName = getToolName(event);
    const message = toolName || event.message;

    return (
        <div className="flex items-start gap-3 py-2 border-b border-gray-800/50 last:border-0">
            <span className="text-sm mt-0.5">{style.icon}</span>
            <div className="flex-1 min-w-0">
                <p className={`text-sm ${style.color} truncate`}>{message}</p>
                {event.message !== message && (
                    <p className="text-xs text-gray-500 truncate mt-0.5">{event.message}</p>
                )}
            </div>
            <span className="text-xs text-gray-600 whitespace-nowrap">
        {formatTime(event.timestamp)}
      </span>
        </div>
    );
}
