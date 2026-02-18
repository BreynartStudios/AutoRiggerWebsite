export default function EnvironmentSetup() {
  return (
    <>
      <ambientLight intensity={0.4} />
      <directionalLight
        position={[5, 8, 5]}
        intensity={1}
        castShadow
        shadow-mapSize-width={2048}
        shadow-mapSize-height={2048}
        shadow-camera-near={0.1}
        shadow-camera-far={50}
      />
      <directionalLight position={[-3, 5, -3]} intensity={0.3} />
      <hemisphereLight
        color="#b1e1ff"
        groundColor="#1a1a2e"
        intensity={0.3}
      />
      <fog attach="fog" args={['#1a1a2e', 10, 30]} />
    </>
  );
}
