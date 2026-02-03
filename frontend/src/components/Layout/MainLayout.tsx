import Header from './Header';
import Sidebar from './Sidebar';
import SceneCanvas from '../Viewer/SceneCanvas';
import PlaybackControls from '../Animation/PlaybackControls';
import { useAnimationStore } from '../../stores/useAnimationStore';

export default function MainLayout() {
  const { currentAnimation } = useAnimationStore();

  return (
    <div className="h-dvh flex flex-col bg-gray-950 text-gray-100">
      <Header />
      <div className="flex flex-1 overflow-hidden">
        <Sidebar />
        <main className="flex-1 flex flex-col relative">
          <SceneCanvas />
          {currentAnimation && (
            <div className="absolute bottom-0 left-0 right-0 z-10">
              <PlaybackControls />
            </div>
          )}
        </main>
      </div>
    </div>
  );
}
