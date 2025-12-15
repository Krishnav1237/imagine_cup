"use client";

import { motion } from "framer-motion";
import { Camera, Settings as SettingsIcon, Download, Eye, EyeOff, Lock } from "lucide-react";
import { AppNav } from "@/components/app-nav";
import { useState, useEffect } from "react";
import { Button } from "@/components/ui/button";

export default function SettingsPage() {
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const [learningMode, setLearningMode] = useState<"short" | "detailed">("short");
  const [fontSize, setFontSize] = useState<"small" | "medium" | "large">("medium");

  useEffect(() => {
    const prefs = localStorage.getItem("focusflow_preferences");
    if (prefs) {
      const parsed = JSON.parse(prefs);
      setCameraEnabled(parsed.cameraEnabled || false);
      setLearningMode(parsed.learningMode || "short");
      setFontSize(parsed.fontSize || "medium");
    }
  }, []);

  const savePreferences = () => {
    localStorage.setItem(
      "focusflow_preferences",
      JSON.stringify({
        cameraEnabled,
        learningMode,
        fontSize,
      })
    );
  };

  useEffect(() => {
    savePreferences();
  }, [cameraEnabled, learningMode, fontSize]);

  const handleExport = () => {
    const userData = {
      preferences: { cameraEnabled, learningMode, fontSize },
      completedSprints: localStorage.getItem("focussprint_user"),
      exportedAt: new Date().toISOString(),
    };

    const blob = new Blob([JSON.stringify(userData, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `focusflow-data-${Date.now()}.json`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white">
      <AppNav />

      <div className="pt-32 pb-20 px-6">
        <div className="max-w-3xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-12"
          >
            <div className="inline-flex items-center gap-2 glass px-4 py-2 rounded-full mb-6">
              <SettingsIcon className="w-4 h-4 text-[#06b6d4]" />
              <span className="text-sm text-[#8888a0]">Customize Your Experience</span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-4">
              <span className="gradient-text">Settings</span>
            </h1>
            <p className="text-xl text-[#8888a0]">
              Control how FocusFlow works for you
            </p>
          </motion.div>

          {/* Camera Tracking */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="glass rounded-3xl p-8 mb-6"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-4">
                <div className="w-12 h-12 rounded-xl bg-[#7c3aed]/20 flex items-center justify-center">
                  <Camera className="w-6 h-6 text-[#7c3aed]" />
                </div>
                <div>
                  <h3 className="text-xl font-semibold">Camera Tracking</h3>
                  <p className="text-sm text-[#8888a0]">Pause when you look away</p>
                </div>
              </div>
              <button
                onClick={() => setCameraEnabled(!cameraEnabled)}
                className={`w-14 h-8 rounded-full transition-all ${
                  cameraEnabled ? "bg-[#10b981]" : "bg-[#2a2a3e]"
                }`}
              >
                <div
                  className={`w-6 h-6 rounded-full bg-white transition-transform ${
                    cameraEnabled ? "translate-x-7" : "translate-x-1"
                  }`}
                />
              </button>
            </div>
            <div className="flex items-start gap-2 text-sm text-[#8888a0] bg-[#1e1e2e] rounded-xl p-4">
              <Lock className="w-4 h-4 mt-0.5 flex-shrink-0" />
              <p>
                Camera processing happens entirely on your device. No video is ever uploaded or
                stored.
              </p>
            </div>
          </motion.div>

          {/* Learning Mode */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="glass rounded-3xl p-8 mb-6"
          >
            <h3 className="text-xl font-semibold mb-4">Learning Mode</h3>
            <div className="grid grid-cols-2 gap-4">
              <button
                onClick={() => setLearningMode("short")}
                className={`p-6 rounded-xl text-left transition-all ${
                  learningMode === "short"
                    ? "bg-[#ff6b4a]/20 border-2 border-[#ff6b4a]"
                    : "bg-[#1e1e2e] border-2 border-transparent hover:border-white/10"
                }`}
              >
                <div className="font-semibold mb-2">Short</div>
                <div className="text-sm text-[#8888a0]">Concise explanations, quick examples</div>
              </button>
              <button
                onClick={() => setLearningMode("detailed")}
                className={`p-6 rounded-xl text-left transition-all ${
                  learningMode === "detailed"
                    ? "bg-[#ff6b4a]/20 border-2 border-[#ff6b4a]"
                    : "bg-[#1e1e2e] border-2 border-transparent hover:border-white/10"
                }`}
              >
                <div className="font-semibold mb-2">Detailed</div>
                <div className="text-sm text-[#8888a0]">In-depth coverage, more context</div>
              </button>
            </div>
          </motion.div>

          {/* Font Size */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="glass rounded-3xl p-8 mb-6"
          >
            <h3 className="text-xl font-semibold mb-4">Font Size</h3>
            <div className="flex gap-4">
              {["small", "medium", "large"].map((size) => (
                <button
                  key={size}
                  onClick={() => setFontSize(size as typeof fontSize)}
                  className={`flex-1 p-4 rounded-xl transition-all ${
                    fontSize === size
                      ? "bg-[#06b6d4]/20 border-2 border-[#06b6d4]"
                      : "bg-[#1e1e2e] border-2 border-transparent hover:border-white/10"
                  }`}
                >
                  <div
                    className={`font-semibold ${
                      size === "small" ? "text-sm" : size === "large" ? "text-lg" : "text-base"
                    }`}
                  >
                    {size === "small" ? "A-" : size === "large" ? "A+" : "A"}
                  </div>
                  <div className="text-xs text-[#8888a0] capitalize">{size}</div>
                </button>
              ))}
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
                <p className="text-sm text-[#8888a0]">Download all your learning data</p>
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
            transition={{ duration: 0.6, delay: 0.5 }}
            className="glass rounded-3xl p-8"
          >
            <h3 className="text-xl font-semibold mb-4">Privacy</h3>
            <div className="space-y-3 text-[#8888a0]">
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-[#10b981]/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <div className="w-2 h-2 rounded-full bg-[#10b981]" />
                </div>
                <span>No camera storage - processing happens on your device</span>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-[#10b981]/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <div className="w-2 h-2 rounded-full bg-[#10b981]" />
                </div>
                <span>All data stored locally in your browser</span>
              </div>
              <div className="flex items-start gap-3">
                <div className="w-6 h-6 rounded-full bg-[#10b981]/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                  <div className="w-2 h-2 rounded-full bg-[#10b981]" />
                </div>
                <span>No third-party tracking or analytics</span>
              </div>
            </div>
            <Button
              variant="outline"
              className="w-full mt-6 border-[#2a2a3e] hover:bg-[#1e1e2e]"
            >
              View Privacy Policy
            </Button>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
