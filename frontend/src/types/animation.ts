export interface Animation {
  id: string;
  name: string;
  category: AnimationCategory;
  duration_seconds: number;
  thumbnail_url: string;
  preview_url: string;
  loop: boolean;
  tags: string[];
  description: string;
}

export type AnimationCategory = 'locomotion' | 'combat' | 'social' | 'misc';

export const CATEGORY_LABELS: Record<AnimationCategory, string> = {
  locomotion: 'Locomotion',
  combat: 'Combat',
  social: 'Social',
  misc: 'Misc',
};
