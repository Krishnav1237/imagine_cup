"use client";

import { useState, useEffect, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Eye, EyeOff } from "lucide-react";

interface AttentionOverlayProps {
  /** Whether attention tracking is enabled */
  enabled?: boolean;
  /** Seconds of looking away before blur activates */
  lookAwayThreshold?: number;
  /** Callback when attention is lost */
  onAttentionLost?: () => void;
  /** Callback when attention returns */
  onAttentionReturned?: () => void;
  children: React.ReactNode;
}

const WELCOME_BACK_MESSAGES = [
  "Welcome back! 👋",
  "Good to see you! 😊",
  "There you are! 🌟",
  "Focus restored! ✨",
  "Let's continue! 🚀",
];

/**
 * Attention Overlay Component.
 * Blurs content gently when user looks away and shows a friendly welcome back message.
 * Uses simulated attention for now - can be connected to real eye tracking later.
 */
export function AttentionOverlay({
  enabled = false,
  lookAwayThreshold = 5,
  onAttentionLost,
  onAttentionReturned,
  children,
}: AttentionOverlayProps) {
  const [isAttentive, setIsAttentive] = useState(true);
  const [showWelcomeBack, setShowWelcomeBack] = useState(false);
  const [welcomeMessage, setWelcomeMessage] = useState("");
  const [trackingActive, setTrackingActive] = useState(false);
  
  const lastActivityRef = useRef(Date.now());
  const checkIntervalRef = useRef<NodeJS.Timeout | null>(null);
  
  // Track user activity (mouse movement, clicks, scrolls, key presses)
  const updateActivity = useCallback(() => {
    lastActivityRef.current = Date.now();
    
    if (!isAttentive) {
      // User returned
      setIsAttentive(true);
      setShowWelcomeBack(true);
      setWelcomeMessage(
        WELCOME_BACK_MESSAGES[Math.floor(Math.random() * WELCOME_BACK_MESSAGES.length)]
      );
      onAttentionReturned?.();
      
      // Hide welcome message after 2 seconds
      setTimeout(() => setShowWelcomeBack(false), 2000);
    }
  }, [isAttentive, onAttentionReturned]);
  
  // Set up activity listeners
  useEffect(() => {
    if (!enabled) return;
    
    const events = ["mousemove", "mousedown", "keydown", "scroll", "touchstart"];
    
    events.forEach((event) => {
      window.addEventListener(event, updateActivity, { passive: true });
    });
    
    // Start tracking after short delay
    const startTimeout = setTimeout(() => setTrackingActive(true), 3000);
    
    return () => {
      events.forEach((event) => {
        window.removeEventListener(event, updateActivity);
      });
      clearTimeout(startTimeout);
    };
  }, [enabled, updateActivity]);
  
  // Check for inactivity
  useEffect(() => {
    if (!enabled || !trackingActive) return;
    
    checkIntervalRef.current = setInterval(() => {
      const inactiveDuration = (Date.now() - lastActivityRef.current) / 1000;
      
      if (inactiveDuration >= lookAwayThreshold && isAttentive) {
        setIsAttentive(false);
        onAttentionLost?.();
      }
    }, 1000);
    
    return () => {
      if (checkIntervalRef.current) {
        clearInterval(checkIntervalRef.current);
      }
    };
  }, [enabled, trackingActive, lookAwayThreshold, isAttentive, onAttentionLost]);
  
  if (!enabled) {
    return <>{children}</>;
  }
  
  return (
    <div className="relative">
      {/* Main content with conditional blur */}
      <motion.div
        animate={{
          filter: isAttentive ? "blur(0px)" : "blur(8px)",
          opacity: isAttentive ? 1 : 0.7,
        }}
        transition={{ duration: 0.5 }}
      >
        {children}
      </motion.div>
      
      {/* Inattention overlay */}
      <AnimatePresence>
        {!isAttentive && (
          <motion.div
            className="absolute inset-0 flex items-center justify-center pointer-events-none"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
          >
            <motion.div
              className="bg-[#0a0a12]/90 backdrop-blur-sm rounded-2xl p-8 text-center"
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              transition={{ type: "spring" }}
            >
              <EyeOff className="w-12 h-12 text-[#8888a0] mx-auto mb-4" />
              <p className="text-xl text-white font-medium mb-2">
                Taking a moment? 🤔
              </p>
              <p className="text-[#8888a0]">
                Move your mouse or tap to continue
              </p>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Welcome back toast */}
      <AnimatePresence>
        {showWelcomeBack && (
          <motion.div
            className="fixed top-24 left-1/2 z-50"
            initial={{ opacity: 0, y: -20, x: "-50%" }}
            animate={{ opacity: 1, y: 0, x: "-50%" }}
            exit={{ opacity: 0, y: -20, x: "-50%" }}
          >
            <div className="bg-[#10b981] text-white px-6 py-3 rounded-full shadow-lg flex items-center gap-2">
              <Eye className="w-5 h-5" />
              <span className="font-medium">{welcomeMessage}</span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Tracking indicator (subtle) */}
      {trackingActive && (
        <div className="fixed bottom-4 right-4 z-40">
          <div className="flex items-center gap-2 bg-[#1e1e2e] px-3 py-2 rounded-full text-xs text-[#8888a0]">
            <div className={`w-2 h-2 rounded-full ${isAttentive ? "bg-[#10b981]" : "bg-[#f59e0b]"}`} />
            <span>Focus tracking {isAttentive ? "active" : "paused"}</span>
          </div>
        </div>
      )}
    </div>
  );
}

export default AttentionOverlay;
