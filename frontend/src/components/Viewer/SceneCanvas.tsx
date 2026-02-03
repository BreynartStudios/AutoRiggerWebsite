import { Canvas } from '@react-three/fiber';
import { OrbitControls, Grid, GizmoHelper, GizmoViewport } from '@react-three/drei';
import { Suspense } from 'react';
import CharacterModel from './CharacterModel';
import EnvironmentSetup from './EnvironmentSetup';
import MarkerSpheres from '../MarkerEditor/MarkerSpheres';
import LoadingOverlay from './LoadingOverlay';
import { useModelStore } from '../../stores/useModelStore';

export default function SceneCanvas() {
  const { model, isProcessing } = useModelStore();

  return (
    <div className="flex-1 relative bg-gray-950">
      {isProcessing && <LoadingOverlay />}

      <Canvas
        camera={{ position: [0, 1.5, 3], fov: 50 }}
        shadows
        className="w-full h-full"
      >
        <Suspense fallback={null}>
          <EnvironmentSetup />

          <Grid
            args={[20, 20]}
            cellSize={0.5}
            cellThickness={0.5}
            cellColor="#2a2a3e"
            sectionSize={2}
            sectionThickness={1}
            sectionColor="#3a3a5e"
            fadeDistance={15}
            fadeStrength={1}
            followCamera={false}
            position={[0, 0, 0]}
          />

          {model && <CharacterModel />}
          <MarkerSpheres />

          <OrbitControls
            makeDefault
            minDistance={0.5}
            maxDistance={10}
            target={[0, 1, 0]}
          />

          <GizmoHelper alignment="bottom-right" margin={[60, 60]}>
            <GizmoViewport
              axisColors={['#f43f5e', '#22c55e', '#3b82f6']}
              labelColor="white"
            />
          </GizmoHelper>
        </Suspense>
      </Canvas>

      {!model && (
        <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
          <div className="text-center space-y-2">
            <p className="text-gray-500 text-lg">No model loaded</p>
            <p className="text-gray-600 text-sm">Upload a 3D model to get started</p>
          </div>
        </div>
      )}
    </div>
  );
}
