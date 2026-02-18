import { useMarkerStore } from '../../stores/useMarkerStore';
import type { MarkerID } from '../../types/marker';

export default function MarkerList() {
  const { markers, selectedMarkerId, selectMarker, removeMarker } = useMarkerStore();

  const handleSelect = (id: MarkerID) => {
    selectMarker(selectedMarkerId === id ? null : id);
  };

  const handleRemove = (e: React.MouseEvent, id: MarkerID) => {
    e.stopPropagation();
    removeMarker(id);
  };

  return (
    <div className="space-y-1">
      {markers.map((marker) => (
        <div
          key={marker.id}
          onClick={() => handleSelect(marker.id)}
          className={`flex items-center gap-3 px-3 py-2 rounded-lg cursor-pointer transition-colors ${
            selectedMarkerId === marker.id
              ? 'bg-gray-700'
              : 'hover:bg-gray-800/50'
          }`}
        >
          <div
            className="w-3 h-3 rounded-full shrink-0"
            style={{
              backgroundColor: marker.placed ? marker.color : 'transparent',
              border: `2px solid ${marker.color}`,
            }}
          />
          <span
            className={`text-sm flex-1 ${
              marker.placed ? 'text-gray-200' : 'text-gray-500'
            }`}
          >
            {marker.name}
          </span>
          {marker.placed && (
            <>
              <span className="text-xs text-gray-500">
                {marker.position?.map((v) => v.toFixed(2)).join(', ')}
              </span>
              <button
                onClick={(e) => handleRemove(e, marker.id)}
                className="text-gray-500 hover:text-red-400 transition-colors text-xs"
                title="Remove marker"
              >
                x
              </button>
            </>
          )}
        </div>
      ))}
    </div>
  );
}
