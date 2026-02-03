# CLAUDE.md - OpenRig Project Specification

## Project Overview

**OpenRig** is an open-source web application that replicates Mixamo's functionality: automatic character rigging with marker-based skeleton fitting, animation library browsing, and export capabilities for game engines. The system runs on Oracle Cloud Free Tier using Blender headless for processing.

### Core Features
1. **Upload 3D Model** - Support for OBJ, FBX, GLB/GLTF formats
2. **Marker Placement** - Interactive 3D interface to place anatomical markers (like Mixamo)
3. **Auto-Rigging** - Blender headless processes the model with Rigify
4. **Animation Library** - Browse and preview pre-made animations (BVH/FBX format)
5. **Animation Preview** - Real-time 3D viewer with playback controls
6. **Animation Management** - Add/remove animations to a personal list
7. **Export** - Download rigged model with selected animations (FBX or GLB)

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (React + Three.js)                    │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │   Upload    │  │   Marker    │  │  Animation  │  │      Preview        │ │
│  │   Panel     │  │   Editor    │  │   Library   │  │      Viewer         │ │
│  │             │  │             │  │             │  │                     │ │
│  │ - Drag/Drop │  │ - 3D View   │  │ - Grid View │  │ - OrbitControls     │ │
│  │ - Format    │  │ - Click to  │  │ - Search    │  │ - Play/Pause        │ │
│  │   validation│  │   place     │  │ - Categories│  │ - Timeline scrub    │ │
│  │             │  │   markers   │  │ - Preview   │  │ - Animation list    │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                        Export Panel                                     ││
│  │  - Format selection (FBX/GLB)                                           ││
│  │  - Animation selection (checkboxes from added animations)               ││
│  │  - Export without animations option                                     ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ REST API
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                         BACKEND (Python FastAPI)                            │
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐ │
│  │  /upload    │  │  /rig       │  │ /animations │  │     /export         │ │
│  │             │  │             │  │             │  │                     │ │
│  │ Store temp  │  │ Process     │  │ List all    │  │ Combine model +     │ │
│  │ model file  │  │ with        │  │ available   │  │ selected animations │ │
│  │             │  │ Blender     │  │ animations  │  │ Export FBX/GLB      │ │
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘ │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                     Blender Headless Worker                             ││
│  │  - auto_rig.py: Marker-based rigging with Rigify                        ││
│  │  - apply_animation.py: Retarget BVH/FBX to rigged model                 ││
│  │  - export_model.py: Export with embedded animations                     ││
│  └─────────────────────────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
                                      │ File Storage
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           FILE SYSTEM                                       │
│                                                                             │
│  /data                                                                      │
│  ├── /uploads          # Temporary uploaded models                          │
│  ├── /processed        # Rigged models (cached)                             │
│  ├── /animations       # Pre-made animation library (BVH/FBX)               │
│  │   ├── /locomotion   # Walk, Run, Jump, etc.                              │
│  │   ├── /combat       # Punch, Kick, Block, etc.                           │
│  │   ├── /social       # Wave, Dance, Sit, etc.                             │
│  │   └── /misc         # Idle, Death, etc.                                  │
│  └── /exports          # Final exported files (temporary)                   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

### Frontend
| Technology | Purpose | Version |
|------------|---------|---------|
| React | UI Framework | 18.x |
| TypeScript | Type Safety | 5.x |
| Three.js | 3D Rendering | 0.160+ |
| @react-three/fiber | React Three.js binding | 8.x |
| @react-three/drei | Three.js helpers | 9.x |
| Tailwind CSS | Styling | 3.x |
| Zustand | State Management | 4.x |
| Axios | HTTP Client | 1.x |

### Backend
| Technology | Purpose | Version |
|------------|---------|---------|
| Python | Runtime | 3.11+ |
| FastAPI | Web Framework | 0.109+ |
| Uvicorn | ASGI Server | 0.27+ |
| Blender | 3D Processing (headless) | 4.0+ |
| python-multipart | File uploads | 0.0.9+ |

### Infrastructure
| Service | Purpose | Tier |
|---------|---------|------|
| Oracle Cloud | Hosting | Free (ARM A1) |
| Docker | Containerization | Latest |
| Nginx | Reverse Proxy | Latest |

---

## Detailed Component Specifications

### 1. Frontend Components

#### 1.1 App Layout
```
┌────────────────────────────────────────────────────────────┐
│  Header: Logo + "OpenRig" title                            │
├──────────────────┬─────────────────────────────────────────┤
│                  │                                         │
│   Left Sidebar   │           Main 3D Viewport              │
│   (300px)        │                                         │
│                  │   - OrbitControls (rotate, zoom, pan)   │
│   - Upload       │   - Grid floor                          │
│   - Markers UI   │   - Character preview                   │
│   - Animation    │   - Marker spheres (during rigging)     │
│     Library      │                                         │
│   - My Animations│                                         │
│   - Export       │                                         │
│                  │                                         │
│                  ├─────────────────────────────────────────┤
│                  │  Playback Controls (when animation)     │
│                  │  [|<] [<] [▶/❚❚] [>] [>|] ──●────── 0:00│
└──────────────────┴─────────────────────────────────────────┘
```

#### 1.2 Component Tree
```
src/
├── components/
│   ├── Layout/
│   │   ├── Header.tsx
│   │   ├── Sidebar.tsx
│   │   └── MainLayout.tsx
│   │
│   ├── Upload/
│   │   ├── UploadPanel.tsx          # Drag & drop zone
│   │   ├── UploadProgress.tsx       # Upload progress bar
│   │   └── FormatInfo.tsx           # Supported formats tooltip
│   │
│   ├── MarkerEditor/
│   │   ├── MarkerPanel.tsx          # Sidebar UI for markers
│   │   ├── MarkerList.tsx           # List of required markers
│   │   ├── MarkerSphere.tsx         # 3D sphere for each marker
│   │   └── MarkerInstructions.tsx   # Step-by-step guide
│   │
│   ├── Viewer/
│   │   ├── SceneCanvas.tsx          # Main Three.js canvas
│   │   ├── CharacterModel.tsx       # Loaded 3D model
│   │   ├── EnvironmentSetup.tsx     # Lights, grid, background
│   │   ├── CameraControls.tsx       # OrbitControls wrapper
│   │   └── LoadingOverlay.tsx       # Processing indicator
│   │
│   ├── Animation/
│   │   ├── AnimationLibrary.tsx     # Grid of available animations
│   │   ├── AnimationCard.tsx        # Single animation thumbnail
│   │   ├── AnimationSearch.tsx      # Search/filter animations
│   │   ├── AnimationCategories.tsx  # Category tabs
│   │   ├── MyAnimationsList.tsx     # User's added animations
│   │   └── PlaybackControls.tsx     # Play/pause/scrub timeline
│   │
│   └── Export/
│       ├── ExportPanel.tsx          # Export configuration
│       ├── FormatSelector.tsx       # FBX/GLB toggle
│       ├── AnimationSelector.tsx    # Checkboxes for animations
│       └── DownloadButton.tsx       # Trigger export & download
│
├── stores/
│   ├── useModelStore.ts             # Current model state
│   ├── useMarkerStore.ts            # Marker positions
│   ├── useAnimationStore.ts         # Animation library & selection
│   └── useExportStore.ts            # Export configuration
│
├── hooks/
│   ├── useModelLoader.ts            # Load GLB/FBX/OBJ
│   ├── useAnimationMixer.ts         # Three.js AnimationMixer
│   ├── useMarkerPlacement.ts        # Raycasting for markers
│   └── useApiClient.ts              # Backend API calls
│
├── services/
│   └── api.ts                       # Axios instance & endpoints
│
├── types/
│   ├── model.ts                     # Model-related types
│   ├── marker.ts                    # Marker types
│   ├── animation.ts                 # Animation types
│   └── api.ts                       # API request/response types
│
└── utils/
    ├── fileValidation.ts            # Validate uploaded files
    ├── markerDefaults.ts            # Default marker positions
    └── formatters.ts                # Time formatting, etc.
```

