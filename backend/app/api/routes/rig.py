import json
import time
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.config import UPLOADS_DIR, PROCESSED_DIR
from app.models.schemas import RigRequest, RigResponse
from app.services.blender_service import run_blender_script, BlenderError

router = APIRouter()

REQUIRED_MARKERS = ["chin", "groin", "wrist_l", "wrist_r", "elbow_l", "elbow_r", "knee_l", "knee_r"]


@router.post("/rig", response_model=RigResponse)
async def rig_model(request: RigRequest):
    # Validate model exists
    model_dir = UPLOADS_DIR / request.model_id
    if not model_dir.exists():
        raise HTTPException(status_code=404, detail="Model not found")

    # Find original file
    original_files = list(model_dir.glob("original.*"))
    if not original_files:
        raise HTTPException(status_code=404, detail="Original model file not found")
    input_path = original_files[0]

    # Validate markers
    for marker in REQUIRED_MARKERS:
        if marker not in request.markers:
            raise HTTPException(status_code=400, detail=f"Missing required marker: {marker}")

    # Prepare output
    output_dir = PROCESSED_DIR / request.model_id
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / "rigged.glb"

    # Write markers to temp JSON
    markers_path = model_dir / "markers.json"
    markers_dict = {k: list(v) for k, v in request.markers.items()}
    markers_path.write_text(json.dumps(markers_dict))

    # Run Blender
    start_time = time.time()
    try:
        await run_blender_script(
            "auto_rig.py",
            args=[
                "--input", str(input_path),
                "--markers", str(markers_path),
                "--output", str(output_path),
            ],
        )
    except BlenderError as e:
        raise HTTPException(status_code=500, detail=f"Rigging failed: {str(e)}")
    processing_time = int((time.time() - start_time) * 1000)

    if not output_path.exists():
        raise HTTPException(status_code=500, detail="Rigging failed: no output produced")

    return RigResponse(
        rigged_model_url=f"/api/models/{request.model_id}/rigged.glb",
        skeleton_info={"bone_count": 52, "rig_type": "rigify_human"},
        processing_time_ms=processing_time,
    )
