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
# Supports: CMU MoCap BVH, MotionBuilder standard, Mixamo FBX
BVH_TO_RIGIFY = {
    # Spine chain
    "Hips": "DEF-spine",
    "LowerBack": "DEF-spine",        # CMU alternate name for Hips
    "Spine": "DEF-spine.001",
    "Spine1": "DEF-spine.002",
    "Spine2": "DEF-spine.003",
    "Neck": "DEF-spine.004",
    "Neck1": "DEF-spine.005",        # CMU has extra neck joint
    "Head": "DEF-spine.006",

    # Left arm
    "LeftShoulder": "DEF-shoulder.L",
    "LeftArm": "DEF-upper_arm.L",
    "LeftForeArm": "DEF-forearm.L",
    "LeftHand": "DEF-hand.L",

    # Right arm
    "RightShoulder": "DEF-shoulder.R",
    "RightArm": "DEF-upper_arm.R",
    "RightForeArm": "DEF-forearm.R",
    "RightHand": "DEF-hand.R",

    # Left leg
    "LeftUpLeg": "DEF-thigh.L",
    "LeftLeg": "DEF-shin.L",
    "LeftFoot": "DEF-foot.L",
    "LeftToeBase": "DEF-toe.L",

    # Right leg
    "RightUpLeg": "DEF-thigh.R",
    "RightLeg": "DEF-shin.R",
    "RightFoot": "DEF-foot.R",
    "RightToeBase": "DEF-toe.R",
}


def build_bone_mapping(source_armature):
    """
    Build bone mapping from source to Rigify, auto-detecting naming convention.
    Supports standard BVH, CMU MoCap, and Mixamo (mixamorig:) naming.
    """
    mapping = {}
    source_bones = [b.name for b in source_armature.pose.bones]

    # Check if this is a Mixamo rig (bones prefixed with "mixamorig:")
    is_mixamo = any(b.startswith("mixamorig:") for b in source_bones)

    if is_mixamo:
        # Map Mixamo names: strip prefix and use standard mapping
        for bone_name in source_bones:
            clean_name = bone_name.replace("mixamorig:", "")
            if clean_name in BVH_TO_RIGIFY:
                mapping[bone_name] = BVH_TO_RIGIFY[clean_name]
    else:
        # Standard BVH / CMU MoCap naming
        for bone_name in source_bones:
            if bone_name in BVH_TO_RIGIFY:
                mapping[bone_name] = BVH_TO_RIGIFY[bone_name]

    return mapping


def import_rigged_model(filepath):
    """Import rigged model and return (mesh, armature)."""
    filepath = Path(filepath)

    if filepath.suffix.lower() in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=str(filepath))
    elif filepath.suffix.lower() == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(filepath))

    armature = None
    mesh = None

    for obj in bpy.context.selected_objects:
        if obj.type == "ARMATURE":
            armature = obj
        elif obj.type == "MESH":
            mesh = obj

    if not armature:
        raise ValueError("No armature found in model")

    return mesh, armature


def import_animation(filepath):
    """Import BVH or FBX animation."""
    filepath = Path(filepath)

    if filepath.suffix.lower() == ".bvh":
        bpy.ops.import_anim.bvh(
            filepath=str(filepath),
            use_fps_scale=True,
            update_scene_fps=False,
        )
    elif filepath.suffix.lower() == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(filepath), use_anim=True)

    for obj in bpy.context.selected_objects:
        if obj.type == "ARMATURE":
            return obj

    raise ValueError("No armature found in animation file")


def retarget_animation(source_armature, target_armature, animation_name):
    """Retarget animation from source armature to target armature."""
    bpy.context.view_layer.objects.active = target_armature
    bpy.ops.object.mode_set(mode="POSE")

    if target_armature.animation_data is None:
        target_armature.animation_data_create()

    action = bpy.data.actions.new(name=animation_name)
    target_armature.animation_data.action = action

    if not (source_armature.animation_data and source_armature.animation_data.action):
        raise ValueError("Source armature has no animation")

    source_action = source_armature.animation_data.action
    frame_start = int(source_action.frame_range[0])
    frame_end = int(source_action.frame_range[1])

    # Build mapping based on source bone naming convention
    bone_mapping = build_bone_mapping(source_armature)
    print(f"[retarget] Mapped {len(bone_mapping)} bones")

    # Detect root bone (Hips or mixamorig:Hips)
    root_bones = {"Hips", "mixamorig:Hips", "LowerBack"}

    for frame in range(frame_start, frame_end + 1):
        bpy.context.scene.frame_set(frame)

        for src_name, rigify_name in bone_mapping.items():
            source_bone = source_armature.pose.bones.get(src_name)
            if not source_bone:
                continue

            target_bone = target_armature.pose.bones.get(rigify_name)
            if not target_bone:
                alt_name = rigify_name.replace("DEF-", "")
                target_bone = target_armature.pose.bones.get(alt_name)

            if not target_bone:
                continue

            target_bone.rotation_quaternion = source_bone.rotation_quaternion
            target_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

            # Copy location for root bone only
            if src_name in root_bones:
                target_bone.location = source_bone.location
                target_bone.keyframe_insert(data_path="location", frame=frame)

    bpy.ops.object.mode_set(mode="OBJECT")

    bpy.data.objects.remove(source_armature, do_unlink=True)

    return action


def export_animated_model(filepath, mesh, armature):
    """Export model with animation."""
    bpy.ops.object.select_all(action="DESELECT")
    mesh.select_set(True)
    armature.select_set(True)

    filepath = Path(filepath)

    if filepath.suffix.lower() == ".glb":
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
    elif filepath.suffix.lower() == ".fbx":
        bpy.ops.export_scene.fbx(
            filepath=str(filepath),
            use_selection=True,
            bake_anim=True,
            bake_anim_use_all_actions=True,
        )


def main():
    argv = sys.argv
    if "--" in argv:
        argv = argv[argv.index("--") + 1:]
    else:
        argv = []

    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--animation", required=True)
    parser.add_argument("--output", required=True)
    parser.add_argument("--name", default="Animation")

    args = parser.parse_args(argv)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    mesh, armature = import_rigged_model(args.model)
    source_anim = import_animation(args.animation)
    retarget_animation(source_anim, armature, args.name)
    export_animated_model(args.output, mesh, armature)

    print(f"Successfully exported animated model to: {args.output}")


if __name__ == "__main__":
    main()
