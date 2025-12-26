"use client";

import { motion } from "framer-motion";
import { 
  Camera, Settings as SettingsIcon, Download, Lock, User, 
  Zap, BarChart3, Sparkles, Clock, Eye, Volume2, Bell, 
  Gamepad2, Shield, AlertCircle, Check
} from "lucide-react";
import { AppNav } from "@/components/app-nav";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { 
  loadPreferences, 
  savePreferences, 
  UserPreferences,
  AgeGroup,
  FocusStyle,
  SessionLength,
  AGE_GROUP_DEFAULTS
} from "@/lib/user-preferences";
import { useTheme } from "@/components/theme-provider";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

// Age group options
const AGE_GROUPS: { id: AgeGroup; label: string; icon: React.ReactNode }[] = [
  { id: "teen", label: "Student (13-18)", icon: <Sparkles className="w-4 h-4" /> },
  { id: "young-adult", label: "Young Adult (18-30)", icon: <Zap className="w-4 h-4" /> },
  { id: "professional", label: "Professional (30+)", icon: <BarChart3 className="w-4 h-4" /> },
  { id: "senior", label: "Accessible", icon: <User className="w-4 h-4" /> },
];

const FOCUS_STYLES: { id: FocusStyle; label: string }[] = [
  { id: "gamified", label: "Gamified" },
  { id: "data-driven", label: "Data-Driven" },
  { id: "minimal", label: "Minimal" },
];

const SESSION_LENGTHS: { id: SessionLength; label: string }[] = [
  { id: "micro", label: "30 seconds" },
  { id: "short", label: "2 minutes" },
  { id: "standard", label: "5 minutes" },
  { id: "long", label: "10 minutes" },
];

