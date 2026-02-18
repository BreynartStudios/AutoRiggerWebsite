import { useModelStore } from '../../stores/useModelStore';

const STAGE_LABELS = {
  upload: 'Upload Model',
  markers: 'Place Markers',
  rigging: 'Processing...',
  animations: 'Animations',
  export: 'Export',
};

export default function Header() {
  const { stage, reset } = useModelStore();

  return (
    <header className="h-14 bg-gray-900 border-b border-gray-700 flex items-center px-4 shrink-0">
      <button
        onClick={reset}
        className="flex items-center gap-2 hover:opacity-80 transition-opacity"
      >
        <div className="w-8 h-8 rounded-lg bg-sky-500 flex items-center justify-center font-bold text-white text-sm">
          OR
        </div>
        <h1 className="text-lg font-semibold text-white">OpenRig</h1>
      </button>

      <div className="ml-8 flex items-center gap-1">
        {(Object.keys(STAGE_LABELS) as Array<keyof typeof STAGE_LABELS>).map((key, i) => (
          <div key={key} className="flex items-center">
            {i > 0 && <div className="w-6 h-px bg-gray-600 mx-1" />}
            <span
              className={`text-xs px-2 py-1 rounded ${
                stage === key
                  ? 'bg-sky-500/20 text-sky-400 font-medium'
                  : 'text-gray-500'
              }`}
            >
              {STAGE_LABELS[key]}
            </span>
          </div>
        ))}
      </div>

      <div className="ml-auto flex items-center gap-3">
        <a
          href="https://github.com"
          target="_blank"
          rel="noopener noreferrer"
          className="text-gray-400 hover:text-white text-sm transition-colors"
        >
          GitHub
        </a>
      </div>
    </header>
  );
}
