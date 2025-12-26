/**
 * User Preferences System
 * Supports age-adaptive UX and personalized focus experience
 */

// ============ Types ============

export type AgeGroup = 'teen' | 'young-adult' | 'professional' | 'senior';

export type FocusStyle = 'gamified' | 'minimal' | 'data-driven';

export type SessionLength = 'micro' | 'short' | 'standard' | 'long';

export type MotivationStyle = 'encouraging' | 'neutral' | 'achievement';

export type ContentDisplayMode = 'text' | 'visual' | 'cards' | 'audio';

export interface UserPreferences {
  // Core preferences
  ageGroup: AgeGroup;
  focusStyle: FocusStyle;
  sessionLength: SessionLength;
  motivationStyle: MotivationStyle;
  
  // Display preferences
  preferredDisplayMode: ContentDisplayMode;
  visualAidsEnabled: boolean;
  highContrastMode: boolean;
  largeTextMode: boolean;
  reducedMotion: boolean;
  
  // Audio preferences
  soundEffectsEnabled: boolean;
  notificationSoundsEnabled: boolean;
  textToSpeechEnabled: boolean;
  
  // Focus features
  hyperfocusGuardEnabled: boolean;
  attentionTrackingEnabled: boolean;
  frustrationDetectionEnabled: boolean;
  microCommitmentEnabled: boolean;
  
  // Gamification
  showCoinsAndRewards: boolean;
  showStreaks: boolean;
  showLeaderboards: boolean;
  mysteryRewardsEnabled: boolean;
}

// ============ Defaults by Age Group ============

export const AGE_GROUP_DEFAULTS: Record<AgeGroup, Partial<UserPreferences>> = {
  'teen': {
    focusStyle: 'gamified',
    sessionLength: 'short',
    motivationStyle: 'encouraging',
    preferredDisplayMode: 'visual',
    visualAidsEnabled: true,
    soundEffectsEnabled: true,
    showCoinsAndRewards: true,
    showStreaks: true,
    showLeaderboards: true,
    mysteryRewardsEnabled: true,
  },
  'young-adult': {
    focusStyle: 'gamified',
    sessionLength: 'standard',
    motivationStyle: 'achievement',
    preferredDisplayMode: 'visual',
    visualAidsEnabled: true,
    soundEffectsEnabled: true,
    showCoinsAndRewards: true,
    showStreaks: true,
    showLeaderboards: false,
    mysteryRewardsEnabled: true,
  },
  'professional': {
    focusStyle: 'data-driven',
    sessionLength: 'standard',
    motivationStyle: 'neutral',
    preferredDisplayMode: 'text',
    visualAidsEnabled: true,
    soundEffectsEnabled: false,
    showCoinsAndRewards: false,
    showStreaks: true,
    showLeaderboards: false,
    mysteryRewardsEnabled: false,
  },
  'senior': {
    focusStyle: 'minimal',
    sessionLength: 'short',
    motivationStyle: 'encouraging',
    preferredDisplayMode: 'text',
    visualAidsEnabled: true,
    highContrastMode: true,
    largeTextMode: true,
    reducedMotion: true,
    soundEffectsEnabled: false,
    showCoinsAndRewards: false,
    showStreaks: false,
    showLeaderboards: false,
    mysteryRewardsEnabled: false,
  },
};

// ============ Default Preferences ============

export const DEFAULT_PREFERENCES: UserPreferences = {
  ageGroup: 'young-adult',
  focusStyle: 'gamified',
  sessionLength: 'standard',
  motivationStyle: 'encouraging',
  
  preferredDisplayMode: 'visual',
  visualAidsEnabled: true,
  highContrastMode: false,
  largeTextMode: false,
  reducedMotion: false,
  
  soundEffectsEnabled: true,
  notificationSoundsEnabled: true,
  textToSpeechEnabled: false,
  
  hyperfocusGuardEnabled: true,
  attentionTrackingEnabled: true,
  frustrationDetectionEnabled: true,
  microCommitmentEnabled: true,
  
  showCoinsAndRewards: true,
  showStreaks: true,
  showLeaderboards: false,
  mysteryRewardsEnabled: true,
};

// ============ Session Length Mappings ============

export const SESSION_LENGTHS: Record<SessionLength, { seconds: number; label: string }> = {
  'micro': { seconds: 30, label: '30 seconds' },
  'short': { seconds: 120, label: '2 minutes' },
  'standard': { seconds: 300, label: '5 minutes' },
  'long': { seconds: 600, label: '10 minutes' },
};

// ============ Helper Functions ============

const STORAGE_KEY = 'focus_user_preferences';

export function loadPreferences(): UserPreferences {
  if (typeof window === 'undefined') return DEFAULT_PREFERENCES;
  
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    if (stored) {
      return { ...DEFAULT_PREFERENCES, ...JSON.parse(stored) };
    }
  } catch (e) {
    console.error('Failed to load preferences:', e);
  }
  
  return DEFAULT_PREFERENCES;
}

export function savePreferences(prefs: Partial<UserPreferences>): UserPreferences {
  const current = loadPreferences();
  const updated = { ...current, ...prefs };
  
  if (typeof window !== 'undefined') {
    try {
      localStorage.setItem(STORAGE_KEY, JSON.stringify(updated));
    } catch (e) {
      console.error('Failed to save preferences:', e);
    }
  }
  
  return updated;
}

export function applyAgeGroupDefaults(ageGroup: AgeGroup): UserPreferences {
  const defaults = AGE_GROUP_DEFAULTS[ageGroup];
  return savePreferences({ ageGroup, ...defaults });
}

export function getSessionDuration(prefs: UserPreferences): number {
  return SESSION_LENGTHS[prefs.sessionLength].seconds;
}

// ============ Feature Flags ============

export function isFeatureEnabled(prefs: UserPreferences, feature: keyof UserPreferences): boolean {
  const value = prefs[feature];
  return typeof value === 'boolean' ? value : true;
}

export function shouldShowGamification(prefs: UserPreferences): boolean {
  return prefs.showCoinsAndRewards || prefs.showStreaks || prefs.mysteryRewardsEnabled;
}

export function getThemeVariant(prefs: UserPreferences): string {
  if (prefs.highContrastMode) return 'high-contrast';
  
  switch (prefs.ageGroup) {
    case 'teen': return 'vibrant';
    case 'young-adult': return 'modern';
    case 'professional': return 'minimal';
    case 'senior': return 'accessible';
    default: return 'modern';
  }
}
