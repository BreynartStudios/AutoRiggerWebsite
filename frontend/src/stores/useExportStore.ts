import { create } from 'zustand';

interface ExportState {
  format: 'fbx' | 'glb';
  selectedAnimationIds: string[];
  exportWithoutAnimations: boolean;
  isExporting: boolean;
  downloadUrl: string | null;
  error: string | null;

  setFormat: (format: 'fbx' | 'glb') => void;
  toggleAnimationSelection: (id: string) => void;
  selectAllAnimations: (ids: string[]) => void;
  selectNoAnimations: () => void;
  setExportWithoutAnimations: (value: boolean) => void;
  setIsExporting: (exporting: boolean) => void;
  setDownloadUrl: (url: string | null) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useExportStore = create<ExportState>((set, get) => ({
  format: 'glb',
  selectedAnimationIds: [],
  exportWithoutAnimations: false,
  isExporting: false,
  downloadUrl: null,
  error: null,

  setFormat: (format) => set({ format, downloadUrl: null, error: null }),

  toggleAnimationSelection: (id) => {
    const { selectedAnimationIds } = get();
    if (selectedAnimationIds.includes(id)) {
      set({ selectedAnimationIds: selectedAnimationIds.filter((a) => a !== id) });
    } else {
      set({ selectedAnimationIds: [...selectedAnimationIds, id] });
    }
  },

  selectAllAnimations: (ids) => set({ selectedAnimationIds: ids }),
  selectNoAnimations: () => set({ selectedAnimationIds: [] }),
  setExportWithoutAnimations: (exportWithoutAnimations) => set({ exportWithoutAnimations }),
  setIsExporting: (isExporting) => set({ isExporting }),
  setDownloadUrl: (downloadUrl) => set({ downloadUrl }),
  setError: (error) => set({ error }),
  reset: () =>
    set({
      format: 'glb',
      selectedAnimationIds: [],
      exportWithoutAnimations: false,
      isExporting: false,
      downloadUrl: null,
      error: null,
    }),
}));
