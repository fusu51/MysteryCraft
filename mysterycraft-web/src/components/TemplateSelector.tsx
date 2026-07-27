import { TEMPLATES } from "../constants/templates";

interface Props {
    onSelect: (query: string) => void;
    disabled: boolean;
}

export default function TemplateSelector({ onSelect, disabled }: Props) {
    return (
        <div className="space-y-2">
            <h3 className="text-sm font-medium text-gray-400">预设模板</h3>
            <div className="flex flex-wrap gap-2">
                {TEMPLATES.map((t) => (
                    <button
                        key={t.label}
                        onClick={() => onSelect(t.query)}
                        disabled={disabled}
                        className="px-3 py-1.5 text-sm rounded-lg border border-gray-700
                       bg-gray-800/50 text-gray-300 hover:bg-purple-600/20
                       hover:border-purple-500/50 hover:text-purple-300
                       disabled:opacity-50 disabled:cursor-not-allowed
                       transition-colors"
                    >
                        {t.label}
                    </button>
                ))}
            </div>
        </div>
    );
}