export default function SettingsPage() {
  const { reloadPreferences } = useTheme();
  const [prefs, setPrefs] = useState<UserPreferences>(() => loadPreferences());
  const [saved, setSaved] = useState(false);

  const updatePref = <K extends keyof UserPreferences>(key: K, value: UserPreferences[K]) => {
    const newPrefs = { ...prefs, [key]: value };
    setPrefs(newPrefs);
    savePreferences(newPrefs);
    reloadPreferences();
    
    // Show saved indicator
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
    
    // Sync with backend
    syncWithBackend(newPrefs);
  };
  
  const syncWithBackend = async (newPrefs: Partial<UserPreferences>) => {
    try {
      const token = localStorage.getItem("focus_token");
      if (token) {
        await fetch(`${API_URL}/preferences`, {
          method: "PATCH",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify(newPrefs),
        });
      }
    } catch (e) {
      console.error("Failed to sync preferences:", e);
    }
  };

  const handleExport = () => {
    const userData = {
      preferences: prefs,
      exportedAt: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(userData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `focussprint-settings-${Date.now()}.json`;
    a.click();
  };

  // Toggle component
  const Toggle = ({ 
    enabled, 
    onChange 
  }: { 
    enabled: boolean; 
    onChange: (v: boolean) => void;
  }) => (
    <button
      onClick={() => onChange(!enabled)}
      className={`w-14 h-8 rounded-full transition-all ${
        enabled ? "bg-[#10b981]" : "bg-[#2a2a3e]"
      }`}
    >
      <div
        className={`w-6 h-6 rounded-full bg-white transition-transform ${
          enabled ? "translate-x-7" : "translate-x-1"
        }`}
      />
    </button>
  );

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white">
      <AppNav />

      <div className="pt-32 pb-20 px-6">
        <div className="max-w-3xl mx-auto">
          {/* Header */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-12"
          >
            <div className="inline-flex items-center gap-2 glass px-4 py-2 rounded-full mb-6">
              <SettingsIcon className="w-4 h-4 text-[#06b6d4]" />
              <span className="text-sm text-[#8888a0]">Personalize Your Experience</span>
              {saved && (
                <span className="flex items-center gap-1 text-[#10b981] text-xs">
                  <Check className="w-3 h-3" /> Saved
                </span>
              )}
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-4">
              <span className="gradient-text">Settings</span>
            </h1>
            <p className="text-xl text-[#8888a0]">
              Customize FocusSprint to match how you learn
            </p>
          </motion.div>

          {/* Profile Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="glass rounded-3xl p-8 mb-6"
          >
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <User className="w-5 h-5 text-[#ff6b4a]" />
              Profile
            </h3>
            <div className="space-y-4">
              <div>
                <label className="text-sm text-[#8888a0] mb-2 block">Age Group</label>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {AGE_GROUPS.map((group) => (
                    <button
                      key={group.id}
                      onClick={() => updatePref("ageGroup", group.id)}
                      className={`p-3 rounded-xl text-sm transition-all ${
                        prefs.ageGroup === group.id
                          ? "bg-[#ff6b4a]/20 border-2 border-[#ff6b4a]"
                          : "bg-[#1e1e2e] border-2 border-transparent hover:border-white/10"
                      }`}
                    >
                      <div className="flex items-center gap-2 justify-center">
                        {group.icon}
                        <span>{group.label.split(" ")[0]}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>

          {/* Focus Preferences */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.15 }}
            className="glass rounded-3xl p-8 mb-6"
          >
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Zap className="w-5 h-5 text-[#f59e0b]" />
              Focus Preferences
            </h3>
            <div className="space-y-6">
              <div>
                <label className="text-sm text-[#8888a0] mb-2 block">Experience Style</label>
                <div className="grid grid-cols-3 gap-3">
                  {FOCUS_STYLES.map((style) => (
                    <button
                      key={style.id}
                      onClick={() => updatePref("focusStyle", style.id)}
                      className={`p-4 rounded-xl transition-all ${
                        prefs.focusStyle === style.id
                          ? "bg-[#f59e0b]/20 border-2 border-[#f59e0b]"
                          : "bg-[#1e1e2e] border-2 border-transparent hover:border-white/10"
                      }`}
                    >
                      {style.label}
                    </button>
                  ))}
                </div>
              </div>
              
              <div>
                <label className="text-sm text-[#8888a0] mb-2 block">Default Session Length</label>
                <div className="grid grid-cols-4 gap-3">
                  {SESSION_LENGTHS.map((length) => (
                    <button
                      key={length.id}
                      onClick={() => updatePref("sessionLength", length.id)}
                      className={`p-3 rounded-xl text-sm transition-all ${
                        prefs.sessionLength === length.id
                          ? "bg-[#7c3aed]/20 border-2 border-[#7c3aed]"
                          : "bg-[#1e1e2e] border-2 border-transparent hover:border-white/10"
                      }`}
                    >
                      {length.label}
                    </button>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>

          {/* Display Settings */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="glass rounded-3xl p-8 mb-6"
          >
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Eye className="w-5 h-5 text-[#06b6d4]" />
              Display
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Visual Aids</div>
                  <div className="text-sm text-[#8888a0]">Icons, diagrams, and visual cues</div>
                </div>
                <Toggle 
                  enabled={prefs.visualAidsEnabled} 
                  onChange={(v) => updatePref("visualAidsEnabled", v)} 
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Large Text</div>
                  <div className="text-sm text-[#8888a0]">Increase font size for readability</div>
                </div>
                <Toggle 
                  enabled={prefs.largeTextMode} 
                  onChange={(v) => updatePref("largeTextMode", v)} 
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">High Contrast</div>
                  <div className="text-sm text-[#8888a0]">Enhanced contrast for visibility</div>
                </div>
                <Toggle 
                  enabled={prefs.highContrastMode} 
                  onChange={(v) => updatePref("highContrastMode", v)} 
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Reduced Motion</div>
                  <div className="text-sm text-[#8888a0]">Minimize animations</div>
                </div>
                <Toggle 
                  enabled={prefs.reducedMotion} 
                  onChange={(v) => updatePref("reducedMotion", v)} 
                />
              </div>
            </div>
          </motion.div>

          {/* Focus Features */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.25 }}
            className="glass rounded-3xl p-8 mb-6"
          >
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Shield className="w-5 h-5 text-[#10b981]" />
              Focus Features
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Hyperfocus Guard</div>
                  <div className="text-sm text-[#8888a0]">Force breaks after 45 min</div>
                </div>
                <Toggle 
                  enabled={prefs.hyperfocusGuardEnabled} 
                  onChange={(v) => updatePref("hyperfocusGuardEnabled", v)} 
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Attention Tracking</div>
                  <div className="text-sm text-[#8888a0]">Pause when you look away</div>
                </div>
                <Toggle 
                  enabled={prefs.attentionTrackingEnabled} 
                  onChange={(v) => updatePref("attentionTrackingEnabled", v)} 
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Frustration Detection</div>
                  <div className="text-sm text-[#8888a0]">Suggest breaks when struggling</div>
                </div>
                <Toggle 
                  enabled={prefs.frustrationDetectionEnabled} 
                  onChange={(v) => updatePref("frustrationDetectionEnabled", v)} 
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Quick Sessions</div>
                  <div className="text-sm text-[#8888a0]">Show "Just 30 seconds" option</div>
                </div>
                <Toggle 
                  enabled={prefs.microCommitmentEnabled} 
                  onChange={(v) => updatePref("microCommitmentEnabled", v)} 
                />
              </div>
            </div>
          </motion.div>

          {/* Gamification */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="glass rounded-3xl p-8 mb-6"
          >
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Gamepad2 className="w-5 h-5 text-[#7c3aed]" />
              Gamification
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Coins & Rewards</div>
                  <div className="text-sm text-[#8888a0]">Earn Focus Coins</div>
                </div>
                <Toggle 
                  enabled={prefs.showCoinsAndRewards} 
                  onChange={(v) => updatePref("showCoinsAndRewards", v)} 
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Streaks</div>
                  <div className="text-sm text-[#8888a0]">Track daily consistency</div>
                </div>
                <Toggle 
                  enabled={prefs.showStreaks} 
                  onChange={(v) => updatePref("showStreaks", v)} 
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Mystery Rewards</div>
                  <div className="text-sm text-[#8888a0]">Variable reward animations</div>
                </div>
                <Toggle 
                  enabled={prefs.mysteryRewardsEnabled} 
                  onChange={(v) => updatePref("mysteryRewardsEnabled", v)} 
                />
              </div>
            </div>
          </motion.div>

          {/* Audio */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.35 }}
            className="glass rounded-3xl p-8 mb-6"
          >
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Volume2 className="w-5 h-5 text-[#ec4899]" />
              Audio
            </h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Sound Effects</div>
                  <div className="text-sm text-[#8888a0]">Completion and reward sounds</div>
                </div>
                <Toggle 
                  enabled={prefs.soundEffectsEnabled} 
                  onChange={(v) => updatePref("soundEffectsEnabled", v)} 
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div>
                  <div className="font-medium">Text-to-Speech</div>
                  <div className="text-sm text-[#8888a0]">Read content aloud</div>
                </div>
                <Toggle 
                  enabled={prefs.textToSpeechEnabled} 
                  onChange={(v) => updatePref("textToSpeechEnabled", v)} 
                />
              </div>
            </div>
          </motion.div>

          {/* Export Data */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="glass rounded-3xl p-8 mb-6"
          >
            <div className="flex items-center justify-between">
              <div>
                <h3 className="text-xl font-semibold mb-2">Export Data</h3>
                <p className="text-sm text-[#8888a0]">Download your settings</p>
              </div>
              <Button
                onClick={handleExport}
                className="bg-[#7c3aed] hover:bg-[#8b5cf6] px-6"
              >
                <Download className="w-4 h-4 mr-2" />
                Download
              </Button>
            </div>
          </motion.div>

          {/* Privacy Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.45 }}
            className="glass rounded-3xl p-8"
          >
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Lock className="w-5 h-5 text-[#8888a0]" />
              Privacy
            </h3>
            <div className="space-y-3 text-[#8888a0]">
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-[#10b981] mt-2" />
                <span>All processing happens on your device</span>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-[#10b981] mt-2" />
                <span>No camera footage is ever stored or uploaded</span>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-2 h-2 rounded-full bg-[#10b981] mt-2" />
                <span>Your data stays on your device</span>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