#### 1.3 Marker System Specification

The marker system mimics Mixamo's approach. Users must place **7 markers** on the character:

| Marker ID | Name | Color | Description |
|-----------|------|-------|-------------|
| `chin` | Chin | #FF0000 | Bottom of the face/jaw |
| `wrist_l` | Left Wrist | #00FF00 | Left hand wrist joint |
| `wrist_r` | Right Wrist | #0000FF | Right hand wrist joint |
| `elbow_l` | Left Elbow | #FFFF00 | Left arm elbow joint |
| `elbow_r` | Right Elbow | #FF00FF | Right arm elbow joint |
| `knee_l` | Left Knee | #00FFFF | Left leg knee joint |
| `knee_r` | Right Knee | #FFA500 | Right leg knee joint |
| `groin` | Groin/Pelvis | #FFFFFF | Center of pelvis/hips |

**Marker Placement Flow:**
1. User uploads model → Model displayed in viewport
2. System prompts: "Click on the character's **chin**"
3. User clicks on model → Raycaster finds intersection point
4. Red sphere appears at click position
5. Repeat for each marker in sequence
6. All 8 markers placed → "Auto-Rig" button enabled
7. User clicks "Auto-Rig" → Markers sent to backend

**Marker Editing:**
- Click existing marker to select it
- Drag to reposition
- Right-click to delete and re-place
- "Reset All" button to start over

#### 1.4 Animation Library UI

```
┌─────────────────────────────────────────┐
│ 🔍 Search animations...                 │
├─────────────────────────────────────────┤
│ [All] [Locomotion] [Combat] [Social]    │
├─────────────────────────────────────────┤
│ ┌─────────┐ ┌─────────┐ ┌─────────┐    │
│ │  🏃     │ │  🚶     │ │  🦘     │    │
│ │  Run    │ │  Walk   │ │  Jump   │    │
│ │  [+]    │ │  [+]    │ │  [+]    │    │
│ └─────────┘ └─────────┘ └─────────┘    │
│ ┌─────────┐ ┌─────────┐ ┌─────────┐    │
│ │  💃     │ │  👋     │ │  🧘     │    │
│ │  Dance  │ │  Wave   │ │  Idle   │    │
│ │  [+]    │ │  [+]    │ │  [+]    │    │
│ └─────────┘ └─────────┘ └─────────┘    │
└─────────────────────────────────────────┘
```

- Hover on card → Shows animated GIF preview (pre-rendered)
- Click card → Applies animation to character in viewport
- Click [+] → Adds to "My Animations" list

#### 1.5 Playback Controls

```
┌─────────────────────────────────────────────────────────────┐
│  [⏮] [⏪] [▶️/⏸️] [⏩] [⏭]    ════●══════════════  0:24/1:30  │
│                                                             │
│  Speed: [0.5x] [1x] [2x]                    [🔁 Loop: ON]   │
└─────────────────────────────────────────────────────────────┘
```

- ⏮ Jump to start
- ⏪ Previous frame
- ▶️/⏸️ Play/Pause toggle
- ⏩ Next frame
- ⏭ Jump to end
- Slider: Scrub through animation
- Loop toggle: Enable/disable looping

#### 1.6 Export Panel

```
┌─────────────────────────────────────────┐
│           EXPORT MODEL                  │
├─────────────────────────────────────────┤
│ Format:                                 │
│ ○ GLB (recommended for web)             │
│ ● FBX (recommended for Unity/Unreal)    │
├─────────────────────────────────────────┤
│ Include Animations:                     │
│ ☑ Idle                                  │
│ ☑ Walk                                  │
│ ☐ Run                                   │
│ ☑ Jump                                  │
│                                         │
│ [Select All] [Select None]              │
├─────────────────────────────────────────┤
│ ☐ Export without animations             │
├─────────────────────────────────────────┤
│        [⬇️ DOWNLOAD]                    │
└─────────────────────────────────────────┘
```

---

### 2. Backend API Specification

#### 2.1 API Endpoints

##### POST /api/upload
Upload a 3D model file for processing.

**Request:**
```
Content-Type: multipart/form-data

file: <binary> (OBJ, FBX, GLB, GLTF)
```

**Response:**
```json
{
  "success": true,
  "model_id": "uuid-string",
  "preview_url": "/api/models/{model_id}/preview.glb",
  "original_format": "obj",
  "vertex_count": 12500,
  "has_skeleton": false
}
```

##### POST /api/rig
Process uploaded model with marker data.

**Request:**
```json
{
  "model_id": "uuid-string",
  "markers": {
    "chin": [0.0, 1.75, 0.05],
    "groin": [0.0, 0.95, 0.0],
    "wrist_l": [-0.65, 1.1, 0.0],
    "wrist_r": [0.65, 1.1, 0.0],
    "elbow_l": [-0.45, 1.3, -0.05],
    "elbow_r": [0.45, 1.3, -0.05],
    "knee_l": [-0.1, 0.5, 0.02],
    "knee_r": [0.1, 0.5, 0.02]
  }
}
```

**Response:**
```json
{
  "success": true,
  "rigged_model_url": "/api/models/{model_id}/rigged.glb",
  "skeleton_info": {
    "bone_count": 52,
    "rig_type": "rigify_human"
  },
  "processing_time_ms": 45000
}
```

##### GET /api/animations
List all available animations in the library.

