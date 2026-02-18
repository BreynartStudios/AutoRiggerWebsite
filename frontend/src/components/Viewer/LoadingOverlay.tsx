import { useModelStore } from '../../stores/useModelStore';

export default function LoadingOverlay() {
  const { status } = useModelStore();

  return (
    <div className="absolute inset-0 z-10 flex items-center justify-center bg-gray-950/80 backdrop-blur-sm">
      <div className="bg-gray-900 rounded-xl p-6 shadow-2xl border border-gray-700 max-w-xs w-full mx-4">
        <div className="flex items-center gap-3 mb-4">
          <div className="w-5 h-5 border-2 border-sky-400 border-t-transparent rounded-full animate-spin" />
          <span className="text-white font-medium">Processing</span>
        </div>
        {status && (
          <>
            <p className="text-sm text-gray-300 mb-3">{status.message}</p>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-sky-500 h-2 rounded-full transition-all duration-500"
                style={{ width: `${status.progress}%` }}
              />
            </div>
            <p className="text-xs text-gray-500 mt-2 text-right">
              {status.progress}%
            </p>
          </>
        )}
      </div>
    </div>
  );
}
