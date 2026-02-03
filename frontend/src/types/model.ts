export interface UploadedModel {
  model_id: string;
  preview_url: string;
  original_format: string;
  vertex_count: number;
  has_skeleton: boolean;
}

export interface ModelStatus {
  model_id: string;
  status: 'uploading' | 'processing' | 'rigging' | 'complete' | 'error';
  stage: string;
  progress: number;
  message: string;
}

export interface RigResult {
  rigged_model_url: string;
  skeleton_info: {
    bone_count: number;
    rig_type: string;
  };
  processing_time_ms: number;
}
