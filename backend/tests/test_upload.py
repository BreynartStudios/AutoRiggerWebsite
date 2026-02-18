import io
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"


def test_upload_invalid_format():
    file_content = b"not a real model"
    response = client.post(
        "/api/upload",
        files={"file": ("model.txt", io.BytesIO(file_content), "text/plain")},
    )
    assert response.status_code == 400


def test_upload_glb():
    # GLB magic bytes: "glTF"
    glb_header = b"glTF\x02\x00\x00\x00"
    glb_content = glb_header + b"\x00" * 100

    response = client.post(
        "/api/upload",
        files={"file": ("test.glb", io.BytesIO(glb_content), "model/gltf-binary")},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "model_id" in data
    assert data["original_format"] == "glb"


def test_list_animations():
    response = client.get("/api/animations")
    assert response.status_code == 200
    data = response.json()
    assert "animations" in data
    assert "categories" in data
    assert len(data["animations"]) > 0
