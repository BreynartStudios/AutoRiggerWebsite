import uuid
import shutil
from pathlib import Path

from fastapi import APIRouter, UploadFile, File, HTTPException

from app.config import UPLOADS_DIR, ALLOWED_MODEL_EXTENSIONS, MAX_UPLOAD_SIZE
from app.models.schemas import UploadResponse
from app.services.model_service import convert_to_preview

router = APIRouter()


@router.post("/upload", response_model=UploadResponse)
async def upload_model(file: UploadFile = File(...)):
    # Validate extension
    ext = Path(file.filename or "").suffix.lower()
    if ext not in ALLOWED_MODEL_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported format '{ext}'. Allowed: {', '.join(ALLOWED_MODEL_EXTENSIONS)}",
        )

    # Read file and check size
    content = await file.read()
    if len(content) > MAX_UPLOAD_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({len(content)} bytes). Maximum: {MAX_UPLOAD_SIZE} bytes",
        )

    # Save uploaded file
    model_id = str(uuid.uuid4())
    model_dir = UPLOADS_DIR / model_id
    model_dir.mkdir(parents=True, exist_ok=True)

    original_path = model_dir / f"original{ext}"
    original_path.write_bytes(content)

    # Generate preview GLB (convert if needed)
    preview_path = model_dir / "preview.glb"
    vertex_count = await convert_to_preview(original_path, preview_path)

    return UploadResponse(
        model_id=model_id,
        preview_url=f"/api/models/{model_id}/preview.glb",
        original_format=ext.lstrip("."),
        vertex_count=vertex_count,
        has_skeleton=False,
    )


@router.get("/models/{model_id}/preview.glb")
async def get_model_preview(model_id: str):
    from fastapi.responses import FileResponse

    preview_path = UPLOADS_DIR / model_id / "preview.glb"
    if not preview_path.exists():
        raise HTTPException(status_code=404, detail="Model not found")
    return FileResponse(preview_path, media_type="model/gltf-binary")


@router.get("/models/{model_id}/rigged.glb")
async def get_rigged_model(model_id: str):
    from fastapi.responses import FileResponse
    from app.config import PROCESSED_DIR

    rigged_path = PROCESSED_DIR / model_id / "rigged.glb"
    if not rigged_path.exists():
        raise HTTPException(status_code=404, detail="Rigged model not found")
    return FileResponse(rigged_path, media_type="model/gltf-binary")


@router.get("/models/{model_id}/animated/{animation_id}.glb")
async def get_animated_model(model_id: str, animation_id: str):
    from fastapi.responses import FileResponse
    from app.config import PROCESSED_DIR

    animated_path = PROCESSED_DIR / model_id / f"animated_{animation_id}.glb"
    if not animated_path.exists():
        raise HTTPException(status_code=404, detail="Animated model not found")
    return FileResponse(animated_path, media_type="model/gltf-binary")


@router.get("/models/{model_id}/status")
async def get_model_status(model_id: str):
    from app.services.model_service import get_job_status

    status = get_job_status(model_id)
    if not status:
        raise HTTPException(status_code=404, detail="Model not found")
    return status
