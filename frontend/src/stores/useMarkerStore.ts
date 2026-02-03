import { create } from 'zustand';
import type { Marker, MarkerID } from '../types/marker';
import { MARKER_DEFINITIONS, MARKER_ORDER } from '../types/marker';

interface MarkerState {
  markers: Marker[];
  currentMarkerIndex: number;
  isPlacingMarkers: boolean;
  selectedMarkerId: MarkerID | null;

  getCurrentMarker: () => Marker | null;
  getPlacedMarkers: () => Marker[];
  allMarkersPlaced: () => boolean;
  placeMarker: (position: [number, number, number]) => void;
  updateMarkerPosition: (id: MarkerID, position: [number, number, number]) => void;
  selectMarker: (id: MarkerID | null) => void;
  removeMarker: (id: MarkerID) => void;
  startPlacing: () => void;
  resetMarkers: () => void;
  getMarkersForApi: () => Record<string, [number, number, number]>;
}

function createInitialMarkers(): Marker[] {
  return MARKER_ORDER.map((id) => ({
    id,
    name: MARKER_DEFINITIONS[id].name,
    color: MARKER_DEFINITIONS[id].color,
    position: null,
    placed: false,
  }));
}

export const useMarkerStore = create<MarkerState>((set, get) => ({
  markers: createInitialMarkers(),
  currentMarkerIndex: 0,
  isPlacingMarkers: false,
  selectedMarkerId: null,

  getCurrentMarker: () => {
    const { markers, currentMarkerIndex } = get();
    return currentMarkerIndex < markers.length ? markers[currentMarkerIndex] : null;
  },

  getPlacedMarkers: () => {
    return get().markers.filter((m) => m.placed);
  },

  allMarkersPlaced: () => {
    return get().markers.every((m) => m.placed);
  },

  placeMarker: (position) => {
    const { currentMarkerIndex, markers } = get();
    if (currentMarkerIndex >= markers.length) return;

    const updated = [...markers];
    updated[currentMarkerIndex] = {
      ...updated[currentMarkerIndex],
      position,
      placed: true,
    };

    set({
      markers: updated,
      currentMarkerIndex: currentMarkerIndex + 1,
      selectedMarkerId: null,
    });
  },

  updateMarkerPosition: (id, position) => {
    set({
      markers: get().markers.map((m) =>
        m.id === id ? { ...m, position, placed: true } : m
      ),
    });
  },

  selectMarker: (id) => set({ selectedMarkerId: id }),

  removeMarker: (id) => {
    const markers = get().markers;
    const idx = markers.findIndex((m) => m.id === id);
    if (idx === -1) return;

    const updated = [...markers];
    updated[idx] = { ...updated[idx], position: null, placed: false };

    set({
      markers: updated,
      currentMarkerIndex: Math.min(get().currentMarkerIndex, idx),
      selectedMarkerId: null,
    });
  },

  startPlacing: () =>
    set({
      isPlacingMarkers: true,
      currentMarkerIndex: 0,
      markers: createInitialMarkers(),
    }),

  resetMarkers: () =>
    set({
      markers: createInitialMarkers(),
      currentMarkerIndex: 0,
      selectedMarkerId: null,
      isPlacingMarkers: false,
    }),

  getMarkersForApi: () => {
    const result: Record<string, [number, number, number]> = {};
    for (const marker of get().markers) {
      if (marker.position) {
        result[marker.id] = marker.position;
      }
    }
    return result;
  },
}));
