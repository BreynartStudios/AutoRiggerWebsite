import { create } from 'zustand';
import type { UploadedModel, ModelStatus } from '../types/model';

export type AppStage = 'upload' | 'markers' | 'rigging' | 'animations' | 'export';

interface ModelState {
  model: UploadedModel | null;
  riggedModelUrl: string | null;
  animatedModelUrl: string | null;
  status: ModelStatus | null;
  stage: AppStage;
  isProcessing: boolean;
  error: string | null;

  setModel: (model: UploadedModel) => void;
  setRiggedModelUrl: (url: string) => void;
  setAnimatedModelUrl: (url: string | null) => void;
  setStatus: (status: ModelStatus | null) => void;
  setStage: (stage: AppStage) => void;
  setProcessing: (processing: boolean) => void;
  setError: (error: string | null) => void;
  reset: () => void;
}

export const useModelStore = create<ModelState>((set) => ({
  model: null,
  riggedModelUrl: null,
  animatedModelUrl: null,
  status: null,
  stage: 'upload',
  isProcessing: false,
  error: null,

  setModel: (model) => set({ model, stage: 'markers', error: null }),
  setRiggedModelUrl: (url) => set({ riggedModelUrl: url, stage: 'animations' }),
  setAnimatedModelUrl: (url) => set({ animatedModelUrl: url }),
  setStatus: (status) => set({ status }),
  setStage: (stage) => set({ stage }),
  setProcessing: (isProcessing) => set({ isProcessing }),
  setError: (error) => set({ error, isProcessing: false }),
  reset: () =>
    set({
      model: null,
      riggedModelUrl: null,
      animatedModelUrl: null,
      status: null,
      stage: 'upload',
      isProcessing: false,
      error: null,
    }),
}));
