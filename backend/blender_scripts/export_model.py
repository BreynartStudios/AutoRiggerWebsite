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
import traceback
from pathlib import Path


def import_model(filepath):
    """Import model, return (mesh, armature)."""
    filepath = Path(filepath)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    if filepath.suffix.lower() in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=str(filepath))
    elif filepath.suffix.lower() == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(filepath))

    # Diagnostic: print all objects
    print(f"[export]   Objects after import ({len(bpy.data.objects)}):")
    for obj in bpy.data.objects:
        parent_info = f", parent='{obj.parent.name}'" if obj.parent else ""
        print(f"[export]     - '{obj.name}' type={obj.type}{parent_info}")
    print(f"[export]   Armature data blocks: {[a.name for a in bpy.data.armatures]}")

    armature = None
    mesh = None

    # Method 1: Direct type check
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE" and armature is None:
            armature = obj
        elif obj.type == "MESH" and mesh is None:
            mesh = obj

    # Method 2: Check for objects with armature data
    if not armature:
        for obj in bpy.data.objects:
            if obj.data and obj.data.__class__.__name__ == "Armature":
                armature = obj
                break

    # Method 3: Check mesh parent/modifiers
    if not armature and mesh:
        parent = mesh.parent
        while parent:
            if parent.type == "ARMATURE":
                armature = parent
                break
            parent = parent.parent
        if not armature:
            for mod in mesh.modifiers:
                if mod.type == "ARMATURE" and mod.object:
                    armature = mod.object
                    break

    # Method 4: Create armature object from orphan data
    if not armature and bpy.data.armatures:
        arm_data = bpy.data.armatures[0]
        print(f"[export]   Creating armature from data: '{arm_data.name}' ({len(arm_data.bones)} bones)")
        armature = bpy.data.objects.new("Armature", arm_data)
        bpy.context.scene.collection.objects.link(armature)
        if mesh and not mesh.parent:
            mesh.parent = armature

    return mesh, armature


def import_and_retarget_animation(armature, anim_path, anim_name):
    """Import animation and retarget to armature."""
    filepath = Path(anim_path)

    # Remember existing armatures
    existing = {obj.name for obj in bpy.data.objects if obj.type == "ARMATURE"}

    if filepath.suffix.lower() == ".bvh":
        bpy.ops.import_anim.bvh(filepath=str(filepath))
    elif filepath.suffix.lower() == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(filepath), use_anim=True)

    # Find newly imported armature
    source = None
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE" and obj.name not in existing:
            source = obj
            break

    if source and source.animation_data and source.animation_data.action:
        action = source.animation_data.action.copy()
        action.name = anim_name
        print(f"[export]   Animation '{anim_name}': {int(action.frame_range[1] - action.frame_range[0])} frames")

        bpy.data.objects.remove(source, do_unlink=True)
        return action

    # Clean up source even if no action found
    if source:
        bpy.data.objects.remove(source, do_unlink=True)

    print(f"[export]   WARNING: No animation data found for '{anim_name}'")
    return None


def export_with_animations(filepath, mesh, armature, actions, fmt):
    """Export model with all animations embedded."""
    if not armature.animation_data:
        armature.animation_data_create()

    for action in actions:
        if action:
            track = armature.animation_data.nla_tracks.new()
            track.name = action.name
            track.strips.new(action.name, int(action.frame_range[0]), action)

    bpy.ops.object.select_all(action="DESELECT")
    mesh.select_set(True)
    armature.select_set(True)

    filepath = Path(filepath)

    if fmt.lower() == "glb":
        gltf_params = dict(
            filepath=str(filepath),
            export_format="GLB",
            use_selection=True,
            export_skins=True,
            export_animations=True,
        )
        try:
            bpy.ops.export_scene.gltf(
                **gltf_params,
                export_nla_strips=True,
                export_all_influences=True,
            )
        except TypeError:
            bpy.ops.export_scene.gltf(**gltf_params)
    elif fmt.lower() == "fbx":
        # bake_anim_use_nla_strips may not exist in Blender 3.0.1
        fbx_params = dict(
            filepath=str(filepath),
            use_selection=True,
            bake_anim=True,
            bake_anim_use_all_actions=True,
            add_leaf_bones=False,
        )
        try:
            bpy.ops.export_scene.fbx(**fbx_params, bake_anim_use_nla_strips=True)
        except TypeError:
            bpy.ops.export_scene.fbx(**fbx_params)


def main():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--animations", required=True, help="Comma-separated paths")
    parser.add_argument("--names", required=True, help="Comma-separated names")
    parser.add_argument("--format", choices=["fbx", "glb"], default="glb")
    parser.add_argument("--output", required=True)

    args = parser.parse_args(argv)

    print(f"[export] Model: {args.model}")
    print(f"[export] Animations: {args.animations}")
    print(f"[export] Names: {args.names}")
    print(f"[export] Format: {args.format}")
    print(f"[export] Output: {args.output}")

    try:
        anim_paths = [p.strip() for p in args.animations.split(",") if p.strip()]
        anim_names = [n.strip() for n in args.names.split(",") if n.strip()]

        print("[export] Step 1/3: Importing model...")
        mesh, armature = import_model(args.model)
        if not armature:
            raise ValueError("No armature found in model")
        if not mesh:
            raise ValueError("No mesh found in model")
        print(f"[export]   Armature: '{armature.name}', Mesh: '{mesh.name}'")

        print(f"[export] Step 2/3: Importing {len(anim_paths)} animations...")
        actions = []
        for path, name in zip(anim_paths, anim_names):
            action = import_and_retarget_animation(armature, path, name)
            if action:
                actions.append(action)

        print(f"[export] Step 3/3: Exporting as {args.format.upper()}...")
        export_with_animations(args.output, mesh, armature, actions, args.format)

        print(f"[export] SUCCESS: Exported {len(actions)} animations to {args.output}")
    except Exception as e:
        print(f"[export] FAILED: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
