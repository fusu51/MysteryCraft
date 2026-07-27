import { useEffect, useRef } from "react";
import type { MonitorEvent } from "../types";
import ProgressItem from "./ProgressItem";

interface Props {
    events: MonitorEvent[];
}

export default function ProgressPanel({ events }: Props) {
    const bottomRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
    }, [events.length]);

    if (events.length === 0) {
        return (
            <div className="text-center text-gray-500 py-12">
                <p className="text-lg mb-2">📡</p>
                <p className="text-sm">等待创作任务...</p>
            </div>
        );
    }

    return (
        <div className="max-h-80 overflow-y-auto space-y-1 pr-1">
            {events.map((ev, i) => (
                <ProgressItem key={i} event={ev} />
            ))}
            <div ref={bottomRef} />
        </div>
    );
}
