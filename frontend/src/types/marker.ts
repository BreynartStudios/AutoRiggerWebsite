export type MarkerID =
  | 'chin'
  | 'wrist_l'
  | 'wrist_r'
  | 'elbow_l'
  | 'elbow_r'
  | 'knee_l'
  | 'knee_r'
  | 'groin';

export interface Marker {
  id: MarkerID;
  name: string;
  color: string;
  position: [number, number, number] | null;
  placed: boolean;
}

export const MARKER_DEFINITIONS: Record<MarkerID, { name: string; color: string }> = {
  chin: { name: 'Chin', color: '#FF0000' },
  wrist_l: { name: 'Left Wrist', color: '#00FF00' },
  wrist_r: { name: 'Right Wrist', color: '#0000FF' },
  elbow_l: { name: 'Left Elbow', color: '#FFFF00' },
  elbow_r: { name: 'Right Elbow', color: '#FF00FF' },
  knee_l: { name: 'Left Knee', color: '#00FFFF' },
  knee_r: { name: 'Right Knee', color: '#FFA500' },
  groin: { name: 'Groin / Pelvis', color: '#FFFFFF' },
};

export const MARKER_ORDER: MarkerID[] = [
  'chin',
  'groin',
  'wrist_l',
  'wrist_r',
  'elbow_l',
  'elbow_r',
  'knee_l',
  'knee_r',
];
