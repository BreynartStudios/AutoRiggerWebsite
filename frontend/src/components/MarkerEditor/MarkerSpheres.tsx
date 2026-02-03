import { useRef } from 'react';
import { useFrame } from '@react-three/fiber';
import * as THREE from 'three';
import { useMarkerStore } from '../../stores/useMarkerStore';

export default function MarkerSpheres() {
  const { markers, selectedMarkerId } = useMarkerStore();
  const placedMarkers = markers.filter((m) => m.placed && m.position);

  return (
    <group>
      {placedMarkers.map((marker) => (
        <MarkerSphere
          key={marker.id}
          position={marker.position!}
          color={marker.color}
          isSelected={marker.id === selectedMarkerId}
        />
      ))}
    </group>
  );
}

function MarkerSphere({
  position,
  color,
  isSelected,
}: {
  position: [number, number, number];
  color: string;
  isSelected: boolean;
}) {
  const meshRef = useRef<THREE.Mesh>(null);
  const pulseRef = useRef(0);

  useFrame((_, delta) => {
    if (!meshRef.current) return;
    if (isSelected) {
      pulseRef.current += delta * 4;
      const scale = 1 + Math.sin(pulseRef.current) * 0.2;
      meshRef.current.scale.setScalar(scale);
    } else {
      meshRef.current.scale.setScalar(1);
    }
  });

  return (
    <mesh ref={meshRef} position={position}>
      <sphereGeometry args={[0.02, 16, 16]} />
      <meshStandardMaterial
        color={color}
        emissive={color}
        emissiveIntensity={isSelected ? 0.8 : 0.3}
        transparent
        opacity={0.9}
      />
    </mesh>
  );
}
