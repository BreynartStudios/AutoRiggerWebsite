from enum import Enum


class ModelFormat(str, Enum):
    OBJ = "obj"
    FBX = "fbx"
    GLB = "glb"
    GLTF = "gltf"


class ExportFormat(str, Enum):
    FBX = "fbx"
    GLB = "glb"


class JobStatus(str, Enum):
    PENDING = "pending"
    UPLOADING = "uploading"
    PROCESSING = "processing"
    RIGGING = "rigging"
    COMPLETE = "complete"
    ERROR = "error"


class AnimationCategory(str, Enum):
    LOCOMOTION = "locomotion"
    COMBAT = "combat"
    SOCIAL = "social"
    MISC = "misc"
