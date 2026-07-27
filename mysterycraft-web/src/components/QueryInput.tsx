interface Props {
    value: string;
    onChange: (val: string) => void;
    disabled: boolean;
}

export default function QueryInput({ value, onChange, disabled }: Props) {
    return (
        <div className="space-y-2">
            <h3 className="text-sm font-medium text-gray-400">自由描述</h3>
            <textarea
                value={value}
                onChange={(e) => onChange(e.target.value)}
                disabled={disabled}
                placeholder="描述你想要的剧本，例如：写一个民国探案本，6人，核心诡计用密室+不在场证明双重设计..."
                rows={5}
                className="w-full px-4 py-3 rounded-xl border border-gray-700 bg-gray-800/50
                   text-gray-100 placeholder-gray-500 resize-none
                   focus:outline-none focus:ring-2 focus:ring-purple-500/50 focus:border-purple-500
                   disabled:opacity-50 disabled:cursor-not-allowed
                   transition-colors"
            />
            <p className="text-xs text-gray-500 text-right">
                {value.length} 字
            </p>
        </div>
    );
}
