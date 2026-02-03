import { useExportStore } from '../../stores/useExportStore';
import { useModelStore } from '../../stores/useModelStore';
import { useAnimationStore } from '../../stores/useAnimationStore';
import { exportModel, getFullUrl } from '../../services/api';

export default function ExportPanel() {
  const { model } = useModelStore();
  const { myAnimations } = useAnimationStore();
  const {
    format,
    selectedAnimationIds,
    exportWithoutAnimations,
    isExporting,
    downloadUrl,
    error,
    setFormat,
    toggleAnimationSelection,
    selectAllAnimations,
    selectNoAnimations,
    setExportWithoutAnimations,
    setIsExporting,
    setDownloadUrl,
    setError,
  } = useExportStore();

  const handleExport = async () => {
    if (!model) return;
    setIsExporting(true);
    setError(null);
    setDownloadUrl(null);

    try {
      const result = await exportModel({
        model_id: model.model_id,
        format,
        animations: exportWithoutAnimations ? [] : selectedAnimationIds,
        include_rig_controls: false,
      });
      setDownloadUrl(result.download_url);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Export failed');
    } finally {
      setIsExporting(false);
    }
  };

  const handleDownload = () => {
    if (downloadUrl) {
      window.open(getFullUrl(downloadUrl), '_blank');
    }
  };

  return (
    <div className="space-y-3">
      <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
        Export Model
      </h2>

      <div className="bg-gray-800 rounded-lg p-3 space-y-3">
        {/* Format */}
        <div className="space-y-2">
          <p className="text-xs font-medium text-gray-400">Format</p>
          <div className="flex gap-2">
            <FormatOption
              value="glb"
              label="GLB"
              description="Web / Three.js"
              selected={format === 'glb'}
              onClick={() => setFormat('glb')}
            />
            <FormatOption
              value="fbx"
              label="FBX"
              description="Unity / Unreal"
              selected={format === 'fbx'}
              onClick={() => setFormat('fbx')}
            />
          </div>
        </div>

        {/* Animation selection */}
        {myAnimations.length > 0 && (
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <p className="text-xs font-medium text-gray-400">Include Animations</p>
              <div className="flex gap-2">
                <button
                  onClick={() => selectAllAnimations(myAnimations.map((a) => a.id))}
                  className="text-xs text-sky-400 hover:text-sky-300"
                >
                  All
                </button>
                <button
                  onClick={selectNoAnimations}
                  className="text-xs text-gray-400 hover:text-gray-300"
                >
                  None
                </button>
              </div>
            </div>
            <div className="space-y-1 max-h-32 overflow-y-auto">
              {myAnimations.map((anim) => (
                <label
                  key={anim.id}
                  className="flex items-center gap-2 px-2 py-1 rounded hover:bg-gray-700/50 cursor-pointer"
                >
                  <input
                    type="checkbox"
                    checked={selectedAnimationIds.includes(anim.id)}
                    onChange={() => toggleAnimationSelection(anim.id)}
                    disabled={exportWithoutAnimations}
                    className="rounded border-gray-600 bg-gray-700 text-sky-500 focus:ring-sky-500 focus:ring-offset-0"
                  />
                  <span
                    className={`text-sm ${
                      exportWithoutAnimations ? 'text-gray-600' : 'text-gray-300'
                    }`}
                  >
                    {anim.name}
                  </span>
                </label>
              ))}
            </div>
          </div>
        )}

        {/* Export without animations */}
        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={exportWithoutAnimations}
            onChange={(e) => setExportWithoutAnimations(e.target.checked)}
            className="rounded border-gray-600 bg-gray-700 text-sky-500 focus:ring-sky-500 focus:ring-offset-0"
          />
          <span className="text-sm text-gray-300">Export without animations</span>
        </label>
      </div>

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-2">
          <p className="text-xs text-red-400">{error}</p>
        </div>
      )}

      {downloadUrl ? (
        <button
          onClick={handleDownload}
          className="w-full py-2.5 rounded-lg font-medium text-sm bg-emerald-500 hover:bg-emerald-600 text-white transition-colors"
        >
          Download .{format.toUpperCase()}
        </button>
      ) : (
        <button
          onClick={handleExport}
          disabled={isExporting || !model}
          className={`w-full py-2.5 rounded-lg font-medium text-sm transition-colors ${
            isExporting || !model
              ? 'bg-gray-700 text-gray-500 cursor-not-allowed'
              : 'bg-sky-500 hover:bg-sky-600 text-white'
          }`}
        >
          {isExporting ? 'Exporting...' : 'Export'}
        </button>
      )}
    </div>
  );
}

function FormatOption({
  label,
  description,
  selected,
  onClick,
}: {
  value: string;
  label: string;
  description: string;
  selected: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`flex-1 p-2 rounded-lg border text-left transition-colors ${
        selected
          ? 'border-sky-500 bg-sky-500/10'
          : 'border-gray-700 hover:border-gray-600'
      }`}
    >
      <p className={`text-sm font-medium ${selected ? 'text-sky-400' : 'text-gray-300'}`}>
        {label}
      </p>
      <p className="text-xs text-gray-500">{description}</p>
    </button>
  );
}
