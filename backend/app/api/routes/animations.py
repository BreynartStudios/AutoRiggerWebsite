import json
from pathlib import Path

from fastapi import APIRouter, HTTPException

from app.config import ANIMATIONS_DIR, PROCESSED_DIR, UPLOADS_DIR
from app.models.schemas import AnimationInfo, AnimationsResponse, ApplyAnimationRequest, ApplyAnimationResponse
from app.services.blender_service import run_blender_script

router = APIRouter()


def load_animation_library() -> list[AnimationInfo]:
    """Scan animations directory for available animations with metadata."""
    animations = []

    if not ANIMATIONS_DIR.exists():
        return animations

    for category_dir in sorted(ANIMATIONS_DIR.iterdir()):
        if not category_dir.is_dir():
            continue
        category = category_dir.name

        for meta_file in sorted(category_dir.glob("*.json")):
            try:
                data = json.loads(meta_file.read_text())
                anim = AnimationInfo(
                    id=data.get("id", meta_file.stem),
                    name=data.get("name", meta_file.stem.replace("_", " ").title()),
                    category=data.get("category", category),
                    duration_seconds=data.get("duration_seconds", 1.0),
                    thumbnail_url=data.get("thumbnail_url", ""),
                    preview_url=data.get("preview_url", ""),
                    loop=data.get("loop", True),
                    tags=data.get("tags", []),
                    description=data.get("description", ""),
                )
                animations.append(anim)
            except (json.JSONDecodeError, KeyError):
                continue

    return animations


def get_available_categories() -> list[str]:
    """Get list of animation categories from directory structure."""
    if not ANIMATIONS_DIR.exists():
        return []
    return sorted(
        d.name for d in ANIMATIONS_DIR.iterdir()
        if d.is_dir() and any(d.glob("*.json"))
    )


@router.get("/animations", response_model=AnimationsResponse)
async def list_animations():
    animations = load_animation_library()
    categories = get_available_categories()

    # If no animations exist on disk, return demo data
    if not animations:
        animations = get_demo_animations()
        categories = ["locomotion", "combat", "social", "misc"]

    return AnimationsResponse(animations=animations, categories=categories)


@router.post("/apply-animation", response_model=ApplyAnimationResponse)
async def apply_animation(request: ApplyAnimationRequest):
    # Validate rigged model exists
    rigged_path = PROCESSED_DIR / request.model_id / "rigged.glb"
    if not rigged_path.exists():
        raise HTTPException(status_code=404, detail="Rigged model not found. Rig the model first.")

    # Find animation file
    anim_file = find_animation_file(request.animation_id)
    if not anim_file:
        raise HTTPException(status_code=404, detail=f"Animation '{request.animation_id}' not found")

    # Output path
    output_path = PROCESSED_DIR / request.model_id / f"animated_{request.animation_id}.glb"

    await run_blender_script(
        "apply_animation.py",
        args=[
            "--model", str(rigged_path),
            "--animation", str(anim_file),
            "--output", str(output_path),
            "--name", request.animation_id,
        ],
    )

    if not output_path.exists():
        raise HTTPException(status_code=500, detail="Animation application failed")

    return ApplyAnimationResponse(
        animated_model_url=f"/api/models/{request.model_id}/animated/{request.animation_id}.glb",
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


def get_demo_animations() -> list[AnimationInfo]:
    """Return demo animation list when no real animations are available."""
    demos = [
        ("idle_01", "Idle", "misc", 2.0, True, ["idle", "standing"]),
        ("walk_01", "Walk", "locomotion", 1.0, True, ["walk", "cycle"]),
        ("run_01", "Run", "locomotion", 0.8, True, ["run", "cycle"]),
        ("jump_01", "Jump", "locomotion", 1.2, False, ["jump"]),
        ("sprint_01", "Sprint", "locomotion", 0.6, True, ["sprint", "fast"]),
        ("crouch_01", "Crouch", "locomotion", 0.5, False, ["crouch"]),
        ("punch_01", "Punch", "combat", 0.8, False, ["punch", "attack"]),
        ("kick_01", "Kick", "combat", 1.0, False, ["kick", "attack"]),
        ("block_01", "Block", "combat", 0.6, False, ["block", "defend"]),
        ("hit_react_01", "Hit React", "combat", 0.7, False, ["hit", "react"]),
        ("death_01", "Death", "combat", 2.0, False, ["death", "fall"]),
        ("wave_01", "Wave", "social", 1.5, False, ["wave", "greet"]),
        ("dance_01", "Dance", "social", 3.0, True, ["dance"]),
        ("bow_01", "Bow", "social", 1.8, False, ["bow"]),
        ("clap_01", "Clap", "social", 1.2, True, ["clap"]),
        ("sit_01", "Sit Down", "social", 2.0, False, ["sit"]),
        ("talk_01", "Talking", "social", 2.5, True, ["talk", "gesture"]),
        ("pick_up_01", "Pick Up", "misc", 1.5, False, ["pick", "item"]),
        ("push_01", "Push", "misc", 1.0, False, ["push"]),
        ("climb_01", "Climb", "misc", 2.0, True, ["climb"]),
    ]

    return [
        AnimationInfo(
            id=id,
            name=name,
            category=cat,
            duration_seconds=dur,
            loop=loop,
            tags=tags,
            description=f"{name} animation",
        )
        for id, name, cat, dur, loop, tags in demos
    ]
