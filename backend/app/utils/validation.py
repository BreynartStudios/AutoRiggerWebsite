from pathlib import Path
from app.config import ALLOWED_MODEL_EXTENSIONS, MAX_UPLOAD_SIZE

# Magic bytes for file type validation
MAGIC_BYTES = {
    ".glb": b"glTF",
    ".fbx": b"Kaydara FBX Binary",
}


def validate_file_type(filepath: Path) -> bool:
    """Validate file type using magic bytes (not just extension)."""
    ext = filepath.suffix.lower()

    if ext not in ALLOWED_MODEL_EXTENSIONS:
        return False

    if ext in MAGIC_BYTES:
        with open(filepath, "rb") as f:
            header = f.read(len(MAGIC_BYTES[ext]))
            return header.startswith(MAGIC_BYTES[ext])

    # OBJ and GLTF are text-based, harder to validate by magic bytes
    return True


def validate_file_size(filepath: Path) -> bool:
    """Check file size is within limits."""
    return filepath.stat().st_size <= MAX_UPLOAD_SIZE


def sanitize_filename(filename: str) -> str:
    """Sanitize a filename to prevent path traversal."""
    # Remove directory separators and null bytes
    name = Path(filename).name
    name = name.replace("\x00", "")
    return name
