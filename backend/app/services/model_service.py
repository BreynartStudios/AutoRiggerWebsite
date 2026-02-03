import logging
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
