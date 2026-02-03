import { useCallback, useState } from 'react';
import { useModelStore } from '../../stores/useModelStore';
import { useMarkerStore } from '../../stores/useMarkerStore';
import { uploadModel } from '../../services/api';
import { validateModelFile, formatFileSize } from '../../utils/fileValidation';
import type { UploadedModel } from '../../types/model';

export default function UploadPanel() {
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);
  const [skeletonPrompt, setSkeletonPrompt] = useState<UploadedModel | null>(null);

  const { setModel, setRiggedModelUrl, setStage, setError: setGlobalError } = useModelStore();
  const { startPlacing } = useMarkerStore();

  const proceedWithMarkers = useCallback(
    (model: UploadedModel) => {
      setModel(model);
      startPlacing();
      setSkeletonPrompt(null);
    },
    [setModel, startPlacing]
  );

  const proceedWithExistingSkeleton = useCallback(
    (model: UploadedModel) => {
      setModel(model);
      // Use the uploaded model directly as "rigged" since it already has a skeleton
      setRiggedModelUrl(model.preview_url);
      setStage('animations');
      setSkeletonPrompt(null);
    },
    [setModel, setRiggedModelUrl, setStage]
  );

  const handleFile = useCallback(
    async (file: File) => {
      setError(null);
      setSkeletonPrompt(null);
      const validation = validateModelFile(file);
      if (!validation.valid) {
        setError(validation.error!);
        return;
      }

      setUploading(true);
      setUploadProgress(0);

      try {
        const progressInterval = setInterval(() => {
          setUploadProgress((p) => Math.min(p + 10, 90));
        }, 200);

        const result = await uploadModel(file);
        clearInterval(progressInterval);
        setUploadProgress(100);

        const model: UploadedModel = {
          model_id: result.model_id,
          preview_url: result.preview_url,
          original_format: result.original_format,
          vertex_count: result.vertex_count,
          has_skeleton: result.has_skeleton,
        };

        if (result.has_skeleton) {
          setSkeletonPrompt(model);
        } else {
          proceedWithMarkers(model);
        }
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Upload failed';
        setError(msg);
        setGlobalError(msg);
      } finally {
        setUploading(false);
      }
    },
    [setGlobalError, proceedWithMarkers]
  );

  const handleDrop = useCallback(
    (e: React.DragEvent) => {
      e.preventDefault();
      setDragOver(false);
      const file = e.dataTransfer.files[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragOver(true);
  }, []);

  const handleDragLeave = useCallback(() => {
    setDragOver(false);
  }, []);

  const handleInputChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      const file = e.target.files?.[0];
      if (file) handleFile(file);
    },
    [handleFile]
  );

  return (
    <div className="space-y-4">
      <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
        Upload Model
      </h2>

      {/* Skeleton detected dialog */}
      {skeletonPrompt && (
        <div className="bg-sky-500/10 border border-sky-500/30 rounded-lg p-4 space-y-3">
          <p className="text-sm text-sky-300 font-medium">
            Skeleton detected
          </p>
          <p className="text-xs text-gray-300">
            This model already has a skeleton. You can use it directly for animations
            or place markers to create a new rig.
          </p>
          <div className="flex gap-2">
            <button
              onClick={() => proceedWithExistingSkeleton(skeletonPrompt)}
              className="flex-1 py-2 rounded-lg text-sm font-medium bg-sky-500 hover:bg-sky-600 text-white transition-colors"
            >
              Use existing skeleton
            </button>
            <button
              onClick={() => proceedWithMarkers(skeletonPrompt)}
              className="flex-1 py-2 rounded-lg text-sm font-medium bg-gray-700 hover:bg-gray-600 text-gray-300 transition-colors"
            >
              Re-rig with markers
            </button>
          </div>
        </div>
      )}

      <div
        onDrop={handleDrop}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        className={`relative border-2 border-dashed rounded-lg p-8 text-center transition-colors cursor-pointer ${
          dragOver
            ? 'border-sky-400 bg-sky-500/10'
            : 'border-gray-600 hover:border-gray-500 bg-gray-800/50'
        }`}
      >
        <input
          type="file"
          accept=".obj,.fbx,.glb,.gltf"
          onChange={handleInputChange}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
          disabled={uploading}
        />
        <div className="space-y-2">
          <div className="text-3xl text-gray-400">
            {uploading ? '...' : '+'}
          </div>
          <p className="text-sm text-gray-300">
            {uploading ? 'Uploading...' : 'Drag & drop your 3D model'}
          </p>
          <p className="text-xs text-gray-500">
            or click to browse
          </p>
        </div>
      </div>

      {uploading && (
        <div className="space-y-2">
          <div className="flex justify-between text-xs text-gray-400">
            <span>Uploading</span>
            <span>{uploadProgress}%</span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-1.5">
            <div
              className="bg-sky-500 h-1.5 rounded-full transition-all duration-200"
              style={{ width: `${uploadProgress}%` }}
            />
          </div>
        </div>
      )}

      {error && (
        <div className="bg-red-500/10 border border-red-500/30 rounded-lg p-3">
          <p className="text-sm text-red-400">{error}</p>
        </div>
      )}

      <div className="bg-gray-800 rounded-lg p-3 space-y-2">
        <p className="text-xs font-medium text-gray-400">Supported formats</p>
        <div className="flex flex-wrap gap-2">
          {['OBJ', 'FBX', 'GLB', 'GLTF'].map((fmt) => (
            <span
              key={fmt}
              className="text-xs bg-gray-700 text-gray-300 px-2 py-1 rounded"
            >
              .{fmt.toLowerCase()}
            </span>
          ))}
        </div>
        <p className="text-xs text-gray-500">
          Max file size: {formatFileSize(50 * 1024 * 1024)}
        </p>
      </div>
    </div>
  );
}
