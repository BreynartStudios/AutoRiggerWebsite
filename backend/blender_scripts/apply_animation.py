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
    "Hips": "DEF-spine",
    "Spine": "DEF-spine.001",
    "Spine1": "DEF-spine.002",
    "Spine2": "DEF-spine.003",
    "Neck": "DEF-spine.004",
    "Head": "DEF-spine.006",
    "LeftShoulder": "DEF-shoulder.L",
    "LeftArm": "DEF-upper_arm.L",
    "LeftForeArm": "DEF-forearm.L",
    "LeftHand": "DEF-hand.L",
    "RightShoulder": "DEF-shoulder.R",
    "RightArm": "DEF-upper_arm.R",
    "RightForeArm": "DEF-forearm.R",
    "RightHand": "DEF-hand.R",
    "LeftUpLeg": "DEF-thigh.L",
    "LeftLeg": "DEF-shin.L",
    "LeftFoot": "DEF-foot.L",
    "LeftToeBase": "DEF-toe.L",
    "RightUpLeg": "DEF-thigh.R",
    "RightLeg": "DEF-shin.R",
    "RightFoot": "DEF-foot.R",
    "RightToeBase": "DEF-toe.R",
}


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

    for frame in range(frame_start, frame_end + 1):
        bpy.context.scene.frame_set(frame)

        for bvh_bone, rigify_bone in BVH_TO_RIGIFY.items():
            source_bone = source_armature.pose.bones.get(bvh_bone)
            if not source_bone:
                continue

            target_bone = target_armature.pose.bones.get(rigify_bone)
            if not target_bone:
                alt_name = rigify_bone.replace("DEF-", "")
                target_bone = target_armature.pose.bones.get(alt_name)

            if not target_bone:
                continue

            target_bone.rotation_quaternion = source_bone.rotation_quaternion
            target_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)

            if bvh_bone == "Hips":
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
