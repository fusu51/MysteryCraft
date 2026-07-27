import { useState } from "react";
import type { FileItem } from "../types";
import { getDownloadUrl, convertToPdf } from "../services/api";

function formatSize(bytes: number): string {
    if (bytes < 1024) return `${bytes} B`;
    if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
    return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

const ICON_MAP: Record<string, string> = {
    "DM_": "📋",
    "角色_": "👤",
    "线索卡": "🃏",
    "案件时间线": "⏰",
};

function getIcon(name: string): string {
    for (const [key, icon] of Object.entries(ICON_MAP)) {
        if (name.includes(key)) return icon;
    }
    return "📄";
}

interface Props {
    file: FileItem;
}

export default function FileItemRow({ file }: Props) {
    const [converting, setConverting] = useState(false);

    async function handleConvert() {
        setConverting(true);
        try {
            const res = await convertToPdf(file.path);
            if (res.status === "ok") {
                alert("PDF 已生成，刷新文件列表即可看到");
            } else {
                alert(res.message || "转换失败");
            }
        } catch {
            alert("转换请求失败");
        } finally {
            setConverting(false);
        }
    }

    return (
        <div className="flex items-center justify-between py-2.5 px-3 rounded-lg
                    bg-gray-800/30 hover:bg-gray-800/50 transition-colors group">
            <div className="flex items-center gap-3 min-w-0">
                <span className="text-lg">{getIcon(file.name)}</span>
                <div className="min-w-0">
                    <p className="text-sm text-gray-200 truncate">{file.name}</p>
                    <p className="text-xs text-gray-600">{formatSize(file.size)}</p>
                </div>
            </div>
            <div className="flex items-center gap-1">
                {file.name.endsWith(".md") && (
                    <button
                        onClick={handleConvert}
                        disabled={converting}
                        className="px-3 py-1.5 text-xs rounded-lg bg-blue-600/20 text-blue-400
                                   hover:bg-blue-600/40 opacity-0 group-hover:opacity-100
                                   transition-all duration-200 flex-shrink-0 disabled:opacity-50"
                    >
                        {converting ? "转换中" : "转PDF"}
                    </button>
                )}
                <a
                    href={getDownloadUrl(file.path)}
                    download={file.name}
                    className="px-3 py-1.5 text-xs rounded-lg bg-purple-600/20 text-purple-400
                       hover:bg-purple-600/40 opacity-0 group-hover:opacity-100
                       transition-all duration-200 flex-shrink-0"
                >
                    下载
                </a>
            </div>
        </div>
    );
}