**Response:**
```json
{
  "animations": [
    {
      "id": "walk_01",
      "name": "Walk",
      "category": "locomotion",
      "duration_seconds": 1.0,
      "thumbnail_url": "/api/animations/walk_01/thumbnail.gif",
      "preview_url": "/api/animations/walk_01/preview.glb"
    },
    {
      "id": "run_01",
      "name": "Run",
      "category": "locomotion",
      "duration_seconds": 0.8,
      "thumbnail_url": "/api/animations/run_01/thumbnail.gif",
      "preview_url": "/api/animations/run_01/preview.glb"
    }
  ],
  "categories": ["locomotion", "combat", "social", "misc"]
}
```

##### POST /api/apply-animation
Apply an animation to the rigged model for preview.

**Request:**
```json
{
  "model_id": "uuid-string",
  "animation_id": "walk_01"
}
```

**Response:**
```json
{
  "success": true,
  "animated_model_url": "/api/models/{model_id}/animated/{animation_id}.glb"
}
```

##### POST /api/export
Export the rigged model with selected animations.

**Request:**
```json
{
  "model_id": "uuid-string",
  "format": "fbx",
  "animations": ["walk_01", "run_01", "idle_01"],
  "include_rig_controls": false
}
```

**Response:**
```json
{
  "success": true,
  "download_url": "/api/downloads/{export_id}.fbx",
  "file_size_bytes": 2450000,
  "expires_at": "2024-01-15T12:00:00Z"
}
```

##### GET /api/models/{model_id}/status
Check processing status for long operations.

**Response:**
```json
{
  "model_id": "uuid-string",
  "status": "processing",
  "stage": "rigging",
  "progress": 65,
  "message": "Generating skeleton weights..."
}
```

#### 2.2 Backend Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # FastAPI app initialization
│   ├── config.py                  # Environment configuration
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   │   ├── __init__.py
│   │   │   ├── upload.py          # /api/upload endpoint
│   │   │   ├── rig.py             # /api/rig endpoint
│   │   │   ├── animations.py      # /api/animations endpoints
│   │   │   └── export.py          # /api/export endpoint
│   │   │
│   │   └── dependencies.py        # Shared dependencies
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── blender_service.py     # Blender subprocess manager
│   │   ├── model_service.py       # Model processing logic
│   │   ├── animation_service.py   # Animation retargeting
│   │   └── export_service.py      # Export processing
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── schemas.py             # Pydantic models
│   │   └── enums.py               # Status enums, formats, etc.
│   │
│   └── utils/
│       ├── __init__.py
│       ├── file_utils.py          # File handling utilities
│       └── validation.py          # Input validation
│
├── blender_scripts/
│   ├── auto_rig.py                # Main rigging script
│   ├── apply_animation.py         # Animation retargeting script
│   ├── export_model.py            # Export with animations
│   ├── generate_preview.py        # Generate GLB preview
│   └── utils/
│       ├── __init__.py
│       ├── marker_fitting.py      # Marker-to-skeleton fitting
│       ├── rigify_utils.py        # Rigify helper functions
│       └── retarget_utils.py      # Animation retargeting
│
├── data/
│   ├── animations/                # Animation library
│   │   ├── locomotion/
│   │   │   ├── walk_01.bvh
│   │   │   ├── walk_01.json       # Metadata
│   │   │   ├── walk_01_thumb.gif
│   │   │   ├── run_01.bvh
│   │   │   └── ...
│   │   ├── combat/
│   │   ├── social/
│   │   └── misc/
│   │
│   └── templates/
│       └── human_metarig.blend    # Base Rigify metarig
│
├── tests/
│   ├── __init__.py
│   ├── test_upload.py
│   ├── test_rig.py
│   └── test_export.py
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

### 3. Blender Scripts Specification

#### 3.1 auto_rig.py - Main Rigging Script

