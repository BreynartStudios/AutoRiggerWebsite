import { useMarkerStore } from '../../stores/useMarkerStore';
import { useModelStore } from '../../stores/useModelStore';
import { rigModel } from '../../services/api';
import MarkerList from './MarkerList';

export default function MarkerPanel() {
  const { markers, currentMarkerIndex, allMarkersPlaced, resetMarkers, getMarkersForApi } =
    useMarkerStore();
  const { model, setRiggedModelUrl, setStage, setProcessing, setError, setStatus } =
    useModelStore();

  const currentMarker = currentMarkerIndex < markers.length ? markers[currentMarkerIndex] : null;

  const handleAutoRig = async () => {
    if (!model || !allMarkersPlaced()) return;

    setProcessing(true);
    setStage('rigging');
    setStatus({
      model_id: model.model_id,
      status: 'processing',
      stage: 'rigging',
      progress: 0,
      message: 'Starting auto-rig process...',
    });

    try {
      // Simulate progress updates
      const progressSteps = [
        { progress: 20, message: 'Fitting skeleton to markers...' },
        { progress: 45, message: 'Generating Rigify rig...' },
        { progress: 70, message: 'Applying automatic weights...' },
        { progress: 90, message: 'Exporting rigged model...' },
      ];

      for (const step of progressSteps) {
        setStatus({
          model_id: model.model_id,
          status: 'processing',
          stage: 'rigging',
          progress: step.progress,
          message: step.message,
        });
        await new Promise((r) => setTimeout(r, 800));
      }

      const result = await rigModel({
        model_id: model.model_id,
        markers: getMarkersForApi(),
      });

      setRiggedModelUrl(result.rigged_model_url);
      setStatus(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Rigging failed');
      setStage('markers');
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
          Place Markers
        </h2>
        <button
          onClick={resetMarkers}
          className="text-xs text-gray-400 hover:text-white transition-colors"
        >
          Reset All
        </button>
      </div>

      {currentMarker && !allMarkersPlaced() && (
        <div className="bg-sky-500/10 border border-sky-500/30 rounded-lg p-3">
          <p className="text-sm text-sky-300">
            Click on the character's{' '}
            <strong style={{ color: currentMarker.color }}>
              {currentMarker.name}
            </strong>
          </p>
          <p className="text-xs text-sky-400/60 mt-1">
            Marker {currentMarkerIndex + 1} of {markers.length}
          </p>
        </div>
      )}

      {allMarkersPlaced() && (
        <div className="bg-emerald-500/10 border border-emerald-500/30 rounded-lg p-3">
          <p className="text-sm text-emerald-300">
            All markers placed! Ready to auto-rig.
          </p>
        </div>
      )}

      <MarkerList />

      <button
        onClick={handleAutoRig}
        disabled={!allMarkersPlaced()}
        className={`w-full py-2.5 rounded-lg font-medium text-sm transition-colors ${
          allMarkersPlaced()
            ? 'bg-sky-500 hover:bg-sky-600 text-white'
            : 'bg-gray-700 text-gray-500 cursor-not-allowed'
        }`}
      >
        Auto-Rig
      </button>

      <div className="bg-gray-800 rounded-lg p-3">
        <p className="text-xs text-gray-400 leading-relaxed">
          Place markers on your model to define the skeleton. Click on the 3D model
          in the viewport to place each marker at the specified body part.
        </p>
      </div>
    </div>
  );
}
