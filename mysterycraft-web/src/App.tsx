import { useState, useCallback } from "react";
import { submitTask } from "./services/api";
import { useWebSocket } from "./hooks/useWebSocket";
import { useSessions } from "./hooks/useSessions";
import { useAppState, useDispatch } from "./context/AppContext";
import TemplateSelector from "./components/TemplateSelector";
import QueryInput from "./components/QueryInput";
import SubmitButton from "./components/SubmitButton";
import ConnectionStatus from "./components/ConnectionStatus";
import ProgressPanel from "./components/ProgressPanel";
import FileList from "./components/FileList";
import SessionHistory from "./components/SessionHistory";


export default function App() {
  const [query, setQuery] = useState("");
  const { threadId, isLoading, connectionStatus, events } = useAppState();
  const dispatch = useDispatch();
  const { addSession } = useSessions();

  // WebSocket 连接
  useWebSocket(threadId);

  const handleSubmit = useCallback(async () => {
    const q = query.trim();
    if (!q) return;

    dispatch({ type: "RESET_PANEL" });
    dispatch({ type: "SET_LOADING", isLoading: true });

    try {
      const res = await submitTask(q);

      // 服务器繁忙或校验失败
      if (res.status === "busy" || res.status === "error") {
        alert(res.message || "请求失败，请稍后重试");
        dispatch({ type: "SET_LOADING", isLoading: false });
        return;
      }

      dispatch({ type: "SET_THREAD", threadId: res.thread_id });
      addSession({
        thread_id: res.thread_id,
        query: q,
        created_at: new Date().toISOString(),
        session_dir: "",
      });
    } catch (e) {
      alert("网络连接失败，请检查后端服务是否启动");
      dispatch({ type: "SET_LOADING", isLoading: false });
    }
  }, [query, dispatch, addSession]);

  const handleTemplateSelect = useCallback((q: string) => {
    setQuery(q);
  }, []);

  return (
      <div className="min-h-screen bg-gray-950 text-gray-100">
        {/* Header */}
        <header className="border-b border-gray-800 px-6 py-4">
          <div className="max-w-6xl mx-auto flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-2xl">🎭</span>
              <h1 className="text-xl font-bold text-purple-400">MysteryCraft</h1>
              <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded">剧本杀 DM 创作助手</span>
            </div>
            <div className="flex items-center gap-2">
              <ConnectionStatus status={connectionStatus} hasTask={!!threadId} />
            </div>
          </div>
        </header>

        {/* Main */}
        <main className="max-w-6xl mx-auto p-6">
          <div className="grid grid-cols-2 gap-6">
            {/* Left Panel */}
            <div className="space-y-4">
              <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-5 space-y-4">
                <TemplateSelector onSelect={handleTemplateSelect} disabled={isLoading} />
                <QueryInput value={query} onChange={setQuery} disabled={isLoading} />
                <SubmitButton disabled={!query.trim()} loading={isLoading} onSubmit={handleSubmit} />
              </div>
            </div>

            {/* Right Panel */}
            <div className="bg-gray-900/50 border border-gray-800 rounded-2xl p-5 space-y-6">
              <div>
                <h3 className="text-sm font-medium text-gray-400 mb-3">📡 实时进度</h3>
                <ProgressPanel events={events} />
              </div>
              <hr className="border-gray-800" />
              <FileList />
            </div>
          </div>
        </main>

        <SessionHistory />
      </div>
  );
}