```python
"""
auto_rig.py - Marker-based automatic rigging with Rigify

Usage:
    blender --background --python auto_rig.py -- \
        --input /path/to/model.obj \
        --markers /path/to/markers.json \
        --output /path/to/rigged.glb

Markers JSON format:
{
    "chin": [x, y, z],
    "groin": [x, y, z],
    "wrist_l": [x, y, z],
    "wrist_r": [x, y, z],
    "elbow_l": [x, y, z],
    "elbow_r": [x, y, z],
    "knee_l": [x, y, z],
    "knee_r": [x, y, z]
}
"""

import bpy
import sys
import json
import argparse
from mathutils import Vector
from pathlib import Path


# Required markers for humanoid rigging
REQUIRED_MARKERS = [
    'chin', 'groin', 
    'wrist_l', 'wrist_r',
    'elbow_l', 'elbow_r', 
    'knee_l', 'knee_r'
]

# Mapping from markers to Rigify metarig bones
MARKER_TO_BONE = {
    'chin': 'spine.006',
    'groin': 'spine',
    'wrist_l': 'hand.L',
    'wrist_r': 'hand.R',
    'elbow_l': 'forearm.L',
    'elbow_r': 'forearm.R',
    'knee_l': 'shin.L',
    'knee_r': 'shin.R',
}


def clear_scene():
    """Remove all objects from the scene."""
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Clear orphan data
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.armatures:
        if block.users == 0:
            bpy.data.armatures.remove(block)


def import_model(filepath: str) -> bpy.types.Object:
    """Import 3D model based on file extension."""
    filepath = Path(filepath)
    ext = filepath.suffix.lower()
    
    if ext == '.obj':
        bpy.ops.wm.obj_import(filepath=str(filepath))
    elif ext == '.fbx':
        bpy.ops.import_scene.fbx(filepath=str(filepath))
    elif ext in ['.glb', '.gltf']:
        bpy.ops.import_scene.gltf(filepath=str(filepath))
    else:
        raise ValueError(f"Unsupported format: {ext}")
    
    # Get imported mesh
    mesh_objects = [obj for obj in bpy.context.selected_objects 
                    if obj.type == 'MESH']
    
    if not mesh_objects:
        raise ValueError("No mesh found in imported file")
    
    # Join multiple meshes if needed
    if len(mesh_objects) > 1:
        bpy.context.view_layer.objects.active = mesh_objects[0]
        bpy.ops.object.select_all(action='DESELECT')
        for obj in mesh_objects:
            obj.select_set(True)
        bpy.ops.object.join()
    
    mesh = bpy.context.active_object
    
    # Center and normalize
    bpy.ops.object.origin_set(type='ORIGIN_CENTER_OF_VOLUME')
    mesh.location = (0, 0, 0)
    
    return mesh


def validate_markers(markers: dict) -> bool:
    """Validate that all required markers are present."""
    for marker in REQUIRED_MARKERS:
        if marker not in markers:
            raise ValueError(f"Missing required marker: {marker}")
        if len(markers[marker]) != 3:
            raise ValueError(f"Invalid coordinates for marker: {marker}")
    return True


def calculate_character_scale(markers: dict) -> float:
    """Calculate scale factor based on marker positions."""
    chin = Vector(markers['chin'])
    groin = Vector(markers['groin'])
    
    # Height from groin to chin
    height = (chin - groin).length
    
    # Standard metarig height is approximately 1.5 units
    standard_height = 1.5
    
    return height / standard_height


def create_metarig() -> bpy.types.Object:
    """Create a Rigify human metarig."""
    bpy.ops.object.armature_human_metarig_add()
    metarig = bpy.context.active_object
    metarig.name = "metarig"
    return metarig


def fit_metarig_to_markers(metarig: bpy.types.Object, markers: dict):
    """
    Adjust metarig bones to match marker positions.
    
    This is the core algorithm that makes the magic happen.
    It interpolates the full skeleton from just 8 marker points.
    """
    scale = calculate_character_scale(markers)
    
    bpy.context.view_layer.objects.active = metarig
    bpy.ops.object.mode_set(mode='EDIT')
    
    bones = metarig.data.edit_bones
    
    # Scale entire metarig first
    for bone in bones:
        bone.head *= scale
        bone.tail *= scale
    
    # Convert markers to Vectors
    m = {k: Vector(v) for k, v in markers.items()}
    
    # === SPINE CHAIN ===
    # Interpolate spine from groin to chin
    spine_bones = ['spine', 'spine.001', 'spine.002', 'spine.003', 
                   'spine.004', 'spine.005', 'spine.006']
    
    for i, bone_name in enumerate(spine_bones):
        if bone_name in bones:
            t = i / (len(spine_bones) - 1)
            target = m['groin'].lerp(m['chin'], t)
            
            # Offset slightly back for natural spine curve
            curve_offset = Vector((0, -0.02 * scale * (1 - abs(2*t - 1)), 0))
            bones[bone_name].head = target + curve_offset
    
    # Fix spine connections
    for i in range(len(spine_bones) - 1):
        if spine_bones[i] in bones and spine_bones[i+1] in bones:
            bones[spine_bones[i]].tail = bones[spine_bones[i+1]].head
    
    # === LEFT ARM ===
    # Calculate shoulder position (interpolate from chin/groin and wrist)
    shoulder_l_pos = m['chin'].lerp(m['groin'], 0.15)
    shoulder_l_pos.x = m['elbow_l'].x * 0.4  # Offset toward arm
    
    if 'shoulder.L' in bones:
        bones['shoulder.L'].head = shoulder_l_pos
    
    if 'upper_arm.L' in bones:
        bones['upper_arm.L'].head = shoulder_l_pos + Vector((-0.1 * scale, 0, 0))
        bones['upper_arm.L'].tail = m['elbow_l']
    
    if 'forearm.L' in bones:
        bones['forearm.L'].head = m['elbow_l']
        bones['forearm.L'].tail = m['wrist_l']
    
    if 'hand.L' in bones:
        bones['hand.L'].head = m['wrist_l']
        # Extend hand in same direction as forearm
        hand_dir = (m['wrist_l'] - m['elbow_l']).normalized()
        bones['hand.L'].tail = m['wrist_l'] + hand_dir * 0.1 * scale
    
    # === RIGHT ARM === (mirror of left)
    shoulder_r_pos = m['chin'].lerp(m['groin'], 0.15)
    shoulder_r_pos.x = m['elbow_r'].x * 0.4
    
    if 'shoulder.R' in bones:
        bones['shoulder.R'].head = shoulder_r_pos
    
    if 'upper_arm.R' in bones:
        bones['upper_arm.R'].head = shoulder_r_pos + Vector((0.1 * scale, 0, 0))
        bones['upper_arm.R'].tail = m['elbow_r']
    
    if 'forearm.R' in bones:
        bones['forearm.R'].head = m['elbow_r']
        bones['forearm.R'].tail = m['wrist_r']
    
    if 'hand.R' in bones:
        bones['hand.R'].head = m['wrist_r']
        hand_dir = (m['wrist_r'] - m['elbow_r']).normalized()
        bones['hand.R'].tail = m['wrist_r'] + hand_dir * 0.1 * scale
    
    # === LEFT LEG ===
    hip_l_pos = m['groin'].copy()
    hip_l_pos.x = m['knee_l'].x
    
    if 'thigh.L' in bones:
        bones['thigh.L'].head = hip_l_pos
        bones['thigh.L'].tail = m['knee_l']
    
    if 'shin.L' in bones:
        bones['shin.L'].head = m['knee_l']
        # Estimate ankle position
        ankle_l = m['knee_l'].copy()
        ankle_l.z = 0.05 * scale  # Just above ground
        bones['shin.L'].tail = ankle_l
    
    if 'foot.L' in bones:
        bones['foot.L'].head = bones['shin.L'].tail
        bones['foot.L'].tail = bones['foot.L'].head + Vector((0, -0.15 * scale, 0))
    
    # === RIGHT LEG === (mirror of left)
    hip_r_pos = m['groin'].copy()
    hip_r_pos.x = m['knee_r'].x
    
    if 'thigh.R' in bones:
        bones['thigh.R'].head = hip_r_pos
        bones['thigh.R'].tail = m['knee_r']
    
    if 'shin.R' in bones:
        bones['shin.R'].head = m['knee_r']
        ankle_r = m['knee_r'].copy()
        ankle_r.z = 0.05 * scale
        bones['shin.R'].tail = ankle_r
    
    if 'foot.R' in bones:
        bones['foot.R'].head = bones['shin.R'].tail
        bones['foot.R'].tail = bones['foot.R'].head + Vector((0, -0.15 * scale, 0))
    
    # === HEAD ===
    if 'spine.006' in bones:
        # Head bone extends up from chin
        head_dir = (m['chin'] - m['groin']).normalized()
        if 'spine.006' in bones:
            bones['spine.006'].tail = m['chin'] + head_dir * 0.2 * scale
    
    bpy.ops.object.mode_set(mode='OBJECT')


def generate_rig(metarig: bpy.types.Object) -> bpy.types.Object:
    """Generate final rig from metarig using Rigify."""
    bpy.context.view_layer.objects.active = metarig
    
    # Generate Rigify rig
    bpy.ops.pose.rigify_generate()
    
    # Get generated rig
    rig = bpy.data.objects.get('rig')
    if not rig:
        raise RuntimeError("Rigify failed to generate rig")
    
    return rig


def bind_mesh_to_rig(mesh: bpy.types.Object, rig: bpy.types.Object):
    """Bind mesh to rig with automatic weights."""
    bpy.ops.object.select_all(action='DESELECT')
    
    mesh.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    
    # Parent with automatic weights
    bpy.ops.object.parent_set(type='ARMATURE_AUTO')


def cleanup_for_export(rig: bpy.types.Object, mesh: bpy.types.Object):
    """Clean up scene for export, removing unnecessary objects."""
    # Remove metarig
    metarig = bpy.data.objects.get('metarig')
    if metarig:
        bpy.data.objects.remove(metarig, do_unlink=True)
    
    # Remove widget objects (WGT-*)
    for obj in bpy.data.objects:
        if obj.name.startswith('WGT-'):
            bpy.data.objects.remove(obj, do_unlink=True)
    
    # Keep only deformation bones visible
    # (This is handled during export)


def export_model(filepath: str, rig: bpy.types.Object, mesh: bpy.types.Object):
    """Export rigged model to GLB format."""
    bpy.ops.object.select_all(action='DESELECT')
    
    mesh.select_set(True)
    rig.select_set(True)
    
    filepath = Path(filepath)
    
    if filepath.suffix.lower() == '.glb':
        bpy.ops.export_scene.gltf(
            filepath=str(filepath),
            export_format='GLB',
            use_selection=True,
            export_skins=True,
            export_all_influences=True,
            export_def_bones=True
        )
    elif filepath.suffix.lower() == '.fbx':
        bpy.ops.export_scene.fbx(
            filepath=str(filepath),
            use_selection=True,
            add_leaf_bones=False,
            bake_anim=False
        )


def main():
    # Parse arguments after "--"
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    parser = argparse.ArgumentParser(description='Auto-rig a 3D model')
    parser.add_argument('--input', required=True, help='Input model file')
    parser.add_argument('--markers', required=True, help='Markers JSON file')
    parser.add_argument('--output', required=True, help='Output file path')
    
    args = parser.parse_args(argv)
    
    # Load markers
    with open(args.markers, 'r') as f:
        markers = json.load(f)
    
    # Validate
    validate_markers(markers)
    
    # Process
    clear_scene()
    mesh = import_model(args.input)
    metarig = create_metarig()
    fit_metarig_to_markers(metarig, markers)
    rig = generate_rig(metarig)
    bind_mesh_to_rig(mesh, rig)
    cleanup_for_export(rig, mesh)
    export_model(args.output, rig, mesh)
    
    print(f"Successfully exported rigged model to: {args.output}")


if __name__ == "__main__":
    main()
```

