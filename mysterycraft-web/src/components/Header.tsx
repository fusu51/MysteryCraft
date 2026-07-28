import { useState } from "react";
import ConnectionStatus from "./ConnectionStatus";
import type { ConnectionStatus as Status } from "../types";

interface Props {
    status: Status;
    hasTask: boolean;
}

export default function Header({ status, hasTask }: Props) {
    const [showSettings, setShowSettings] = useState(false);
    const [token, setToken] = useState(localStorage.getItem("mysterycraft_token") || "");

    function saveToken() {
        if (token.trim()) {
            localStorage.setItem("mysterycraft_token", token.trim());
        } else {
            localStorage.removeItem("mysterycraft_token");
        }
        setShowSettings(false);
    }

    return (
        <header className="border-b border-gray-800 px-6 py-4">
            <div className="max-w-6xl mx-auto flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <span className="text-2xl">🎭</span>
                    <h1 className="text-xl font-bold text-purple-400">MysteryCraft</h1>
                    <span className="text-xs text-gray-500 bg-gray-800 px-2 py-0.5 rounded">剧本杀 DM 创作助手</span>
                </div>

                <div className="flex items-center gap-3">
                    <ConnectionStatus status={status} hasTask={hasTask} />

                    {/* 设置按钮 */}
                    <button
                        onClick={() => setShowSettings(!showSettings)}
                        className="text-gray-500 hover:text-gray-300 text-sm"
                        title="设置"
                    >
                        ⚙️
                    </button>
                </div>
            </div>

            {/* 设置面板 */}
            {showSettings && (
                <div className="max-w-6xl mx-auto mt-3 p-3 bg-gray-800/50 rounded-lg border border-gray-700">
                    <label className="text-xs text-gray-400 block mb-1">访问令牌（Access Token）</label>
                    <div className="flex gap-2">
                        <input
                            type="password"
                            value={token}
                            onChange={(e) => setToken(e.target.value)}
                            placeholder="如未启用认证可不填"
                            className="flex-1 px-3 py-1.5 text-sm rounded-lg border border-gray-600 bg-gray-900
                         text-gray-200 placeholder-gray-600 focus:outline-none focus:ring-1 focus:ring-purple-500"
                        />
                        <button
                            onClick={saveToken}
                            className="px-4 py-1.5 text-sm rounded-lg bg-purple-600 text-white hover:bg-purple-500"
                        >
                            保存
                        </button>
                    </div>
                </div>
            )}
        </header>
    );
}
