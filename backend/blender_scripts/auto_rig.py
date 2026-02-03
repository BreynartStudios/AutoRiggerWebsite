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
import addon_utils
from mathutils import Vector
from pathlib import Path


REQUIRED_MARKERS = [
    "chin", "groin",
    "wrist_l", "wrist_r",
    "elbow_l", "elbow_r",
    "knee_l", "knee_r",
]

MARKER_TO_BONE = {
    "chin": "spine.006",
    "groin": "spine",
    "wrist_l": "hand.L",
    "wrist_r": "hand.R",
    "elbow_l": "forearm.L",
    "elbow_r": "forearm.R",
    "knee_l": "shin.L",
    "knee_r": "shin.R",
}


def enable_rigify():
    """Enable the Rigify addon (required for Blender 3.x from apt)."""
    loaded_default, loaded_state = addon_utils.check("rigify")
    if not loaded_state:
        addon_utils.enable("rigify", default_set=True)
        print("Rigify addon enabled successfully")
    else:
        print("Rigify addon already enabled")


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
    """Import 3D model based on file extension."""
    filepath = Path(filepath)
    ext = filepath.suffix.lower()

    if ext == ".obj":
        # bpy.ops.wm.obj_import was added in Blender 3.4+
        # Blender 3.0 uses bpy.ops.import_scene.obj
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

    # Remove any existing armatures from the import (we create our own with Rigify)
    for obj in list(bpy.data.objects):
        if obj.type == "ARMATURE":
            print(f"[auto_rig] Removing existing armature: '{obj.name}'")
            bpy.data.objects.remove(obj, do_unlink=True)

    mesh_objects = [obj for obj in bpy.data.objects if obj.type == "MESH"]

    if not mesh_objects:
        raise ValueError("No mesh found in imported file")

    # Join multiple meshes into one
    if len(mesh_objects) > 1:
        bpy.ops.object.select_all(action="DESELECT")
        for obj in mesh_objects:
            obj.select_set(True)
        bpy.context.view_layer.objects.active = mesh_objects[0]
        bpy.ops.object.join()

    mesh = mesh_objects[0] if len(mesh_objects) == 1 else bpy.context.active_object
    bpy.context.view_layer.objects.active = mesh
    bpy.ops.object.origin_set(type="ORIGIN_CENTER_OF_VOLUME")
    mesh.location = (0, 0, 0)

    return mesh


def validate_markers(markers):
    """Validate that all required markers are present."""
    for marker in REQUIRED_MARKERS:
        if marker not in markers:
            raise ValueError(f"Missing required marker: {marker}")
        if len(markers[marker]) != 3:
            raise ValueError(f"Invalid coordinates for marker: {marker}")
    return True


def calculate_character_scale(markers):
    """Calculate scale factor based on marker positions."""
    chin = Vector(markers["chin"])
    groin = Vector(markers["groin"])
    height = (chin - groin).length
    standard_height = 1.5
    return height / standard_height


def create_metarig():
    """Create a Rigify human metarig."""
    bpy.ops.object.armature_human_metarig_add()
    metarig = bpy.context.active_object
    metarig.name = "metarig"
    return metarig