#### 3.2 apply_animation.py - Animation Retargeting

```python
"""
apply_animation.py - Retarget animation to rigged character

Usage:
    blender --background --python apply_animation.py -- \
        --model /path/to/rigged.glb \
        --animation /path/to/animation.bvh \
        --output /path/to/animated.glb
"""

import bpy
import sys
import argparse
from pathlib import Path


# Bone mapping from BVH standard to Rigify deform bones
BVH_TO_RIGIFY = {
    'Hips': 'DEF-spine',
    'Spine': 'DEF-spine.001',
    'Spine1': 'DEF-spine.002',
    'Spine2': 'DEF-spine.003',
    'Neck': 'DEF-spine.004',
    'Head': 'DEF-spine.006',
    
    'LeftShoulder': 'DEF-shoulder.L',
    'LeftArm': 'DEF-upper_arm.L',
    'LeftForeArm': 'DEF-forearm.L',
    'LeftHand': 'DEF-hand.L',
    
    'RightShoulder': 'DEF-shoulder.R',
    'RightArm': 'DEF-upper_arm.R',
    'RightForeArm': 'DEF-forearm.R',
    'RightHand': 'DEF-hand.R',
    
    'LeftUpLeg': 'DEF-thigh.L',
    'LeftLeg': 'DEF-shin.L',
    'LeftFoot': 'DEF-foot.L',
    'LeftToeBase': 'DEF-toe.L',
    
    'RightUpLeg': 'DEF-thigh.R',
    'RightLeg': 'DEF-shin.R',
    'RightFoot': 'DEF-foot.R',
    'RightToeBase': 'DEF-toe.R',
}


def import_rigged_model(filepath: str) -> tuple:
    """Import rigged model and return (mesh, armature)."""
    filepath = Path(filepath)
    
    if filepath.suffix.lower() in ['.glb', '.gltf']:
        bpy.ops.import_scene.gltf(filepath=str(filepath))
    elif filepath.suffix.lower() == '.fbx':
        bpy.ops.import_scene.fbx(filepath=str(filepath))
    
    armature = None
    mesh = None
    
    for obj in bpy.context.selected_objects:
        if obj.type == 'ARMATURE':
            armature = obj
        elif obj.type == 'MESH':
            mesh = obj
    
    if not armature:
        raise ValueError("No armature found in model")
    
    return mesh, armature


def import_animation(filepath: str) -> bpy.types.Object:
    """Import BVH or FBX animation."""
    filepath = Path(filepath)
    
    if filepath.suffix.lower() == '.bvh':
        bpy.ops.import_anim.bvh(
            filepath=str(filepath),
            use_fps_scale=True,
            update_scene_fps=False
        )
    elif filepath.suffix.lower() == '.fbx':
        bpy.ops.import_scene.fbx(
            filepath=str(filepath),
            use_anim=True
        )
    
    # Get imported armature
    for obj in bpy.context.selected_objects:
        if obj.type == 'ARMATURE':
            return obj
    
    raise ValueError("No armature found in animation file")


def retarget_animation(source_armature: bpy.types.Object, 
                       target_armature: bpy.types.Object,
                       animation_name: str):
    """
    Retarget animation from source armature to target armature.
    
    This uses constraint-based retargeting with the bone mapping.
    """
    bpy.context.view_layer.objects.active = target_armature
    bpy.ops.object.mode_set(mode='POSE')
    
    # Get or create action for target
    if target_armature.animation_data is None:
        target_armature.animation_data_create()
    
    action = bpy.data.actions.new(name=animation_name)
    target_armature.animation_data.action = action
    
    # Get source action
    if source_armature.animation_data and source_armature.animation_data.action:
        source_action = source_armature.animation_data.action
    else:
        raise ValueError("Source armature has no animation")
    
    # Get frame range
    frame_start = int(source_action.frame_range[0])
    frame_end = int(source_action.frame_range[1])
    
    # For each frame, copy transforms
    for frame in range(frame_start, frame_end + 1):
        bpy.context.scene.frame_set(frame)
        
        for bvh_bone, rigify_bone in BVH_TO_RIGIFY.items():
            # Find source bone
            source_bone = source_armature.pose.bones.get(bvh_bone)
            if not source_bone:
                continue
            
            # Find target bone
            target_bone = target_armature.pose.bones.get(rigify_bone)
            if not target_bone:
                # Try without DEF- prefix
                alt_name = rigify_bone.replace('DEF-', '')
                target_bone = target_armature.pose.bones.get(alt_name)
            
            if not target_bone:
                continue
            
            # Copy rotation
            target_bone.rotation_quaternion = source_bone.rotation_quaternion
            target_bone.keyframe_insert(data_path='rotation_quaternion', frame=frame)
            
            # Copy location for root bone only
            if bvh_bone == 'Hips':
                target_bone.location = source_bone.location
                target_bone.keyframe_insert(data_path='location', frame=frame)
    
    bpy.ops.object.mode_set(mode='OBJECT')
    
    # Delete source armature
    bpy.data.objects.remove(source_armature, do_unlink=True)
    
    return action


def export_animated_model(filepath: str, mesh: bpy.types.Object, 
                          armature: bpy.types.Object):
    """Export model with animation."""
    bpy.ops.object.select_all(action='DESELECT')
    
    mesh.select_set(True)
    armature.select_set(True)
    
    filepath = Path(filepath)
    
    if filepath.suffix.lower() == '.glb':
        bpy.ops.export_scene.gltf(
            filepath=str(filepath),
            export_format='GLB',
            use_selection=True,
            export_skins=True,
            export_animations=True,
            export_all_influences=True
        )
    elif filepath.suffix.lower() == '.fbx':
        bpy.ops.export_scene.fbx(
            filepath=str(filepath),
            use_selection=True,
            bake_anim=True,
            bake_anim_use_all_actions=True
        )


def main():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True)
    parser.add_argument('--animation', required=True)
    parser.add_argument('--output', required=True)
    parser.add_argument('--name', default='Animation')
    
    args = parser.parse_args(argv)
    
    # Clear scene
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    # Import and process
    mesh, armature = import_rigged_model(args.model)
    source_anim = import_animation(args.animation)
    retarget_animation(source_anim, armature, args.name)
    export_animated_model(args.output, mesh, armature)
    
    print(f"Successfully exported animated model to: {args.output}")


if __name__ == "__main__":
    main()
```

