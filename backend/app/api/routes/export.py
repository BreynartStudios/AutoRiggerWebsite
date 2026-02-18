import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

from app.config import PROCESSED_DIR, EXPORTS_DIR, ANIMATIONS_DIR
from app.models.schemas import ExportRequest, ExportResponse
from app.services.blender_service import run_blender_script, BlenderError

router = APIRouter()


@router.post("/export", response_model=ExportResponse)
async def export_model(request: ExportRequest):
    # Validate rigged model exists
    rigged_path = PROCESSED_DIR / request.model_id / "rigged.glb"
    if not rigged_path.exists():
        raise HTTPException(status_code=404, detail="Rigged model not found")

    export_id = str(uuid.uuid4())
    ext = request.format.lower()
    output_path = EXPORTS_DIR / f"{export_id}.{ext}"

    if request.animations:
        # Find animation files
        anim_paths = []
        anim_names = []
        for anim_id in request.animations:
            anim_file = find_animation_file(anim_id)
            if anim_file:
                anim_paths.append(str(anim_file))
                anim_names.append(anim_id)

        if anim_paths:
            try:
                await run_blender_script(
                    "export_model.py",
                    args=[
                        "--model", str(rigged_path),
                        "--animations", ",".join(anim_paths),
                        "--names", ",".join(anim_names),
                        "--format", ext,
                        "--output", str(output_path),
                    ],
                )
            except BlenderError as e:
                raise HTTPException(status_code=500, detail=f"Export failed: {str(e)[:500]}")
        else:
            # No animation files found, export without animations
            try:
                await export_without_animations(rigged_path, output_path, ext)
            except BlenderError as e:
                raise HTTPException(status_code=500, detail=f"Export failed: {str(e)[:500]}")
    else:
        try:
            await export_without_animations(rigged_path, output_path, ext)
        except BlenderError as e:
            raise HTTPException(status_code=500, detail=f"Export failed: {str(e)[:500]}")

    if not output_path.exists():
        raise HTTPException(status_code=500, detail="Export failed")

    file_size = output_path.stat().st_size
    expires = datetime.now(timezone.utc) + timedelta(hours=24)

    return ExportResponse(
        download_url=f"/api/downloads/{export_id}.{ext}",
        file_size_bytes=file_size,
        expires_at=expires.isoformat(),
    )


@router.get("/downloads/{filename}")
async def download_file(filename: str):
    filepath = EXPORTS_DIR / filename
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found or expired")

    media_type = "model/gltf-binary" if filename.endswith(".glb") else "application/octet-stream"
    return FileResponse(
        filepath,
        media_type=media_type,
        filename=filename,
    )


async def export_without_animations(model_path: Path, output_path: Path, format: str):
    """Export model without animations using Blender or simple copy."""
    if model_path.suffix.lower() == f".{format}":
        # Same format, just copy
        import shutil
        shutil.copy2(model_path, output_path)
    else:
        await run_blender_script(
            "export_model.py",
            args=[
                "--model", str(model_path),
                "--animations", "",
                "--names", "",
                "--format", format,
                "--output", str(output_path),
            ],
        )


def find_animation_file(animation_id: str) -> Path | None:
    """Find animation BVH/FBX file by ID."""
    for category_dir in ANIMATIONS_DIR.iterdir():
        if not category_dir.is_dir():
            continue
        for ext in [".bvh", ".fbx"]:
            path = category_dir / f"{animation_id}{ext}"
            if path.exists():
                return path
    return None
