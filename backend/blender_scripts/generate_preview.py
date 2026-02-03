"""
generate_preview.py - Convert model to GLB preview format

Usage:
    blender --background --python generate_preview.py -- \
        --input /path/to/model.obj \
        --output /path/to/preview.glb
"""

import bpy
import sys
import argparse
from pathlib import Path


def clear_scene():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def import_model(filepath):
    filepath = Path(filepath)
    ext = filepath.suffix.lower()

    if ext == ".obj":
        if hasattr(bpy.ops.wm, "obj_import"):
            bpy.ops.wm.obj_import(filepath=str(filepath))
        else:
            bpy.ops.import_scene.obj(filepath=str(filepath))
    elif ext == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(filepath))
    elif ext in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=str(filepath))
    else:
        raise ValueError(f"Unsupported format: {ext}")


def export_glb(filepath):
    bpy.ops.object.select_all(action="SELECT")
    try:
        bpy.ops.export_scene.gltf(
            filepath=str(filepath),
            export_format="GLB",
            use_selection=True,
            export_skins=True,
            export_materials="EXPORT",
        )
    except TypeError:
        # Older Blender versions may not support export_materials param
        bpy.ops.export_scene.gltf(
            filepath=str(filepath),
            export_format="GLB",
            use_selection=True,
            export_skins=True,
        )


def main():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True)
    parser.add_argument("--output", required=True)

    args = parser.parse_args(argv)

    clear_scene()
    import_model(args.input)
    export_glb(args.output)

    print(f"Preview exported to: {args.output}")


if __name__ == "__main__":
    main()
