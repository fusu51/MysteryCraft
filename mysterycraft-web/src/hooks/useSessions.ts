import { useEffect } from "react";
import type { SessionRecord } from "../types";
import { useAppState, useDispatch } from "../context/AppContext";
import { getSessionPath, fetchFiles } from "../services/api";

const STORAGE_KEY = "mysterycraft_sessions";

function loadSessions(): SessionRecord[] {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch {
        return [];
    }
}

function saveSessions(sessions: SessionRecord[]) {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions.slice(0, 20)));
}

export function useSessions() {
    const { sessions, activeSession } = useAppState();
    const dispatch = useDispatch();

    useEffect(() => {
        dispatch({ type: "SET_SESSIONS", sessions: loadSessions() });
    }, [dispatch]);

    function addSession(record: SessionRecord) {
        const updated = [record, ...sessions.filter(s => s.thread_id !== record.thread_id)].slice(0, 20);
        saveSessions(updated);
        dispatch({ type: "SET_SESSIONS", sessions: updated });
    }

    async function switchSession(threadId: string) {
        dispatch({ type: "SET_ACTIVE_SESSION", threadId });
        dispatch({ type: "CLEAR_EVENTS" });
        dispatch({ type: "SET_FILES", files: [] });

        // 通过 threadId 获取 session_dir 并拉文件列表
        const dir = await getSessionPath(threadId);
        if (dir) {
            dispatch({ type: "SET_SESSION_DIR", dir });
            const files = await fetchFiles(dir);
            dispatch({ type: "SET_FILES", files });
        }
    }

    function clearSessions() {
        localStorage.removeItem(STORAGE_KEY);
        dispatch({ type: "SET_SESSIONS", sessions: [] });
    }

    return { sessions, activeSession, addSession, switchSession, clearSessions };
}