#### 3.3 export_model.py - Multi-Animation Export

```python
"""
export_model.py - Export model with multiple animations

Usage:
    blender --background --python export_model.py -- \
        --model /path/to/rigged.glb \
        --animations walk.bvh,run.bvh,idle.bvh \
        --names Walk,Run,Idle \
        --format fbx \
        --output /path/to/final.fbx
"""

import bpy
import sys
import argparse
from pathlib import Path


def import_model(filepath: str) -> tuple:
    """Import model, return (mesh, armature)."""
    filepath = Path(filepath)
    
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete()
    
    if filepath.suffix.lower() in ['.glb', '.gltf']:
        bpy.ops.import_scene.gltf(filepath=str(filepath))
    elif filepath.suffix.lower() == '.fbx':
        bpy.ops.import_scene.fbx(filepath=str(filepath))
    
    armature = None
    mesh = None
    
    for obj in bpy.data.objects:
        if obj.type == 'ARMATURE':
            armature = obj
        elif obj.type == 'MESH':
            mesh = obj
    
    return mesh, armature


def import_and_retarget_animation(armature: bpy.types.Object,
                                   anim_path: str,
                                   anim_name: str) -> bpy.types.Action:
    """Import animation and retarget to armature."""
    # This is a simplified version - full implementation would use
    # the retargeting logic from apply_animation.py
    
    filepath = Path(anim_path)
    
    if filepath.suffix.lower() == '.bvh':
        bpy.ops.import_anim.bvh(filepath=str(filepath))
    
    # Get imported armature
    source = None
    for obj in bpy.context.selected_objects:
        if obj.type == 'ARMATURE' and obj != armature:
            source = obj
            break
    
    if source and source.animation_data:
        action = source.animation_data.action.copy()
        action.name = anim_name
        
        # Remove source armature
        bpy.data.objects.remove(source, do_unlink=True)
        
        return action
    
    return None


def export_with_animations(filepath: str, 
                           mesh: bpy.types.Object,
                           armature: bpy.types.Object,
                           actions: list,
                           format: str):
    """Export model with all animations embedded."""
    
    # Ensure all actions are linked
    if not armature.animation_data:
        armature.animation_data_create()
    
    # Create NLA tracks for each action
    for action in actions:
        if action:
            track = armature.animation_data.nla_tracks.new()
            track.name = action.name
            track.strips.new(action.name, int(action.frame_range[0]), action)
    
    # Select for export
    bpy.ops.object.select_all(action='DESELECT')
    mesh.select_set(True)
    armature.select_set(True)
    
    filepath = Path(filepath)
    
    if format.lower() == 'glb':
        bpy.ops.export_scene.gltf(
            filepath=str(filepath),
            export_format='GLB',
            use_selection=True,
            export_skins=True,
            export_animations=True,
            export_nla_strips=True,
            export_all_influences=True
        )
    elif format.lower() == 'fbx':
        bpy.ops.export_scene.fbx(
            filepath=str(filepath),
            use_selection=True,
            bake_anim=True,
            bake_anim_use_nla_strips=True,
            bake_anim_use_all_actions=True,
            add_leaf_bones=False
        )


def main():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []
    
    parser = argparse.ArgumentParser()
    parser.add_argument('--model', required=True)
    parser.add_argument('--animations', required=True, help='Comma-separated paths')
    parser.add_argument('--names', required=True, help='Comma-separated names')
    parser.add_argument('--format', choices=['fbx', 'glb'], default='glb')
    parser.add_argument('--output', required=True)
    
    args = parser.parse_args(argv)
    
    anim_paths = args.animations.split(',')
    anim_names = args.names.split(',')
    
    if len(anim_paths) != len(anim_names):
        raise ValueError("Number of animations must match number of names")
    
    mesh, armature = import_model(args.model)
    
    actions = []
    for path, name in zip(anim_paths, anim_names):
        action = import_and_retarget_animation(armature, path.strip(), name.strip())
        if action:
            actions.append(action)
    
    export_with_animations(args.output, mesh, armature, actions, args.format)
    
    print(f"Exported {len(actions)} animations to: {args.output}")


if __name__ == "__main__":
    main()
```

---

### 4. Animation Library

The project requires a library of pre-made animations. Here are recommended free sources:

#### 4.1 Animation Sources (Creative Commons / Free)

