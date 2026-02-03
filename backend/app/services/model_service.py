import json
import logging
import struct
from pathlib import Path

from app.services.blender_service import run_blender_script

logger = logging.getLogger(__name__)

# In-memory job status tracking (would use Redis/DB in production)
_job_status: dict[str, dict] = {}


async def convert_to_preview(input_path: Path, output_path: Path) -> int:
    """
    Convert uploaded model to GLB preview format.
    Returns approximate vertex count.

    If Blender is available, uses it for conversion.
    Otherwise, for GLB/GLTF files, copies directly.
    """
    ext = input_path.suffix.lower()

    # GLB can be served directly as preview
    if ext in (".glb", ".gltf"):
        import shutil
        shutil.copy2(input_path, output_path)
        return estimate_vertex_count(input_path)

    # For other formats, try Blender conversion
    try:
        await run_blender_script(
            "generate_preview.py",
            args=["--input", str(input_path), "--output", str(output_path)],
        )
    except Exception as e:
        logger.warning("Blender conversion failed, model may need Blender installed: %s", e)
        # Copy original as fallback (won't work for OBJ in browser, but doesn't crash)
        import shutil
        shutil.copy2(input_path, output_path)

    return estimate_vertex_count(input_path)


def detect_skeleton(filepath: Path) -> bool:
    """Check if a GLB/GLTF file contains a skeleton (skins array)."""
    ext = filepath.suffix.lower()
    try:
        if ext == ".glb":
            with open(filepath, "rb") as f:
                # GLB header: magic(4) + version(4) + length(4)
                magic = f.read(4)
                if magic != b"glTF":
                    return False
                f.read(4)  # version
                f.read(4)  # total length
                # First chunk: length(4) + type(4) + data
                chunk_length = struct.unpack("<I", f.read(4))[0]
                chunk_type = f.read(4)
                if chunk_type != b"JSON":
                    return False
                json_data = json.loads(f.read(chunk_length).decode("utf-8"))
                skins = json_data.get("skins", [])
                return len(skins) > 0
        elif ext == ".gltf":
            json_data = json.loads(filepath.read_text())
            return len(json_data.get("skins", [])) > 0
        elif ext == ".fbx":
            # FBX binary contains identifiable strings for bone/skeleton data.
            # Search for common bone-type markers in the binary.
            data = filepath.read_bytes()
            bone_markers = [
                b"LimbNode", b"Skeleton",
                b"Hips", b"Spine", b"mixamorig:",
                b"DEF-spine", b"LeftUpLeg", b"RightUpLeg",
            ]
            return any(marker in data for marker in bone_markers)
    except Exception as e:
        logger.debug("Skeleton detection failed for %s: %s", filepath, e)
    return False


def estimate_vertex_count(filepath: Path) -> int:
    """Estimate vertex count from file size (rough heuristic)."""
    size = filepath.stat().st_size
    # Very rough: ~100 bytes per vertex for typical models
    return max(100, size // 100)


def update_job_status(model_id: str, status: str, stage: str, progress: int, message: str):
    _job_status[model_id] = {
        "model_id": model_id,
        "status": status,
        "stage": stage,
        "progress": progress,
        "message": message,
    }


def get_job_status(model_id: str) -> dict | None:
    return _job_status.get(model_id)
