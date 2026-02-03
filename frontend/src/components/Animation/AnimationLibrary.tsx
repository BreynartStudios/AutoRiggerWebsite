import { useEffect } from 'react';
import { useAnimationStore } from '../../stores/useAnimationStore';
import { useModelStore } from '../../stores/useModelStore';
import { fetchAnimations, applyAnimation } from '../../services/api';
import type { AnimationCategory } from '../../types/animation';
import { CATEGORY_LABELS } from '../../types/animation';
import AnimationCard from './AnimationCard';

export default function AnimationLibrary() {
  const {
    categories,
    selectedCategory,
    searchQuery,
    setAnimations,
    setSelectedCategory,
    setSearchQuery,
    getFilteredAnimations,
    setCurrentAnimation,
    addToMyAnimations,
  } = useAnimationStore();
  const { model, setAnimatedModelUrl } = useModelStore();

  useEffect(() => {
    fetchAnimations()
      .then((data) => setAnimations(data.animations, data.categories as AnimationCategory[]))
      .catch(() => {});
  }, [setAnimations]);

  const filteredAnimations = getFilteredAnimations();

  const handlePreview = async (animId: string) => {
    if (!model) return;
    const anim = filteredAnimations.find((a) => a.id === animId);
    if (!anim) return;

    setCurrentAnimation(anim);

    try {
      const result = await applyAnimation({
        model_id: model.model_id,
        animation_id: animId,
      });
      setAnimatedModelUrl(result.animated_model_url);
    } catch {
      // Preview failed, but animation card was still selected
    }
  };

  const handleAdd = (animId: string) => {
    const anim = filteredAnimations.find((a) => a.id === animId);
    if (anim) addToMyAnimations(anim);
  };

  return (
    <div className="space-y-3">
      <h2 className="text-sm font-semibold text-white uppercase tracking-wider">
        Animation Library
      </h2>

      <input
        type="text"
        placeholder="Search animations..."
        value={searchQuery}
        onChange={(e) => setSearchQuery(e.target.value)}
        className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-200 placeholder-gray-500 focus:outline-none focus:border-sky-500 transition-colors"
      />

      <div className="flex flex-wrap gap-1">
        <CategoryTab
          label="All"
          active={!selectedCategory}
          onClick={() => setSelectedCategory(null)}
        />
        {categories.map((cat) => (
          <CategoryTab
            key={cat}
            label={CATEGORY_LABELS[cat] || cat}
            active={selectedCategory === cat}
            onClick={() => setSelectedCategory(cat)}
          />
        ))}
      </div>

      <div className="grid grid-cols-2 gap-2 max-h-60 overflow-y-auto pr-1">
        {filteredAnimations.map((anim) => (
          <AnimationCard
            key={anim.id}
            animation={anim}
            onPreview={() => handlePreview(anim.id)}
            onAdd={() => handleAdd(anim.id)}
          />
        ))}
        {filteredAnimations.length === 0 && (
          <p className="col-span-2 text-sm text-gray-500 text-center py-4">
            No animations found
          </p>
        )}
      </div>
    </div>
  );
}

function CategoryTab({
  label,
  active,
  onClick,
}: {
  label: string;
  active: boolean;
  onClick: () => void;
}) {
  return (
    <button
      onClick={onClick}
      className={`text-xs px-2.5 py-1 rounded-full transition-colors ${
        active
          ? 'bg-sky-500 text-white'
          : 'bg-gray-800 text-gray-400 hover:text-gray-200'
      }`}
    >
      {label}
    </button>
  );
}