def fit_metarig_to_markers(metarig, markers):
    """
    Adjust metarig bones to match marker positions.
    Interpolates the full skeleton from 8 marker points.
    """
    scale = calculate_character_scale(markers)

    bpy.context.view_layer.objects.active = metarig
    bpy.ops.object.mode_set(mode="EDIT")

    bones = metarig.data.edit_bones
    m = {k: Vector(v) for k, v in markers.items()}

    # Scale entire metarig first
    for bone in bones:
        bone.head *= scale
        bone.tail *= scale

    # === SPINE CHAIN ===
    spine_bones = [
        "spine", "spine.001", "spine.002", "spine.003",
        "spine.004", "spine.005", "spine.006",
    ]

    for i, bone_name in enumerate(spine_bones):
        if bone_name in bones:
            t = i / (len(spine_bones) - 1)
            target = m["groin"].lerp(m["chin"], t)
            curve_offset = Vector((0, -0.02 * scale * (1 - abs(2 * t - 1)), 0))
            bones[bone_name].head = target + curve_offset

    for i in range(len(spine_bones) - 1):
        if spine_bones[i] in bones and spine_bones[i + 1] in bones:
            bones[spine_bones[i]].tail = bones[spine_bones[i + 1]].head

    # === LEFT ARM ===
    shoulder_l_pos = m["chin"].lerp(m["groin"], 0.15)
    shoulder_l_pos.x = m["elbow_l"].x * 0.4

    if "shoulder.L" in bones:
        bones["shoulder.L"].head = shoulder_l_pos
    if "upper_arm.L" in bones:
        bones["upper_arm.L"].head = shoulder_l_pos + Vector((-0.1 * scale, 0, 0))
        bones["upper_arm.L"].tail = m["elbow_l"]
    if "forearm.L" in bones:
        bones["forearm.L"].head = m["elbow_l"]
        bones["forearm.L"].tail = m["wrist_l"]
    if "hand.L" in bones:
        bones["hand.L"].head = m["wrist_l"]
        hand_dir = (m["wrist_l"] - m["elbow_l"]).normalized()
        bones["hand.L"].tail = m["wrist_l"] + hand_dir * 0.1 * scale

    # === RIGHT ARM ===
    shoulder_r_pos = m["chin"].lerp(m["groin"], 0.15)
    shoulder_r_pos.x = m["elbow_r"].x * 0.4

    if "shoulder.R" in bones:
        bones["shoulder.R"].head = shoulder_r_pos
    if "upper_arm.R" in bones:
        bones["upper_arm.R"].head = shoulder_r_pos + Vector((0.1 * scale, 0, 0))
        bones["upper_arm.R"].tail = m["elbow_r"]
    if "forearm.R" in bones:
        bones["forearm.R"].head = m["elbow_r"]
        bones["forearm.R"].tail = m["wrist_r"]
    if "hand.R" in bones:
        bones["hand.R"].head = m["wrist_r"]
        hand_dir = (m["wrist_r"] - m["elbow_r"]).normalized()
        bones["hand.R"].tail = m["wrist_r"] + hand_dir * 0.1 * scale

    # === LEFT LEG ===
    hip_l_pos = m["groin"].copy()
    hip_l_pos.x = m["knee_l"].x

    if "thigh.L" in bones:
        bones["thigh.L"].head = hip_l_pos
        bones["thigh.L"].tail = m["knee_l"]
    if "shin.L" in bones:
        bones["shin.L"].head = m["knee_l"]
        ankle_l = m["knee_l"].copy()
        ankle_l.z = 0.05 * scale
        bones["shin.L"].tail = ankle_l
    if "foot.L" in bones:
        bones["foot.L"].head = bones["shin.L"].tail
        bones["foot.L"].tail = bones["foot.L"].head + Vector((0, -0.15 * scale, 0))

    # === RIGHT LEG ===
    hip_r_pos = m["groin"].copy()
    hip_r_pos.x = m["knee_r"].x

    if "thigh.R" in bones:
        bones["thigh.R"].head = hip_r_pos
        bones["thigh.R"].tail = m["knee_r"]
    if "shin.R" in bones:
        bones["shin.R"].head = m["knee_r"]
        ankle_r = m["knee_r"].copy()
        ankle_r.z = 0.05 * scale
        bones["shin.R"].tail = ankle_r
    if "foot.R" in bones:
        bones["foot.R"].head = bones["shin.R"].tail
        bones["foot.R"].tail = bones["foot.R"].head + Vector((0, -0.15 * scale, 0))

    # === HEAD ===
    if "spine.006" in bones:
        head_dir = (m["chin"] - m["groin"]).normalized()
        bones["spine.006"].tail = m["chin"] + head_dir * 0.2 * scale

    bpy.ops.object.mode_set(mode="OBJECT")


def generate_rig(metarig):
    """Generate final rig from metarig using Rigify."""
    bpy.context.view_layer.objects.active = metarig
    bpy.ops.pose.rigify_generate()

    rig = bpy.data.objects.get("rig")
    if not rig:
        raise RuntimeError("Rigify failed to generate rig")
    return rig


def bind_mesh_to_rig(mesh, rig):
    """Bind mesh to rig with automatic weights."""
    bpy.ops.object.select_all(action="DESELECT")
    mesh.select_set(True)
    rig.select_set(True)
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.parent_set(type="ARMATURE_AUTO")


def cleanup_for_export(rig, mesh):
    """Clean up scene for export."""
    metarig = bpy.data.objects.get("metarig")
    if metarig:
        bpy.data.objects.remove(metarig, do_unlink=True)

    for obj in list(bpy.data.objects):
        if obj.name.startswith("WGT-"):
            bpy.data.objects.remove(obj, do_unlink=True)


