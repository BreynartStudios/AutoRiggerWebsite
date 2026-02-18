from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import CORS_ORIGINS, DATA_DIR
from app.api.routes import upload, rig, animations, export

app = FastAPI(
    title="OpenRig API",
    description="Open-source auto-rigging and animation service",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(upload.router, prefix="/api", tags=["upload"])
app.include_router(rig.router, prefix="/api", tags=["rig"])
app.include_router(animations.router, prefix="/api", tags=["animations"])
app.include_router(export.router, prefix="/api", tags=["export"])

# Serve static data files (processed models, animations, etc.)
app.mount("/data", StaticFiles(directory=str(DATA_DIR)), name="data")


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "service": "openrig"}
