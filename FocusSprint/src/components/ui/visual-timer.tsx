"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface VisualTimerProps {
  /** Duration in seconds */
  duration: number;
  /** Time elapsed in seconds */
  elapsed: number;
  /** Whether the timer is paused */
  isPaused?: boolean;
  /** Size of the timer circle */
  size?: number;
  /** Show time comparison (e.g., "Like 1 song") */
  showComparison?: boolean;
}

/**
 * Visual countdown timer designed for ADHD users.
 * Features a shrinking circle with color transitions to combat time blindness.
 */
export function VisualTimer({
  duration,
  elapsed,
  isPaused = false,
  size = 120,
  showComparison = true,
}: VisualTimerProps) {
  const progress = Math.min(elapsed / duration, 1);
  const remaining = Math.max(duration - elapsed, 0);
  
  // Color transitions: green → yellow → orange → red
  const getProgressColor = (progress: number): string => {
    if (progress < 0.5) return "#10b981"; // green
    if (progress < 0.75) return "#f59e0b"; // yellow/amber
    if (progress < 0.9) return "#f97316"; // orange
    return "#ef4444"; // red
  };
  
  // Time comparison for better understanding
  const getTimeComparison = (seconds: number): string => {
    if (seconds <= 30) return "Half a TikTok";
    if (seconds <= 60) return "Like 1 short video";
    if (seconds <= 180) return "Like 1 song";
    if (seconds <= 300) return "Like 1-2 songs";
    if (seconds <= 600) return "Like a coffee break";
    return "Like a podcast episode";
  };
  
  // Format time as MM:SS
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };
  
  const strokeWidth = 8;
  const radius = (size - strokeWidth) / 2;
  const circumference = 2 * Math.PI * radius;
  const strokeDashoffset = circumference * progress;
  
  return (
    <div className="relative flex flex-col items-center">
      {/* Main circular timer */}
      <div className="relative" style={{ width: size, height: size }}>
        {/* Background circle */}
        <svg
          className="absolute inset-0 transform -rotate-90"
          width={size}
          height={size}
        >
          <circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke="#2a2a3e"
            strokeWidth={strokeWidth}
            fill="none"
          />
          {/* Progress circle with animation */}
          <motion.circle
            cx={size / 2}
            cy={size / 2}
            r={radius}
            stroke={getProgressColor(progress)}
            strokeWidth={strokeWidth}
            fill="none"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: 0 }}
            animate={{ 
              strokeDashoffset,
              stroke: getProgressColor(progress)
            }}
            transition={{ duration: 0.5, ease: "easeOut" }}
          />
        </svg>
        
        {/* Center content */}
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <motion.span 
            className="text-2xl font-bold text-white"
            key={Math.floor(remaining)}
            initial={{ scale: 1.1, opacity: 0.8 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ duration: 0.2 }}
          >
            {formatTime(remaining)}
          </motion.span>
          <span className="text-xs text-[#8888a0]">remaining</span>
        </div>
        
        {/* Pulse animation when almost done */}
        <AnimatePresence>
          {progress > 0.9 && !isPaused && (
            <motion.div
              className="absolute inset-0 rounded-full border-2 border-red-500"
              initial={{ scale: 1, opacity: 0.8 }}
              animate={{ scale: 1.1, opacity: 0 }}
              transition={{ 
                duration: 1, 
                repeat: Infinity,
                ease: "easeOut"
              }}
            />
          )}
        </AnimatePresence>
        
        {/* Paused indicator */}
        <AnimatePresence>
          {isPaused && (
            <motion.div
              className="absolute inset-0 flex items-center justify-center bg-black/50 rounded-full"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
            >
              <span className="text-white text-sm font-medium">PAUSED</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>
      
      {/* Time comparison */}
      {showComparison && (
        <motion.p 
          className="mt-3 text-sm text-[#8888a0] text-center"
          initial={{ opacity: 0, y: 5 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.2 }}
        >
          ⏱️ {getTimeComparison(remaining)}
        </motion.p>
      )}
    </div>
  );
}

/**
 * Minimal inline timer for compact displays
 */
export function InlineTimer({
  duration,
  elapsed,
}: {
  duration: number;
  elapsed: number;
}) {
  const progress = Math.min(elapsed / duration, 1);
  const remaining = Math.max(duration - elapsed, 0);
  
  const formatTime = (seconds: number): string => {
    const mins = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${mins}:${secs.toString().padStart(2, "0")}`;
  };
  
  return (
    <div className="flex items-center gap-2">
      <div className="w-20 h-2 bg-[#2a2a3e] rounded-full overflow-hidden">
        <motion.div
          className="h-full bg-gradient-to-r from-[#10b981] to-[#ff6b4a]"
          initial={{ width: "0%" }}
          animate={{ width: `${progress * 100}%` }}
          transition={{ duration: 0.3 }}
        />
      </div>
      <span className="text-sm text-[#8888a0] font-mono">
        {formatTime(remaining)}
      </span>
    </div>
  );
}

export default VisualTimer;
