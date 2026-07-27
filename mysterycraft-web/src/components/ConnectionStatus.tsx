import type { ConnectionStatus as Status } from "../types";

const STATUS_MAP: Record<Status | "idle", { dot: string; label: string }> = {
    idle:          { dot: "bg-gray-500", label: "等待任务" },
    connected:     { dot: "bg-green-400", label: "已连接" },
    connecting:    { dot: "bg-yellow-400 animate-pulse", label: "连接中" },
    disconnected:  { dot: "bg-red-500", label: "已断开" },
};

interface Props {
    status: Status;
    hasTask: boolean;
}

export default function ConnectionStatus({ status, hasTask }: Props) {
    const key = hasTask ? status : "idle";
    const s = STATUS_MAP[key];
    return (
        <div className="flex items-center gap-2">
            <span className={`h-2 w-2 rounded-full ${s.dot}`} />
            <span className="text-xs text-gray-500">{s.label}</span>
        </div>
    );
}