| Source | URL | Format | Notes |
|--------|-----|--------|-------|
| Mixamo | mixamo.com | FBX | Download manually, check license |
| CMU Motion Capture | mocap.cs.cmu.edu | BVH | Public domain |
| Bandai Namco | github.com/BandaiNamcoResearchInc | BVH | CC-BY-4.0 |
| Rokoko | rokoko.com/free-mocap | FBX/BVH | Free starter pack |
| ActorCore | actorcore.reallusion.com | Various | Some free options |

#### 4.2 Required Animation Set (Minimum)

Create these folders and populate with animations:

```
data/animations/
├── locomotion/
│   ├── idle_01.bvh          # Standing idle
│   ├── idle_02.bvh          # Idle variation (shifting weight)
│   ├── walk_01.bvh          # Walk cycle
│   ├── walk_02.bvh          # Walk variation
│   ├── run_01.bvh           # Run cycle
│   ├── sprint_01.bvh        # Fast run
│   ├── jump_01.bvh          # Jump in place
│   ├── jump_forward_01.bvh  # Running jump
│   ├── crouch_01.bvh        # Crouch idle
│   └── crouch_walk_01.bvh   # Crouch walk
│
├── combat/
│   ├── punch_01.bvh         # Right punch
│   ├── punch_02.bvh         # Left punch
│   ├── kick_01.bvh          # Right kick
│   ├── block_01.bvh         # Blocking pose
│   ├── hit_react_01.bvh     # Getting hit reaction
│   └── death_01.bvh         # Death/fall animation
│
├── social/
│   ├── wave_01.bvh          # Waving hello
│   ├── bow_01.bvh           # Bowing
│   ├── clap_01.bvh          # Clapping
│   ├── dance_01.bvh         # Simple dance
│   ├── sit_01.bvh           # Sitting down
│   └── talk_01.bvh          # Talking gesture
│
└── misc/
    ├── pick_up_01.bvh       # Picking up item
    ├── push_01.bvh          # Pushing
    ├── pull_01.bvh          # Pulling
    └── climb_01.bvh         # Climbing
```

#### 4.3 Animation Metadata

Each animation needs a JSON metadata file:

```json
{
  "id": "walk_01",
  "name": "Walk",
  "category": "locomotion",
  "duration_seconds": 1.0,
  "fps": 30,
  "loop": true,
  "root_motion": true,
  "tags": ["walk", "locomotion", "cycle"],
  "description": "Standard walk cycle, loops seamlessly"
}
```

---

### 5. Infrastructure Setup

#### 5.1 Oracle Cloud Setup

**Free Tier Resources:**
- 4 ARM OCPUs (Ampere A1)
- 24 GB RAM
- 200 GB Block Storage
- 10 TB/month Outbound Data Transfer

**Instance Configuration:**

```bash
# Create instance via OCI CLI
oci compute instance launch \
    --availability-domain "AD-1" \
    --compartment-id $COMPARTMENT_ID \
    --shape "VM.Standard.A1.Flex" \
    --shape-config '{"ocpus": 4, "memoryInGBs": 24}' \
    --image-id $UBUNTU_ARM_IMAGE_ID \
    --subnet-id $SUBNET_ID \
    --assign-public-ip true
```

#### 5.2 Docker Configuration

**docker-compose.yml:**

```yaml
version: '3.8'

services:
  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "3000:3000"
    environment:
      - REACT_APP_API_URL=http://localhost:8000
    depends_on:
      - backend

  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    volumes:
      - ./data:/app/data
      - blender-cache:/tmp/blender
    environment:
      - BLENDER_PATH=/opt/blender/blender
      - DATA_DIR=/app/data
      - MAX_UPLOAD_SIZE=52428800  # 50MB
    deploy:
      resources:
        limits:
          memory: 16G
        reservations:
          memory: 8G

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./certbot/conf:/etc/letsencrypt
    depends_on:
      - frontend
      - backend

volumes:
  blender-cache:
```

**Backend Dockerfile:**

```dockerfile
FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive
ENV BLENDER_VERSION=4.0.2

# Install system dependencies
RUN apt-get update && apt-get install -y \
    wget \
    xz-utils \
    libxi6 \
    libxxf86vm1 \
    libxfixes3 \
    libxrender1 \
    libgl1-mesa-glx \
    libglu1-mesa \
    python3 \
    python3-pip \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

# Download and install Blender for ARM64
RUN wget -q https://download.blender.org/release/Blender4.0/blender-${BLENDER_VERSION}-linux-arm64.tar.xz \
    && tar -xf blender-${BLENDER_VERSION}-linux-arm64.tar.xz \
    && mv blender-${BLENDER_VERSION}-linux-arm64 /opt/blender \
    && rm blender-${BLENDER_VERSION}-linux-arm64.tar.xz \
    && ln -s /opt/blender/blender /usr/local/bin/blender

# Set up Python environment
WORKDIR /app

COPY requirements.txt .
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy application code
COPY app/ ./app/
COPY blender_scripts/ ./blender_scripts/

# Create data directories
RUN mkdir -p /app/data/uploads \
    /app/data/processed \
    /app/data/animations \
    /app/data/exports

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Frontend Dockerfile:**

```dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm ci

COPY . .
RUN npm run build

FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 3000

CMD ["nginx", "-g", "daemon off;"]
```

#### 5.3 Nginx Configuration

```nginx
upstream frontend {
    server frontend:3000;
}

upstream backend {
    server backend:8000;
}

server {
    listen 80;
    server_name openrig.example.com;
    
    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name openrig.example.com;
    
    ssl_certificate /etc/letsencrypt/live/openrig.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/openrig.example.com/privkey.pem;
    
    client_max_body_size 50M;
    
    # Frontend
    location / {
        proxy_pass http://frontend;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
    }
    
    # Backend API
    location /api {
        proxy_pass http://backend;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_read_timeout 300s;  # Long timeout for rigging
    }
    
    # Static files (animations, processed models)
    location /static {
        alias /app/data;
        expires 1d;
        add_header Cache-Control "public, immutable";
    }
}
```

---

### 6. Development Workflow

#### 6.1 Getting Started

```bash
# Clone repository
git clone https://github.com/your-username/openrig.git
cd openrig

# Start development environment
docker-compose -f docker-compose.dev.yml up

# Frontend runs at http://localhost:3000
# Backend runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

#### 6.2 Development Phases

**Phase 1: Core Infrastructure (Week 1-2)**
- [ ] Set up project structure
- [ ] Configure Docker environment
- [ ] Implement file upload endpoint
- [ ] Test Blender headless execution
- [ ] Basic GLB import/export

**Phase 2: Rigging System (Week 3-4)**
- [ ] Implement marker placement UI
- [ ] Develop auto_rig.py script
- [ ] Integrate Rigify generation
- [ ] Automatic weight painting
- [ ] Preview rigged model

