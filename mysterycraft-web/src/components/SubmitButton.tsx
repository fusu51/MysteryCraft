interface Props {
    disabled: boolean;
    loading: boolean;
    onSubmit: () => void;
}

export default function SubmitButton({ disabled, loading, onSubmit }: Props) {
    return (
        <button
            onClick={onSubmit}
            disabled={disabled || loading}
            className="w-full py-3 rounded-xl font-semibold text-lg
                 bg-purple-600 text-white
                 hover:bg-purple-500 active:bg-purple-700
                 disabled:bg-gray-700 disabled:text-gray-500 disabled:cursor-not-allowed
                 transition-all duration-200
                 flex items-center justify-center gap-2"
        >
            {loading ? (
                <>
                    <svg className="animate-spin h-5 w-5" viewBox="0 0 24 24">
                        <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                        <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" />
                    </svg>
                    创作中...
                </>
            ) : (
                "开始创作"
            )}
        </button>
    );
}