def simplify_rig_for_export(rig, mesh):
    """
    Strip the Rigify rig down to only DEF- (deformation) bones.

    Blender 3.0.1's GLTF exporter doesn't have the export_def_bones
    parameter and can't handle the complex Rigify rig (hundreds of
    control/mechanism bones). It ends up exporting EMPTY nodes instead
    of a proper armature/skin. This function manually removes all
    non-deformation bones so the GLTF exporter can produce a valid GLB.
    """
    bpy.context.view_layer.objects.active = rig
    bpy.ops.object.select_all(action="DESELECT")
    rig.select_set(True)

    # Step 1: Remove constraints on DEF- bones (they reference control bones
    # that we're about to delete)
    bpy.ops.object.mode_set(mode="POSE")
    for pbone in rig.pose.bones:
        if pbone.name.startswith("DEF-"):
            for c in list(pbone.constraints):
                pbone.constraints.remove(c)
    bpy.ops.object.mode_set(mode="OBJECT")

    # Step 2: In edit mode, re-parent DEF bones to nearest DEF ancestor,
    # then delete all non-DEF bones
    bpy.ops.object.mode_set(mode="EDIT")
    edit_bones = rig.data.edit_bones

    # Re-parent: walk up each DEF bone's parent chain to find nearest DEF parent
    for bone in edit_bones:
        if not bone.name.startswith("DEF-"):
            continue
        parent = bone.parent
        while parent and not parent.name.startswith("DEF-"):
            parent = parent.parent
        bone.parent = parent  # None if no DEF ancestor

    # Delete all non-DEF bones
    non_def = [b for b in edit_bones if not b.name.startswith("DEF-")]
    for bone in non_def:
        edit_bones.remove(bone)

    bpy.ops.object.mode_set(mode="OBJECT")

    # Step 3: Remove vertex groups that no longer have corresponding bones
    remaining_bones = {b.name for b in rig.data.bones}
    for vg in list(mesh.vertex_groups):
        if vg.name not in remaining_bones:
            mesh.vertex_groups.remove(vg)

    print(f"[auto_rig] Simplified rig: {len(remaining_bones)} DEF bones, "
          f"{len(mesh.vertex_groups)} vertex groups")


def export_model(filepath, rig, mesh):
    """Export rigged model."""
    bpy.ops.object.select_all(action="DESELECT")
    mesh.select_set(True)
    rig.select_set(True)

    filepath = Path(filepath)

    if filepath.suffix.lower() == ".glb":
        # Parameters differ between Blender versions
        # export_def_bones / export_all_influences were added in later versions
        gltf_params = dict(
            filepath=str(filepath),
            export_format="GLB",
            use_selection=True,
            export_skins=True,
        )
        try:
            bpy.ops.export_scene.gltf(
                **gltf_params,
                export_all_influences=True,
                export_def_bones=True,
            )
        except TypeError:
            bpy.ops.export_scene.gltf(**gltf_params)
    elif filepath.suffix.lower() == ".fbx":
        bpy.ops.export_scene.fbx(
            filepath=str(filepath),
            use_selection=True,
            add_leaf_bones=False,
            bake_anim=False,
        )


def main():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser(description="Auto-rig a 3D model")
    parser.add_argument("--input", required=True, help="Input model file")
    parser.add_argument("--markers", required=True, help="Markers JSON file")
    parser.add_argument("--output", required=True, help="Output file path")

    args = parser.parse_args(argv)

    # Enable Rigify addon (not enabled by default in apt-installed Blender)
    print(f"[auto_rig] Input: {args.input}")
    print(f"[auto_rig] Markers: {args.markers}")
    print(f"[auto_rig] Output: {args.output}")

    try:
        print("[auto_rig] Step 1/9: Enabling Rigify...")
        enable_rigify()

        print("[auto_rig] Step 2/9: Loading markers...")
        with open(args.markers, "r") as f:
            markers = json.load(f)
        validate_markers(markers)
        print(f"[auto_rig] Markers loaded: {list(markers.keys())}")

        print("[auto_rig] Step 3/9: Clearing scene...")
        clear_scene()

        print("[auto_rig] Step 4/9: Importing model...")
        mesh = import_model(args.input)
        print(f"[auto_rig] Model imported: {mesh.name}, verts={len(mesh.data.vertices)}")

        print("[auto_rig] Step 5/9: Creating metarig...")
        metarig = create_metarig()

        print("[auto_rig] Step 6/9: Fitting metarig to markers...")
        fit_metarig_to_markers(metarig, markers)

        print("[auto_rig] Step 7/9: Generating Rigify rig...")
        rig = generate_rig(metarig)

        print("[auto_rig] Step 8/9: Binding mesh and cleaning up...")
        bind_mesh_to_rig(mesh, rig)
        cleanup_for_export(rig, mesh)

        print("[auto_rig] Step 9/9: Saving .blend and exporting GLB preview...")
        # Save .blend FIRST (preserves full armature data for animation pipeline)
        # Blender 3.0.1's GLTF exporter cannot handle armatures properly
        blend_path = str(Path(args.output).with_suffix(".blend"))
        bpy.ops.wm.save_as_mainfile(filepath=blend_path)
        print(f"[auto_rig] Saved .blend: {blend_path}")

        # Also export GLB for browser preview (mesh-only is fine for viewer)
        simplify_rig_for_export(rig, mesh)
        export_model(args.output, rig, mesh)

        print(f"[auto_rig] SUCCESS: Exported to {args.output}")
    except Exception as e:
        import traceback
        print(f"[auto_rig] FAILED at: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
