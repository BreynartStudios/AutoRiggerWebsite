import { useRef, useEffect, useCallback } from 'react';
import { useLoader, useFrame, useThree } from '@react-three/fiber';
import { GLTFLoader } from 'three/examples/jsm/loaders/GLTFLoader.js';
import * as THREE from 'three';
import { useModelStore } from '../../stores/useModelStore';
import { useMarkerStore } from '../../stores/useMarkerStore';
import { useAnimationStore } from '../../stores/useAnimationStore';
import { getFullUrl } from '../../services/api';

export default function CharacterModel() {
  const groupRef = useRef<THREE.Group>(null);
  const mixerRef = useRef<THREE.AnimationMixer | null>(null);

  // Use selectors to avoid re-renders from unrelated store changes
  const model = useModelStore((s) => s.model);
  const riggedModelUrl = useModelStore((s) => s.riggedModelUrl);
  const animatedModelUrl = useModelStore((s) => s.animatedModelUrl);
  const isPlacingMarkers = useMarkerStore((s) => s.isPlacingMarkers);
  const placeMarker = useMarkerStore((s) => s.placeMarker);
  const loopEnabled = useAnimationStore((s) => s.loopEnabled);

  const modelUrl = animatedModelUrl || riggedModelUrl || model?.preview_url;

  const { raycaster, pointer, camera } = useThree();

  // Load model
  const gltf = useLoader(GLTFLoader, modelUrl ? getFullUrl(modelUrl) : '/placeholder.glb', undefined, () => {});

  // Set up animation mixer when gltf changes
  useEffect(() => {
    if (!gltf?.animations?.length) {
      mixerRef.current = null;
      return;
    }

    const mixer = new THREE.AnimationMixer(gltf.scene);
    mixerRef.current = mixer;

    const action = mixer.clipAction(gltf.animations[0]);
    action.play();

    useAnimationStore.getState().setDuration(gltf.animations[0].duration);

    return () => {
      mixer.stopAllAction();
      mixerRef.current = null;
    };
  }, [gltf]);

  // Update loop setting separately (doesn't recreate mixer)
  useEffect(() => {
    if (!mixerRef.current || !gltf?.animations?.length) return;
    const action = mixerRef.current.existingAction(gltf.animations[0]);
    if (action) {
      action.setLoop(loopEnabled ? THREE.LoopRepeat : THREE.LoopOnce, Infinity);
      action.clampWhenFinished = !loopEnabled;
    }
  }, [gltf, loopEnabled]);

  // Update mixer every frame - reads directly from store to avoid re-render loop
  useFrame((_, delta) => {
    if (!mixerRef.current) return;
    const { isPlaying, playbackSpeed } = useAnimationStore.getState();
    if (isPlaying) {
      mixerRef.current.update(delta * playbackSpeed);
    }
    const clip = gltf?.animations?.[0];
    if (clip) {
      const action = mixerRef.current.existingAction(clip);
      if (action) {
        useAnimationStore.getState().setCurrentTime(action.time);
      }
    }
  });

  // Handle click for marker placement
  const handleClick = useCallback(() => {
    if (!isPlacingMarkers || !groupRef.current) return;

    raycaster.setFromCamera(pointer, camera);
    const intersects = raycaster.intersectObject(groupRef.current, true);

    if (intersects.length > 0) {
      const point = intersects[0].point;
      placeMarker([point.x, point.y, point.z]);
    }
  }, [isPlacingMarkers, raycaster, pointer, camera, placeMarker]);

  if (!modelUrl || !gltf) return null;

  return (
    <group ref={groupRef} onClick={handleClick} key={modelUrl}>
      <primitive object={gltf.scene} />
    </group>
  );
}
