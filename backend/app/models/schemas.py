from pydantic import BaseModel, Field
from typing import Optional


class UploadResponse(BaseModel):
    success: bool = True
    model_id: str
    preview_url: str
    original_format: str
    vertex_count: int
    has_skeleton: bool = False


class MarkerPositions(BaseModel):
    chin: tuple[float, float, float]
    groin: tuple[float, float, float]
    wrist_l: tuple[float, float, float]
    wrist_r: tuple[float, float, float]
    elbow_l: tuple[float, float, float]
    elbow_r: tuple[float, float, float]
    knee_l: tuple[float, float, float]
    knee_r: tuple[float, float, float]


class RigRequest(BaseModel):
    model_id: str
    markers: dict[str, tuple[float, float, float]]


class RigResponse(BaseModel):
    success: bool = True
    rigged_model_url: str
    skeleton_info: dict = Field(default_factory=lambda: {"bone_count": 52, "rig_type": "rigify_human"})
    processing_time_ms: int = 0


class AnimationInfo(BaseModel):
    id: str
    name: str
    category: str
    duration_seconds: float
    thumbnail_url: str = ""
    preview_url: str = ""
    loop: bool = True
    tags: list[str] = []
    description: str = ""


class AnimationsResponse(BaseModel):
    animations: list[AnimationInfo]
    categories: list[str]


class ApplyAnimationRequest(BaseModel):
    model_id: str
    animation_id: str


class ApplyAnimationResponse(BaseModel):
    success: bool = True
    animated_model_url: str


class ExportRequest(BaseModel):
    model_id: str
    format: str = "glb"
    animations: list[str] = []
    include_rig_controls: bool = False


class ExportResponse(BaseModel):
    success: bool = True
    download_url: str
    file_size_bytes: int = 0
    expires_at: str = ""


class StatusResponse(BaseModel):
    model_id: str
    status: str
    stage: str
    progress: int
    message: str


class ErrorResponse(BaseModel):
    success: bool = False
    error: dict = Field(default_factory=dict)
