import axios from 'axios';
import type {
  UploadResponse,
  RigRequest,
  RigResponse,
  AnimationsResponse,
  ApplyAnimationRequest,
  ApplyAnimationResponse,
  ExportRequest,
  ExportResponse,
  StatusResponse,
} from '../types/api';

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  timeout: 300000, // 5 min for long operations
});

export async function uploadModel(file: File): Promise<UploadResponse> {
  const formData = new FormData();
  formData.append('file', file);
  const { data } = await api.post<UploadResponse>('/api/upload', formData, {
    headers: { 'Content-Type': 'multipart/form-data' },
  });
  return data;
}

export async function rigModel(request: RigRequest): Promise<RigResponse> {
  const { data } = await api.post<RigResponse>('/api/rig', request);
  return data;
}

export async function fetchAnimations(): Promise<AnimationsResponse> {
  const { data } = await api.get<AnimationsResponse>('/api/animations');
  return data;
}

export async function applyAnimation(
  request: ApplyAnimationRequest
): Promise<ApplyAnimationResponse> {
  const { data } = await api.post<ApplyAnimationResponse>('/api/apply-animation', request);
  return data;
}

export async function exportModel(request: ExportRequest): Promise<ExportResponse> {
  const { data } = await api.post<ExportResponse>('/api/export', request);
  return data;
}

export async function getModelStatus(modelId: string): Promise<StatusResponse> {
  const { data } = await api.get<StatusResponse>(`/api/models/${modelId}/status`);
  return data;
}

export function getFullUrl(path: string): string {
  const baseURL = import.meta.env.VITE_API_URL || '';
  return `${baseURL}${path}`;
}

export default api;
