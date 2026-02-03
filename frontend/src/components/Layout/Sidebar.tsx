import { useModelStore } from '../../stores/useModelStore';
import UploadPanel from '../Upload/UploadPanel';
import MarkerPanel from '../MarkerEditor/MarkerPanel';
import AnimationLibrary from '../Animation/AnimationLibrary';
import MyAnimationsList from '../Animation/MyAnimationsList';
import ExportPanel from '../Export/ExportPanel';

export default function Sidebar() {
  const { stage } = useModelStore();

  return (
    <aside className="w-80 bg-gray-900 border-r border-gray-700 flex flex-col overflow-hidden shrink-0">
      <div className="flex-1 overflow-y-auto p-4 space-y-4">
        {stage === 'upload' && <UploadPanel />}
        {stage === 'markers' && <MarkerPanel />}
        {stage === 'rigging' && <RiggingProgress />}
        {(stage === 'animations' || stage === 'export') && (
          <>
            <AnimationLibrary />
            <MyAnimationsList />
            <ExportPanel />
          </>
        )}
      </div>
    </aside>
  );
}

function RiggingProgress() {
  const { status } = useModelStore();
  const progress = status?.progress ?? 0;

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
        Auto-Rigging
      </h2>
      <div className="bg-gray-800 rounded-lg p-4 space-y-3">
        <div className="flex justify-between text-sm">
          <span className="text-gray-300">
            {status?.message || 'Processing model...'}
          </span>
          <span className="text-sky-400">{progress}%</span>
        </div>
        <div className="w-full bg-gray-700 rounded-full h-2">
          <div
            className="bg-sky-500 h-2 rounded-full transition-all duration-300"
            style={{ width: `${progress}%` }}
          />
        </div>
        <p className="text-xs text-gray-500">
          This may take a moment. The model is being rigged with Rigify.
        </p>
      </div>
    </div>
  );
}
