#!/bin/bash
# Backend entrypoint: ensure animation BVH files exist, then start server

set -e

ANIM_DIR="/app/data/animations"
BASE_URL="https://raw.githubusercontent.com/una-dinosauria/cmu-mocap/master/data"

# Check if BVH files need downloading
bvh_count=$(find "$ANIM_DIR" -name "*.bvh" 2>/dev/null | wc -l)

if [ "$bvh_count" -lt 5 ]; then
    echo "[entrypoint] Found only $bvh_count BVH files. Downloading CMU MoCap animations..."

    mkdir -p "$ANIM_DIR/locomotion" "$ANIM_DIR/combat" "$ANIM_DIR/social" "$ANIM_DIR/misc"

    download() {
        local cmu_path="$1"
        local target="$2"
        local name="$3"
        if [ -f "$ANIM_DIR/$target" ]; then
            echo "  [skip] $name (already exists)"
            return 0
        fi
        echo -n "  Downloading $name... "
        if curl -sLf --connect-timeout 10 --max-time 30 "$BASE_URL/$cmu_path.bvh" -o "$ANIM_DIR/$target"; then
            echo "OK"
        else
            echo "FAILED (non-fatal)"
        fi
    }

    download "002/02_01" "locomotion/walk_01.bvh" "Walk 1"
    download "002/02_02" "locomotion/walk_02.bvh" "Walk 2"
    download "035/35_01" "locomotion/walk_03.bvh" "Walk Style"
    download "009/09_01" "locomotion/run_01.bvh" "Run 1"
    download "009/09_02" "locomotion/run_02.bvh" "Run 2"
    download "035/35_17" "locomotion/sprint_01.bvh" "Fast Run"
    download "016/16_35" "locomotion/jump_01.bvh" "Jump"
    download "086/86_10" "locomotion/crouch_walk_01.bvh" "Crouch Walk"
    download "086/86_01" "locomotion/idle_01.bvh" "Idle/Stand"
    download "016/16_15" "locomotion/jump_forward_01.bvh" "Jump Forward"
    download "143/143_01" "combat/punch_01.bvh" "Punch"
    download "143/143_06" "combat/kick_01.bvh" "Kick"
    download "014/14_06" "combat/block_01.bvh" "Block"
    download "014/14_14" "combat/hit_react_01.bvh" "Hit React"
    download "005/05_06" "social/dance_01.bvh" "Dance"
    download "056/56_05" "social/wave_01.bvh" "Wave"
    download "086/86_02" "misc/pick_up_01.bvh" "Pick Up"
    download "002/02_03" "misc/push_01.bvh" "Push"

    bvh_count=$(find "$ANIM_DIR" -name "*.bvh" 2>/dev/null | wc -l)
    echo "[entrypoint] $bvh_count BVH files now available."
else
    echo "[entrypoint] Found $bvh_count BVH animation files."
fi

echo "[entrypoint] Starting uvicorn..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
