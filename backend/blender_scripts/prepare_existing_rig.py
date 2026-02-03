"""
prepare_existing_rig.py - Prepare an uploaded model with an existing skeleton

When a user uploads a model that already has a skeleton (e.g., from Mixamo or
another rigging tool), this script opens it and saves as .blend + .glb so the
animation pipeline can use it.

Usage:
    blender --background --python prepare_existing_rig.py -- \
        --input /path/to/model.fbx \
        --output /path/to/rigged.glb
"""

import bpy
import sys
import argparse
import traceback
from pathlib import Path


def clear_scene():
    """Remove all objects from the scene."""
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()
    for block in bpy.data.meshes:
        if block.users == 0:
            bpy.data.meshes.remove(block)
    for block in bpy.data.armatures:
        if block.users == 0:
            bpy.data.armatures.remove(block)


def import_model(filepath):
    """Import model and return (mesh, armature)."""
    filepath = Path(filepath)
    ext = filepath.suffix.lower()

    print(f"[prepare_rig]   Importing {ext} file: {filepath}")

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

    # Catalog all objects
    print(f"[prepare_rig]   Objects in scene ({len(bpy.data.objects)}):")
    for obj in bpy.data.objects:
        parent_info = f", parent='{obj.parent.name}'" if obj.parent else ""
        print(f"[prepare_rig]     - '{obj.name}' type={obj.type}{parent_info}")

    armature = None
    mesh = None

    for obj in bpy.data.objects:
        if obj.type == "ARMATURE" and armature is None:
            armature = obj
        elif obj.type == "MESH" and mesh is None:
            mesh = obj

    # If no armature found directly, check mesh parent/modifiers
    if not armature and mesh:
        if mesh.parent and mesh.parent.type == "ARMATURE":
            armature = mesh.parent
        else:
            for mod in mesh.modifiers:
                if mod.type == "ARMATURE" and mod.object:
                    armature = mod.object
                    break

    return mesh, armature


def strip_to_def_bones(rig, mesh):
    """Strip rig to DEF-only bones for GLTF export (Blender 3.0.1 compat).

    Only strips if the rig actually has DEF- prefixed bones (i.e., Rigify).
    Non-Rigify rigs (Mixamo, custom) are left as-is.
    """
    bone_names = [b.name for b in rig.data.bones]
    has_def_bones = any(b.startswith("DEF-") for b in bone_names)

    if not has_def_bones:
        print("[prepare_rig]   No DEF- bones found, keeping rig as-is for export")
        return

    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)

    # Remove constraints on DEF bones
    bpy.ops.object.mode_set(mode="POSE")
    for pbone in rig.pose.bones:
        if pbone.name.startswith("DEF-"):
            for c in list(pbone.constraints):
                pbone.constraints.remove(c)
    bpy.ops.object.mode_set(mode="OBJECT")

    # Re-parent DEF bones and delete non-DEF
    bpy.ops.object.mode_set(mode="EDIT")
    edit_bones = rig.data.edit_bones
    for bone in edit_bones:
        if not bone.name.startswith("DEF-"):
            continue
        parent = bone.parent
        while parent and not parent.name.startswith("DEF-"):
            parent = parent.parent
        bone.parent = parent
    non_def = [b for b in edit_bones if not b.name.startswith("DEF-")]
    for bone in non_def:
        edit_bones.remove(bone)
    bpy.ops.object.mode_set(mode="OBJECT")

    # Clean vertex groups
    remaining = {b.name for b in rig.data.bones}
    for vg in list(mesh.vertex_groups):
        if vg.name not in remaining:
            mesh.vertex_groups.remove(vg)
    print(f"[prepare_rig]   Stripped to {len(remaining)} DEF bones")


def export_glb(filepath, mesh, armature):
    """Export mesh + armature as GLB."""
    # Clean up WGT- objects
    for obj in list(bpy.data.objects):
        if obj.name.startswith("WGT-"):
            bpy.data.objects.remove(obj, do_unlink=True)

    bpy.ops.object.select_all(action="DESELECT")
    mesh.select_set(True)
    armature.select_set(True)

    gltf_params = dict(
        filepath=str(filepath),
        export_format="GLB",
        use_selection=True,
        export_skins=True,
        export_animations=True,
    )
    try:
        bpy.ops.export_scene.gltf(**gltf_params, export_all_influences=True)
    except TypeError:
        bpy.ops.export_scene.gltf(**gltf_params)


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

    print(f"[prepare_rig] Input: {args.input}")
    print(f"[prepare_rig] Output: {args.output}")

    try:
        print("[prepare_rig] Step 1/3: Importing model...")
        clear_scene()
        mesh, armature = import_model(args.input)

        if not armature:
            raise ValueError("No armature/skeleton found in model")
        if not mesh:
            raise ValueError("No mesh found in model")

        bone_names = [b.name for b in armature.data.bones]
        print(f"[prepare_rig]   Armature: '{armature.name}', {len(bone_names)} bones")
        print(f"[prepare_rig]   Mesh: '{mesh.name}'")
        print(f"[prepare_rig]   Bone names: {bone_names[:20]}...")

        # Ensure mesh is parented to armature
        if mesh.parent != armature:
            print("[prepare_rig]   Re-parenting mesh to armature")
            mesh.parent = armature
            # Add armature modifier if not present
            has_arm_mod = any(m.type == "ARMATURE" for m in mesh.modifiers)
            if not has_arm_mod:
                mod = mesh.modifiers.new(name="Armature", type="ARMATURE")
                mod.object = armature

        print("[prepare_rig] Step 2/3: Saving .blend file...")
        blend_path = str(Path(args.output).with_suffix(".blend"))
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"[prepare_rig]   Saved: {blend_path}")

        print("[prepare_rig] Step 3/3: Exporting GLB preview...")
        strip_to_def_bones(armature, mesh)
        export_glb(args.output, mesh, armature)

        print(f"[prepare_rig] SUCCESS: bone_count={len(bone_names)}")
    except Exception as e:
        print(f"[prepare_rig] FAILED: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
