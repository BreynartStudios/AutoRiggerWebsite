const ALLOWED_EXTENSIONS = ['.obj', '.fbx', '.glb', '.gltf'];
const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

export function validateModelFile(file: File): { valid: boolean; error?: string } {
  const ext = '.' + file.name.split('.').pop()?.toLowerCase();

  if (!ALLOWED_EXTENSIONS.includes(ext)) {
    return {
      valid: false,
      error: `Unsupported format "${ext}". Supported: ${ALLOWED_EXTENSIONS.join(', ')}`,
    };
  }

  if (file.size > MAX_FILE_SIZE) {
    const sizeMB = (file.size / (1024 * 1024)).toFixed(1);
    return {
      valid: false,
      error: `File too large (${sizeMB} MB). Maximum: 50 MB`,
    };
  }

  return { valid: true };
}

export function getFileExtension(filename: string): string {
  return filename.split('.').pop()?.toLowerCase() || '';
}

export function formatFileSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B';
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}
