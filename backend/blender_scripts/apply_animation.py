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
import traceback
from pathlib import Path


# Bone mapping from BVH standard names to Rigify deform bone names.
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


def build_bone_mapping(source_armature, target_armature):
    """
    Build bone mapping from source to target, auto-detecting naming convention.
    Tries DEF- prefixed names, plain names, and ORG- names.
    """
    mapping = {}
    source_bones = [b.name for b in source_armature.pose.bones]
    target_bones = {b.name for b in target_armature.pose.bones}

    print(f"[apply_anim]   Source bones ({len(source_bones)}): {source_bones[:30]}")
    print(f"[apply_anim]   Target bones ({len(target_bones)}): {sorted(list(target_bones))[:30]}")

    # Check if this is a Mixamo rig (bones prefixed with "mixamorig:")
    is_mixamo = any(b.startswith("mixamorig:") for b in source_bones)
    if is_mixamo:
        print("[apply_anim]   Detected Mixamo naming convention")

    for bone_name in source_bones:
        # Get the clean name for BVH lookup
        clean_name = bone_name.replace("mixamorig:", "") if is_mixamo else bone_name

        rigify_name = BVH_TO_RIGIFY.get(clean_name)
        if not rigify_name:
            continue

        # Try multiple target name patterns
        candidates = [
            rigify_name,                          # DEF-spine
            rigify_name.replace("DEF-", ""),       # spine
            rigify_name.replace("DEF-", "ORG-"),   # ORG-spine
        ]

        for candidate in candidates:
            if candidate in target_bones:
                mapping[bone_name] = candidate
                break

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

    # Check all objects (not just selected - GLTF may not select all)
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE" and armature is None:
            armature = obj
        elif obj.type == "MESH" and mesh is None:
            mesh = obj

    if not armature:
        raise ValueError("No armature found in rigged model")
    if not mesh:
        raise ValueError("No mesh found in rigged model")

    return mesh, armature


def import_animation(filepath, existing_armatures):
    """Import BVH or FBX animation. Returns newly imported armature."""
    filepath = Path(filepath)

    if filepath.suffix.lower() == ".bvh":
        bpy.ops.import_anim.bvh(
            filepath=str(filepath),
            use_fps_scale=True,
            update_scene_fps=False,
        )
    elif filepath.suffix.lower() == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(filepath), use_anim=True)

    # Find the NEW armature (not one that existed before import)
    for obj in bpy.data.objects:
        if obj.type == "ARMATURE" and obj.name not in existing_armatures:
            return obj

    raise ValueError("No new armature found after importing animation")


