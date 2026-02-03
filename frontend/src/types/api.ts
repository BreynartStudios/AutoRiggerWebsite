export interface ApiResponse<T = unknown> {
  success: boolean;
  data?: T;
  error?: ApiError;
}

export interface ApiError {
  code: string;
  message: string;
  details?: string;
  suggestion?: string;
}

export interface UploadResponse {
  success: boolean;
  model_id: string;
  preview_url: string;
  original_format: string;
  vertex_count: number;
  has_skeleton: boolean;
}

export interface RigRequest {
  model_id: string;
  markers: Record<string, [number, number, number]>;
}

export interface RigResponse {
  success: boolean;
  rigged_model_url: string;
  skeleton_info: {
    bone_count: number;
    rig_type: string;
  };
  processing_time_ms: number;
}

export interface AnimationsResponse {
  animations: import('./animation').Animation[];
  categories: string[];
}

export interface ApplyAnimationRequest {
  model_id: string;
  animation_id: string;
}

export interface ApplyAnimationResponse {
  success: boolean;
  animated_model_url: string;
}

export interface ExportRequest {
  model_id: string;
  format: 'fbx' | 'glb';
  animations: string[];
  include_rig_controls: boolean;
}

export interface ExportResponse {
  success: boolean;
  download_url: string;
  file_size_bytes: number;
  expires_at: string;
}

export interface StatusResponse {
  model_id: string;
  status: string;
  stage: string;
  progress: number;
  message: string;
}
