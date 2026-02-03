import type { Animation } from '../../types/animation';
import { useAnimationStore } from '../../stores/useAnimationStore';

interface AnimationCardProps {
  animation: Animation;
  onPreview: () => void;
  onAdd: () => void;
}

export default function AnimationCard({ animation, onPreview, onAdd }: AnimationCardProps) {
  const { currentAnimation, myAnimations } = useAnimationStore();
  const isActive = currentAnimation?.id === animation.id;
  const isAdded = myAnimations.some((a) => a.id === animation.id);

  return (
    <div
      onClick={onPreview}
      className={`group relative bg-gray-800 rounded-lg overflow-hidden cursor-pointer transition-all hover:ring-1 hover:ring-sky-500/50 ${
        isActive ? 'ring-2 ring-sky-500' : ''
      }`}
    >
      <div className="aspect-square bg-gray-750 flex items-center justify-center">
        <div className="text-2xl text-gray-600 group-hover:text-gray-400 transition-colors">
          {getCategoryIcon(animation.category)}
        </div>
      </div>
      <div className="p-2">
        <p className="text-xs font-medium text-gray-200 truncate">{animation.name}</p>
        <p className="text-xs text-gray-500">{animation.duration_seconds.toFixed(1)}s</p>
      </div>
      <button
        onClick={(e) => {
          e.stopPropagation();
          onAdd();
        }}
        disabled={isAdded}
        className={`absolute top-1.5 right-1.5 w-6 h-6 rounded-full text-xs font-bold flex items-center justify-center transition-all ${
          isAdded
            ? 'bg-emerald-500 text-white'
            : 'bg-gray-900/80 text-gray-300 hover:bg-sky-500 hover:text-white opacity-0 group-hover:opacity-100'
        }`}
        title={isAdded ? 'Added' : 'Add to my animations'}
      >
        {isAdded ? '\u2713' : '+'}
      </button>
    </div>
  );
}

function getCategoryIcon(category: string): string {
  switch (category) {
    case 'locomotion':
      return '\u{1F3C3}';
    case 'combat':
      return '\u{1F94A}';
    case 'social':
      return '\u{1F44B}';
    default:
      return '\u{1F3AC}';
  }
}
