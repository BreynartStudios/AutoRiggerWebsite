import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

DATA_DIR = Path(os.getenv("DATA_DIR", str(BASE_DIR / "data")))
UPLOADS_DIR = DATA_DIR / "uploads"
PROCESSED_DIR = DATA_DIR / "processed"
ANIMATIONS_DIR = DATA_DIR / "animations"
EXPORTS_DIR = DATA_DIR / "exports"
TEMPLATES_DIR = DATA_DIR / "templates"

BLENDER_PATH = os.getenv("BLENDER_PATH", "blender")
BLENDER_SCRIPTS_DIR = BASE_DIR / "blender_scripts"

MAX_UPLOAD_SIZE = int(os.getenv("MAX_UPLOAD_SIZE", 52428800))  # 50MB
MAX_VERTEX_COUNT = 100000
JOB_TIMEOUT = 300  # 5 minutes
FILE_RETENTION_HOURS = 24
MAX_CONCURRENT_JOBS = 2

ALLOWED_MODEL_EXTENSIONS = {".obj", ".fbx", ".glb", ".gltf"}
ALLOWED_ANIMATION_EXTENSIONS = {".bvh", ".fbx"}

CORS_ORIGINS = os.getenv("CORS_ORIGINS", "http://localhost:3000").split(",")

# Ensure directories exist
for d in [UPLOADS_DIR, PROCESSED_DIR, EXPORTS_DIR]:
    d.mkdir(parents=True, exist_ok=True)
