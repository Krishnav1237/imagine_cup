"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Coffee, Droplets, StretchVertical, Brain, Heart, X } from "lucide-react";
import { Button } from "@/components/ui/button";

interface HyperfocusGuardProps {
  /** Threshold in minutes before triggering break (default: 45) */
  thresholdMinutes?: number;
  /** Minimum time break overlay shows before dismiss (default: 60 seconds) */
  minBreakSeconds?: number;
  /** Callback when break is taken */
  onBreakTaken?: () => void;
  /** Whether the guard is enabled */
  enabled?: boolean;
  children: React.ReactNode;
}

const BREAK_ACTIVITIES = [
  { icon: Droplets, text: "Hydrate – grab some water or tea 💧", color: "#06b6d4" },
  { icon: Coffee, text: "Step away for a quick snack 🍎", color: "#f59e0b" },
  { icon: StretchVertical, text: "Stand up and stretch for a minute 🧘", color: "#10b981" },
  { icon: Brain, text: "Look away from the screen – rest your eyes 👀", color: "#7c3aed" },
  { icon: Heart, text: "Take 5 slow breaths 🌬️", color: "#ec4899" },
];

const ENCOURAGEMENT_MESSAGES = [
  "Extended focus is impressive, but sustainable performance requires breaks. 📊",
  "Research shows breaks improve retention and productivity. 📈",
  "Your brain consolidates learning during rest periods. 🧠",
  "Professionals who take breaks outperform those who don't. 💼",
  "Step away now to come back sharper. ⚡",
];

/**
 * Hyperfocus Protection Guard.
 * Wraps content and shows a forced break overlay after continuous use.
 */
export function HyperfocusGuard({
  thresholdMinutes = 45,
  minBreakSeconds = 60,
  onBreakTaken,
  enabled = true,
  children,
}: HyperfocusGuardProps) {
  const [sessionStart] = useState(() => Date.now());
  const [showBreakOverlay, setShowBreakOverlay] = useState(false);
  const [dismissCountdown, setDismissCountdown] = useState(minBreakSeconds);
  const [selectedActivity, setSelectedActivity] = useState(0);
  const [encouragement, setEncouragement] = useState("");
  
  const intervalRef = useRef<NodeJS.Timeout | null>(null);
  
  // Check session duration
  useEffect(() => {
    if (!enabled) return;
    
    const checkDuration = () => {
      const elapsed = (Date.now() - sessionStart) / 1000 / 60; // minutes
      if (elapsed >= thresholdMinutes && !showBreakOverlay) {
        // Trigger break
        setShowBreakOverlay(true);
        setDismissCountdown(minBreakSeconds);
        setSelectedActivity(Math.floor(Math.random() * BREAK_ACTIVITIES.length));
        setEncouragement(
          ENCOURAGEMENT_MESSAGES[Math.floor(Math.random() * ENCOURAGEMENT_MESSAGES.length)]
        );
      }
    };
    
    intervalRef.current = setInterval(checkDuration, 30000); // Check every 30s
    
    return () => {
      if (intervalRef.current) clearInterval(intervalRef.current);
    };
  }, [enabled, sessionStart, thresholdMinutes, showBreakOverlay, minBreakSeconds]);
  
  // Countdown for dismiss button
  useEffect(() => {
    if (!showBreakOverlay || dismissCountdown <= 0) return;
    
    const timer = setInterval(() => {
      setDismissCountdown((prev) => Math.max(0, prev - 1));
    }, 1000);
    
    return () => clearInterval(timer);
  }, [showBreakOverlay, dismissCountdown]);
  
  const handleDismiss = useCallback(() => {
    if (dismissCountdown > 0) return;
    setShowBreakOverlay(false);
    onBreakTaken?.();
  }, [dismissCountdown, onBreakTaken]);
  
  const activity = BREAK_ACTIVITIES[selectedActivity];
  const ActivityIcon = activity.icon;
  
  return (
    <>
      {children}
      
      <AnimatePresence>
        {showBreakOverlay && (
          <motion.div
            className="fixed inset-0 z-50 flex items-center justify-center"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            {/* Backdrop with blur */}
            <div className="absolute inset-0 bg-black/80 backdrop-blur-md" />
            
            {/* Content */}
            <motion.div
              className="relative z-10 max-w-md mx-4 text-center"
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              transition={{ delay: 0.1, type: "spring" }}
            >
              {/* Header */}
              <motion.div
                initial={{ scale: 0 }}
                animate={{ scale: 1 }}
                transition={{ delay: 0.2, type: "spring" }}
                className="w-20 h-20 mx-auto mb-6 rounded-full flex items-center justify-center"
                style={{ backgroundColor: `${activity.color}20` }}
              >
                <ActivityIcon 
                  className="w-10 h-10" 
                  style={{ color: activity.color }} 
                />
              </motion.div>
              
              <motion.h2
                className="text-3xl font-bold text-white mb-4"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.3 }}
              >
                Time for a Break! 🌟
              </motion.h2>
              
              <motion.p
                className="text-lg text-[#8888a0] mb-6"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.4 }}
              >
                You&apos;ve been focused for <span className="text-[#ff6b4a] font-semibold">{thresholdMinutes}+ minutes</span>.
                Your brain deserves a rest!
              </motion.p>
              
              {/* Activity suggestion */}
              <motion.div
                className="glass rounded-2xl p-6 mb-6"
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.5 }}
              >
                <p className="text-xl text-white font-medium mb-2">
                  {activity.text}
                </p>
                <p className="text-sm text-[#8888a0]">
                  {encouragement}
                </p>
              </motion.div>
              
              {/* Timer or dismiss */}
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.6 }}
              >
                {dismissCountdown > 0 ? (
                  <div className="flex flex-col items-center gap-2">
                    <p className="text-[#8888a0]">
                      Take a moment... you can continue in
                    </p>
                    <div className="text-4xl font-bold text-white">
                      {dismissCountdown}s
                    </div>
                    <p className="text-xs text-[#8888a0]">
                      (This is for your own good! 💜)
                    </p>
                  </div>
                ) : (
                  <Button
                    onClick={handleDismiss}
                    className="bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold px-8 py-3 rounded-xl"
                  >
                    I&apos;m Refreshed! Continue Learning →
                  </Button>
                )}
              </motion.div>
              
              {/* Session stats */}
              <motion.div
                className="mt-8 pt-6 border-t border-white/10"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.7 }}
              >
                <p className="text-xs text-[#8888a0]">
                  🎯 Your focus session: {thresholdMinutes}+ minutes | 
                  🧠 Break frequency is key to long-term learning
                </p>
              </motion.div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  );
}

/**
 * Hook to manually trigger break overlay
 */
export function useHyperfocusBreak() {
  const [showBreak, setShowBreak] = useState(false);
  
  const triggerBreak = useCallback(() => setShowBreak(true), []);
  const dismissBreak = useCallback(() => setShowBreak(false), []);
  
  return { showBreak, triggerBreak, dismissBreak };
}

export default HyperfocusGuard;
