#!/bin/bash
# Download free CMU Motion Capture animations (public domain BVH files)
# Source: https://github.com/una-dinosauria/cmu-mocap
# Original data: Carnegie Mellon University Graphics Lab Motion Capture Database

set -e

BASE_URL="https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/master/data"
ANIM_DIR="$(dirname "$0")/../backend/data/animations"

echo "Downloading CMU MoCap animations to: $ANIM_DIR"

mkdir -p "$ANIM_DIR/locomotion"
mkdir -p "$ANIM_DIR/combat"
mkdir -p "$ANIM_DIR/social"
mkdir -p "$ANIM_DIR/misc"

download() {
    local cmu_path="$1"
    local target="$2"
    local name="$3"
    echo -n "  Downloading $name... "
    if curl -sLf "$BASE_URL/$cmu_path.bvh" -o "$ANIM_DIR/$target"; then
        echo "OK ($(du -h "$ANIM_DIR/$target" | cut -f1))"
        return 0
    else
        echo "FAILED"
        return 1
    fi
}

echo ""
echo "=== Locomotion ==="
download "002/02_01" "locomotion/walk_01.bvh" "Walk 1 (CMU 02_01)"
download "002/02_02" "locomotion/walk_02.bvh" "Walk 2 (CMU 02_02)"
download "035/35_01" "locomotion/walk_03.bvh" "Walk Style (CMU 35_01)"
download "009/09_01" "locomotion/run_01.bvh" "Run 1 (CMU 09_01)"
download "009/09_02" "locomotion/run_02.bvh" "Run 2 (CMU 09_02)"
download "035/35_17" "locomotion/sprint_01.bvh" "Fast Run (CMU 35_17)"
download "016/16_35" "locomotion/jump_01.bvh" "Jump (CMU 16_35)"
download "086/86_10" "locomotion/crouch_walk_01.bvh" "Crouch Walk (CMU 86_10)"
download "086/86_01" "locomotion/idle_01.bvh" "Idle/Stand (CMU 86_01)"
download "016/16_15" "locomotion/jump_forward_01.bvh" "Jump Forward (CMU 16_15)"

echo ""
echo "=== Combat ==="
download "143/143_01" "combat/punch_01.bvh" "Punch 1 (CMU 143_01)"
download "143/143_06" "combat/kick_01.bvh" "Kick (CMU 143_06)"
download "014/14_06" "combat/block_01.bvh" "Block (CMU 14_06)"
download "014/14_14" "combat/hit_react_01.bvh" "Hit React (CMU 14_14)"

echo ""
echo "=== Social ==="
download "005/05_06" "social/dance_01.bvh" "Dance (CMU 05_06)"
download "056/56_05" "social/wave_01.bvh" "Wave/Gesture (CMU 56_05)"

echo ""
echo "=== Misc ==="
download "086/86_02" "misc/pick_up_01.bvh" "Pick Up (CMU 86_02)"
download "002/02_03" "misc/push_01.bvh" "Push/Walk Slow (CMU 02_03)"

echo ""
echo "Done! Downloaded animations to $ANIM_DIR"
echo ""
echo "Note: These are CMU Motion Capture animations (public domain)."
echo "Some motion labels are approximate - CMU files contain general"
echo "motion capture sessions that may include multiple actions."
echo ""
echo "Now rebuild Docker to pick up new files:"
echo "  docker compose up --build -d"