**Phase 3: Animation System (Week 5-6)**
- [ ] Build animation library structure
- [ ] Implement animation browsing UI
- [ ] Develop retargeting system
- [ ] Animation preview in viewer
- [ ] Playback controls

**Phase 4: Export System (Week 7-8)**
- [ ] Multi-animation export
- [ ] FBX export with Blender
- [ ] GLB export optimization
- [ ] Download management
- [ ] Error handling

**Phase 5: Polish & Deploy (Week 9-10)**
- [ ] UI/UX improvements
- [ ] Performance optimization
- [ ] Oracle Cloud deployment
- [ ] SSL/HTTPS setup
- [ ] Documentation

#### 6.3 Testing Strategy

```bash
# Backend tests
cd backend
pytest tests/ -v

# Frontend tests
cd frontend
npm test

# E2E tests
npm run test:e2e

# Test Blender scripts locally
blender --background --python blender_scripts/auto_rig.py -- \
    --input test_models/human.obj \
    --markers test_data/markers.json \
    --output output/rigged.glb
```

---

### 7. UI/UX Design Guidelines

#### 7.1 Color Scheme

```css
:root {
  /* Primary */
  --primary-50: #f0f9ff;
  --primary-500: #0ea5e9;
  --primary-600: #0284c7;
  --primary-700: #0369a1;
  
  /* Background */
  --bg-dark: #1a1a2e;
  --bg-card: #16213e;
  --bg-input: #0f3460;
  
  /* Accent */
  --accent-success: #10b981;
  --accent-warning: #f59e0b;
  --accent-error: #ef4444;
  
  /* Text */
  --text-primary: #f8fafc;
  --text-secondary: #94a3b8;
  --text-muted: #64748b;
}
```

#### 7.2 Component Styling

- Dark theme (like Mixamo)
- Rounded corners (8px default)
- Subtle shadows and gradients
- Smooth transitions (200ms)
- Clear hover/active states
- Loading skeletons for async content

#### 7.3 Responsive Breakpoints

```css
/* Mobile first */
@media (min-width: 640px) { /* sm */ }
@media (min-width: 768px) { /* md */ }
@media (min-width: 1024px) { /* lg */ }
@media (min-width: 1280px) { /* xl */ }
```

Minimum supported: 1024px width (desktop-focused like Mixamo)

---

### 8. Error Handling

#### 8.1 Backend Errors

```python
class OpenRigError(Exception):
    """Base exception for OpenRig."""
    pass

class ModelValidationError(OpenRigError):
    """Invalid model file."""
    pass

class RiggingError(OpenRigError):
    """Rigging process failed."""
    pass

class AnimationError(OpenRigError):
    """Animation processing failed."""
    pass

class ExportError(OpenRigError):
    """Export process failed."""
    pass
```

#### 8.2 Error Response Format

```json
{
  "success": false,
  "error": {
    "code": "RIGGING_FAILED",
    "message": "Failed to generate skeleton",
    "details": "Blender process exited with code 1",
    "suggestion": "Ensure model is a closed mesh with proper topology"
  }
}
```

#### 8.3 Frontend Error Display

- Toast notifications for minor errors
- Modal dialogs for blocking errors
- Inline validation for forms
- Retry buttons where appropriate

---

### 9. Performance Considerations

#### 9.1 Backend Optimization

- **Process pooling**: Pre-spawn Blender processes
- **Caching**: Cache rigged models by hash
- **Cleanup**: Auto-delete old files (24h TTL)
- **Queue**: Use job queue for long operations

#### 9.2 Frontend Optimization

- **Model LOD**: Reduce polygon count for preview
- **Lazy loading**: Load animations on demand
- **Web Workers**: Offload heavy computations
- **Compression**: Use Draco for GLB files

#### 9.3 Resource Limits

| Resource | Limit | Rationale |
|----------|-------|-----------|
| Upload size | 50 MB | Reasonable for game models |
| Vertex count | 100,000 | Performance in browser |
| Concurrent jobs | 2 | Free tier memory limit |
| Job timeout | 5 minutes | Prevent hanging processes |
| File retention | 24 hours | Storage management |

---

### 10. Security Considerations

#### 10.1 Input Validation

- Validate file types (magic bytes, not just extension)
- Sanitize file names
- Limit upload sizes
- Validate JSON marker data
- Rate limiting (10 requests/minute per IP)

#### 10.2 Process Isolation

- Run Blender in sandboxed container
- No network access during processing
- Temporary directories per job
- Clean up after each job

#### 10.3 CORS Configuration

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://openrig.example.com"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)
```

---

### 11. Monitoring & Logging

#### 11.1 Logging Format

```python
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Log structure
{
    "timestamp": "2024-01-15T10:30:00Z",
    "level": "INFO",
    "service": "rigging",
    "job_id": "uuid",
    "message": "Rigging completed",
    "duration_ms": 45000
}
```

#### 11.2 Metrics to Track

- Upload count/size
- Rigging success/failure rate
- Processing time distribution
- Animation usage statistics
- Export format preferences

---

### 12. Future Enhancements

#### 12.1 Potential Features

- [ ] User accounts (save models/animations)
- [ ] Custom animation upload
- [ ] Face rigging
- [ ] Finger rigging
- [ ] Batch processing
- [ ] API access for developers
- [ ] Animation blending preview
- [ ] Texture support in preview

#### 12.2 Scalability Path

1. **Phase 1**: Single Oracle instance (current)
2. **Phase 2**: Add Redis for job queue
3. **Phase 3**: Separate worker containers
4. **Phase 4**: Object storage for files
5. **Phase 5**: Load balancer for multiple workers

---

## Quick Reference

### Key Commands

```bash
# Development
docker-compose up -d              # Start all services
docker-compose logs -f backend    # View backend logs
docker-compose exec backend bash  # Shell into backend

# Testing
pytest backend/tests/             # Run backend tests
npm test                          # Run frontend tests

# Blender Scripts
blender --background --python blender_scripts/auto_rig.py -- --help

# Deployment
./scripts/deploy.sh               # Deploy to Oracle Cloud
```

### API Quick Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | /api/upload | Upload 3D model |
| POST | /api/rig | Process with markers |
| GET | /api/animations | List animations |
| POST | /api/apply-animation | Apply animation |
| POST | /api/export | Export final model |
| GET | /api/models/{id}/status | Check job status |

### File Size Limits

| Type | Limit |
|------|-------|
| Model upload | 50 MB |
| Animation file | 10 MB |
| Export result | 100 MB |

---

## License

This project is licensed under the MIT License.

## Contributing

See CONTRIBUTING.md for guidelines.

## Support

- GitHub Issues for bugs
- Discussions for questions
- Wiki for documentation
