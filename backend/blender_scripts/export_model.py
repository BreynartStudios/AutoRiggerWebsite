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


def import_model(filepath):
    """Import model, return (mesh, armature)."""
    filepath = Path(filepath)

    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()

    if filepath.suffix.lower() in (".glb", ".gltf"):
        bpy.ops.import_scene.gltf(filepath=str(filepath))
    elif filepath.suffix.lower() == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(filepath))

    armature = None
    mesh = None

    for obj in bpy.data.objects:
        if obj.type == "ARMATURE":
            armature = obj
        elif obj.type == "MESH":
            mesh = obj

    return mesh, armature


def import_and_retarget_animation(armature, anim_path, anim_name):
    """Import animation and retarget to armature."""
    filepath = Path(anim_path)

    if filepath.suffix.lower() == ".bvh":
        bpy.ops.import_anim.bvh(filepath=str(filepath))
    elif filepath.suffix.lower() == ".fbx":
        bpy.ops.import_scene.fbx(filepath=str(filepath), use_anim=True)

    source = None
    for obj in bpy.context.selected_objects:
        if obj.type == "ARMATURE" and obj != armature:
            source = obj
            break

    if source and source.animation_data:
        action = source.animation_data.action.copy()
        action.name = anim_name

        bpy.data.objects.remove(source, do_unlink=True)
        return action

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
        bpy.ops.export_scene.fbx(
            filepath=str(filepath),
            use_selection=True,
            bake_anim=True,
            bake_anim_use_nla_strips=True,
            bake_anim_use_all_actions=True,
            add_leaf_bones=False,
        )


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

    anim_paths = [p.strip() for p in args.animations.split(",") if p.strip()]
    anim_names = [n.strip() for n in args.names.split(",") if n.strip()]

    mesh, armature = import_model(args.model)

    actions = []
    for path, name in zip(anim_paths, anim_names):
        action = import_and_retarget_animation(armature, path, name)
        if action:
            actions.append(action)

    if actions:
        export_with_animations(args.output, mesh, armature, actions, args.format)
        print(f"Exported {len(actions)} animations to: {args.output}")
    else:
        # Export without animations
        export_with_animations(args.output, mesh, armature, [], args.format)
        print(f"Exported model (no animations) to: {args.output}")


if __name__ == "__main__":
    main()
