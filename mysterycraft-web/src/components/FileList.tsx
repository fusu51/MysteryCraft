import { useEffect } from "react";
import { fetchFiles } from "../services/api";
import { useAppState, useDispatch } from "../context/AppContext";
import FileItemRow from "./FileItemRow";

export default function FileList() {
    const { sessionDir, files } = useAppState();
    const dispatch = useDispatch();

    useEffect(() => {
        if (!sessionDir) return;
        fetchFiles(sessionDir)
            .then((f) => dispatch({ type: "SET_FILES", files: f }))
            .catch(console.error);
    }, [sessionDir, dispatch]);

    if (!sessionDir) return null;

    return (
        <div>
            <h3 className="text-sm font-medium text-gray-400 mb-3">
                📁 生成文件 {files.length > 0 && `(${files.length})`}
            </h3>
            {files.length === 0 ? (
                <p className="text-xs text-gray-600 text-center py-6">生成中，文件将在这里显示...</p>
            ) : (
                <div className="space-y-1">
                    {files.map((f) => (
                        <FileItemRow key={f.path} file={f} />
                    ))}
                </div>
            )}
        </div>
    );
}
