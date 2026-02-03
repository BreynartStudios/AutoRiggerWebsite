import { create } from 'zustand';
import type { Animation, AnimationCategory } from '../types/animation';

interface AnimationState {
  animations: Animation[];
  categories: AnimationCategory[];
  selectedCategory: AnimationCategory | null;
  searchQuery: string;
  myAnimations: Animation[];
  currentAnimation: Animation | null;
  isPlaying: boolean;
  playbackSpeed: number;
  loopEnabled: boolean;
  currentTime: number;
  duration: number;

  setAnimations: (animations: Animation[], categories: AnimationCategory[]) => void;
  setSelectedCategory: (cat: AnimationCategory | null) => void;
  setSearchQuery: (query: string) => void;
  addToMyAnimations: (anim: Animation) => void;
  removeFromMyAnimations: (id: string) => void;
  setCurrentAnimation: (anim: Animation | null) => void;
  setIsPlaying: (playing: boolean) => void;
  togglePlayback: () => void;
  setPlaybackSpeed: (speed: number) => void;
  setLoopEnabled: (enabled: boolean) => void;
  setCurrentTime: (time: number) => void;
  setDuration: (duration: number) => void;
  getFilteredAnimations: () => Animation[];
}

export const useAnimationStore = create<AnimationState>((set, get) => ({
  animations: [],
  categories: [],
  selectedCategory: null,
  searchQuery: '',
  myAnimations: [],
  currentAnimation: null,
  isPlaying: false,
  playbackSpeed: 1,
  loopEnabled: true,
  currentTime: 0,
  duration: 0,

  setAnimations: (animations, categories) =>
    set({ animations, categories: categories as AnimationCategory[] }),
  setSelectedCategory: (selectedCategory) => set({ selectedCategory }),
  setSearchQuery: (searchQuery) => set({ searchQuery }),

  addToMyAnimations: (anim) => {
    const { myAnimations } = get();
    if (!myAnimations.find((a) => a.id === anim.id)) {
      set({ myAnimations: [...myAnimations, anim] });
    }
  },

  removeFromMyAnimations: (id) =>
    set({ myAnimations: get().myAnimations.filter((a) => a.id !== id) }),

  setCurrentAnimation: (anim) => set({ currentAnimation: anim, currentTime: 0, isPlaying: !!anim }),
  setIsPlaying: (isPlaying) => set({ isPlaying }),
  togglePlayback: () => set({ isPlaying: !get().isPlaying }),
  setPlaybackSpeed: (playbackSpeed) => set({ playbackSpeed }),
  setLoopEnabled: (loopEnabled) => set({ loopEnabled }),
  setCurrentTime: (currentTime) => set({ currentTime }),
  setDuration: (duration) => set({ duration }),

  getFilteredAnimations: () => {
    const { animations, selectedCategory, searchQuery } = get();
    let filtered = animations;
    if (selectedCategory) {
      filtered = filtered.filter((a) => a.category === selectedCategory);
    }
    if (searchQuery.trim()) {
      const q = searchQuery.toLowerCase();
      filtered = filtered.filter(
        (a) =>
          a.name.toLowerCase().includes(q) ||
          a.tags.some((t) => t.toLowerCase().includes(q))
      );
    }
    return filtered;
  },
}));
