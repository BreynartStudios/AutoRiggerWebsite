import { useAnimationStore } from '../../stores/useAnimationStore';

export default function MyAnimationsList() {
  const { myAnimations, removeFromMyAnimations, setCurrentAnimation } =
    useAnimationStore();

  if (myAnimations.length === 0) return null;

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
          My Animations
        </h2>
        <span className="text-xs text-gray-500">{myAnimations.length} added</span>
      </div>
      <div className="space-y-1">
        {myAnimations.map((anim) => (
          <div
            key={anim.id}
            className="flex items-center gap-2 px-3 py-2 bg-gray-800 rounded-lg group"
          >
            <button
              onClick={() => setCurrentAnimation(anim)}
              className="flex-1 text-left text-sm text-gray-300 hover:text-white transition-colors truncate"
            >
              {anim.name}
            </button>
            <span className="text-xs text-gray-500 shrink-0">
              {anim.duration_seconds.toFixed(1)}s
            </span>
            <button
              onClick={() => removeFromMyAnimations(anim.id)}
              className="text-gray-600 hover:text-red-400 transition-colors opacity-0 group-hover:opacity-100 text-xs shrink-0"
              title="Remove"
            >
              x
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
