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

  const { model, riggedModelUrl, animatedModelUrl } = useModelStore();
  const { isPlacingMarkers, placeMarker } = useMarkerStore();
  const { isPlaying, playbackSpeed, loopEnabled, setCurrentTime, setDuration } =
    useAnimationStore();

  const modelUrl = animatedModelUrl || riggedModelUrl || model?.preview_url;

  const { raycaster, pointer, camera } = useThree();

  // Load model
  const gltf = useLoader(GLTFLoader, modelUrl ? getFullUrl(modelUrl) : '/placeholder.glb', undefined, () => {});

  // Set up animations
  useEffect(() => {
    if (!gltf || !groupRef.current) return;

    if (gltf.animations.length > 0) {
      const mixer = new THREE.AnimationMixer(gltf.scene);
      mixerRef.current = mixer;

      const action = mixer.clipAction(gltf.animations[0]);
      action.setLoop(loopEnabled ? THREE.LoopRepeat : THREE.LoopOnce, Infinity);
      action.clampWhenFinished = !loopEnabled;

      if (isPlaying) {
        action.play();
      }

      setDuration(gltf.animations[0].duration);

      return () => {
        mixer.stopAllAction();
        mixerRef.current = null;
      };
    }
  }, [gltf, loopEnabled, isPlaying, setDuration]);

  // Update mixer
  useFrame((_, delta) => {
    if (mixerRef.current && isPlaying) {
      mixerRef.current.update(delta * playbackSpeed);
      const action = mixerRef.current.existingAction(gltf.animations[0]);
      if (action) {
        setCurrentTime(action.time);
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
    <group ref={groupRef} onClick={handleClick}>
      <primitive object={gltf.scene} />
    </group>
  );
}
