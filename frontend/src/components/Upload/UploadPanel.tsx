import { useCallback, useState } from 'react';
import { useModelStore } from '../../stores/useModelStore';
import { useMarkerStore } from '../../stores/useMarkerStore';
import { uploadModel } from '../../services/api';
import { validateModelFile, formatFileSize } from '../../utils/fileValidation';

export default function UploadPanel() {
  const [dragOver, setDragOver] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [uploadProgress, setUploadProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const { setModel, setError: setGlobalError } = useModelStore();
  const { startPlacing } = useMarkerStore();

  const handleFile = useCallback(
    async (file: File) => {
      setError(null);
      const validation = validateModelFile(file);
      if (!validation.valid) {
        setError(validation.error!);
        return;
      }

      setUploading(true);
      setUploadProgress(0);

      try {
        // Simulate progress while uploading
        const progressInterval = setInterval(() => {
          setUploadProgress((p) => Math.min(p + 10, 90));
        }, 200);

        const result = await uploadModel(file);
        clearInterval(progressInterval);
        setUploadProgress(100);

        setModel({
          model_id: result.model_id,
          preview_url: result.preview_url,
          original_format: result.original_format,
          vertex_count: result.vertex_count,
          has_skeleton: result.has_skeleton,
        });
        startPlacing();
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Upload failed';
        setError(msg);
        setGlobalError(msg);
      } finally {
        setUploading(false);
      }
    },
    [setModel, setGlobalError, startPlacing]
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