def retarget_animation(source_armature, target_armature, animation_name):
    """Retarget animation from source armature to target armature."""
    # Build mapping using both armatures
    bone_mapping = build_bone_mapping(source_armature, target_armature)
    print(f"[apply_anim]   Mapping: {bone_mapping}")

    if not bone_mapping:
        print("[apply_anim]   WARNING: No bones could be mapped!")
        bpy.data.objects.remove(source_armature, do_unlink=True)
        return None

    # Get source action
    if not (source_armature.animation_data and source_armature.animation_data.action):
        raise ValueError("Source armature has no animation data")

    source_action = source_armature.animation_data.action
    frame_start = int(source_action.frame_range[0])
    frame_end = int(source_action.frame_range[1])
    total_frames = frame_end - frame_start + 1
    print(f"[apply_anim]   Frame range: {frame_start}-{frame_end} ({total_frames} frames)")

    # Set up target for posing
    bpy.context.view_layer.objects.active = target_armature
    bpy.ops.object.mode_set(mode="POSE")

    if target_armature.animation_data is None:
        target_armature.animation_data_create()

    action = bpy.data.actions.new(name=animation_name)
    target_armature.animation_data.action = action

    # Root bones get location keyframes too
    root_bones = {"Hips", "mixamorig:Hips", "LowerBack"}

    # Log rotation modes for debugging
    for src_name, tgt_name in list(bone_mapping.items())[:3]:
        sb = source_armature.pose.bones.get(src_name)
        tb = target_armature.pose.bones.get(tgt_name)
        if sb and tb:
            print(f"[apply_anim]   Rotation modes: src '{src_name}'={sb.rotation_mode}, tgt '{tgt_name}'={tb.rotation_mode}")

    mapped_per_frame = 0
    for frame in range(frame_start, frame_end + 1):
        bpy.context.scene.frame_set(frame)

        for src_name, tgt_name in bone_mapping.items():
            source_bone = source_armature.pose.bones.get(src_name)
            target_bone = target_armature.pose.bones.get(tgt_name)
            if not source_bone or not target_bone:
                continue

            # Read rotation in whatever mode the source uses
            if source_bone.rotation_mode == "QUATERNION":
                quat = source_bone.rotation_quaternion.copy()
            else:
                # BVH bones typically use Euler - convert to quaternion
                quat = source_bone.rotation_euler.to_quaternion()

            # Write rotation in whatever mode the target uses
            if target_bone.rotation_mode == "QUATERNION":
                target_bone.rotation_quaternion = quat
                target_bone.keyframe_insert(data_path="rotation_quaternion", frame=frame)
            else:
                target_bone.rotation_euler = quat.to_euler(target_bone.rotation_mode)
                target_bone.keyframe_insert(data_path="rotation_euler", frame=frame)

            if frame == frame_start:
                mapped_per_frame += 1

            # Copy location for root bone only
            if src_name in root_bones:
                target_bone.location = source_bone.location
                target_bone.keyframe_insert(data_path="location", frame=frame)

    print(f"[apply_anim]   Bones animated per frame: {mapped_per_frame}")

    bpy.ops.object.mode_set(mode="OBJECT")

    # Clean up source armature
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

    print(f"[apply_anim] Model: {args.model}")
    print(f"[apply_anim] Animation: {args.animation}")
    print(f"[apply_anim] Output: {args.output}")
    print(f"[apply_anim] Name: {args.name}")

    try:
        print("[apply_anim] Step 1/5: Clearing scene...")
        bpy.ops.object.select_all(action="SELECT")
        bpy.ops.object.delete()

        print("[apply_anim] Step 2/5: Importing rigged model...")
        mesh, armature = import_rigged_model(args.model)
        bone_names = [b.name for b in armature.data.bones]
        print(f"[apply_anim]   Armature: '{armature.name}', {len(bone_names)} bones")
        print(f"[apply_anim]   Mesh: '{mesh.name}'")
        print(f"[apply_anim]   All bone names: {bone_names}")

        # Remember existing armatures before importing animation
        existing_armatures = {obj.name for obj in bpy.data.objects if obj.type == "ARMATURE"}

        print("[apply_anim] Step 3/5: Importing animation...")
        source_anim = import_animation(args.animation, existing_armatures)
        src_bone_names = [b.name for b in source_anim.data.bones]
        print(f"[apply_anim]   BVH armature: '{source_anim.name}', {len(src_bone_names)} bones")
        print(f"[apply_anim]   BVH bone names: {src_bone_names}")
        if source_anim.animation_data and source_anim.animation_data.action:
            act = source_anim.animation_data.action
            print(f"[apply_anim]   Action: '{act.name}', frames {act.frame_range[0]}-{act.frame_range[1]}")
        else:
            print("[apply_anim]   WARNING: No animation data on imported armature!")

        print("[apply_anim] Step 4/5: Retargeting animation...")
        result = retarget_animation(source_anim, armature, args.name)
        if result:
            print(f"[apply_anim]   Retarget complete, action: '{result.name}'")
        else:
            print("[apply_anim]   WARNING: Retarget produced no action")

        print("[apply_anim] Step 5/5: Exporting animated model...")
        export_animated_model(args.output, mesh, armature)

        print(f"[apply_anim] SUCCESS: Exported to {args.output}")
    except Exception as e:
        print(f"[apply_anim] FAILED: {e}")
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
