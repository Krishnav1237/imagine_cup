"use client";

import { useState, useEffect, useRef, useCallback } from "react";

interface FrustrationMetrics {
  rapidClicks: number;
  erraticScrolls: number;
  tabSwitches: number;
  frustrationScore: number;
  isFrustrated: boolean;
}

interface UseFrustrationDetectorOptions {
  /** Clicks per second threshold for "rapid clicking" */
  rapidClickThreshold?: number;
  /** Scroll direction changes per 3 seconds for "erratic scrolling" */
  erraticScrollThreshold?: number;
  /** Overall frustration score threshold (0-100) */
  frustrationThreshold?: number;
  /** Callback when frustration is detected */
  onFrustrationDetected?: (metrics: FrustrationMetrics) => void;
  /** Whether detection is enabled */
  enabled?: boolean;
}

/**
 * Hook to detect user frustration patterns.
 * Monitors rapid clicking, erratic scrolling, and tab switches.
 */
export function useFrustrationDetector({
  rapidClickThreshold = 4,
  erraticScrollThreshold = 6,
  frustrationThreshold = 60,
  onFrustrationDetected,
  enabled = true,
}: UseFrustrationDetectorOptions = {}): FrustrationMetrics {
  const [metrics, setMetrics] = useState<FrustrationMetrics>({
    rapidClicks: 0,
    erraticScrolls: 0,
    tabSwitches: 0,
    frustrationScore: 0,
    isFrustrated: false,
  });
  
  const clickTimestamps = useRef<number[]>([]);
  const scrollDirections = useRef<Array<"up" | "down">>([]);
  const lastScrollY = useRef(0);
  const tabSwitchCount = useRef(0);
  const analysisInterval = useRef<NodeJS.Timeout | null>(null);
  
  // Track clicks
  const handleClick = useCallback(() => {
    if (!enabled) return;
    
    const now = Date.now();
    clickTimestamps.current.push(now);
    
    // Keep only clicks from last 2 seconds
    clickTimestamps.current = clickTimestamps.current.filter(
      (t) => now - t < 2000
    );
  }, [enabled]);
  
  // Track scroll patterns
  const handleScroll = useCallback(() => {
    if (!enabled) return;
    
    const currentY = window.scrollY;
    const direction = currentY > lastScrollY.current ? "down" : "up";
    
    scrollDirections.current.push(direction);
    lastScrollY.current = currentY;
    
    // Keep only last 10 scroll events
    if (scrollDirections.current.length > 10) {
      scrollDirections.current.shift();
    }
  }, [enabled]);
  
  // Track tab visibility changes
  const handleVisibilityChange = useCallback(() => {
    if (!enabled) return;
    
    if (document.visibilityState === "hidden") {
      tabSwitchCount.current++;
    }
  }, [enabled]);
  
  // Count scroll direction changes (erratic scrolling)
  const countErraticScrolls = (): number => {
    const directions = scrollDirections.current;
    let changes = 0;
    
    for (let i = 1; i < directions.length; i++) {
      if (directions[i] !== directions[i - 1]) {
        changes++;
      }
    }
    
    return changes;
  };
  
  // Analyze patterns and calculate frustration score
  const analyzePatterns = useCallback(() => {
    const now = Date.now();
    
    // Count rapid clicks (clicks in last 2 seconds)
    const recentClicks = clickTimestamps.current.filter(
      (t) => now - t < 2000
    ).length;
    
    // Count erratic scrolls
    const erraticScrolls = countErraticScrolls();
    
    // Get tab switches (reset after analysis)
    const tabSwitches = tabSwitchCount.current;
    
    // Calculate frustration score (0-100)
    let score = 0;
    
    // Rapid clicking contribution (max 40 points)
    score += Math.min((recentClicks / rapidClickThreshold) * 40, 40);
    
    // Erratic scrolling contribution (max 30 points)
    score += Math.min((erraticScrolls / erraticScrollThreshold) * 30, 30);
    
    // Tab switching contribution (max 30 points)
    score += Math.min(tabSwitches * 10, 30);
    
    const isFrustrated = score >= frustrationThreshold;
    
    const newMetrics: FrustrationMetrics = {
      rapidClicks: recentClicks,
      erraticScrolls,
      tabSwitches,
      frustrationScore: Math.round(score),
      isFrustrated,
    };
    
    setMetrics(newMetrics);
    
    // Trigger callback if frustrated
    if (isFrustrated && onFrustrationDetected) {
      onFrustrationDetected(newMetrics);
      // Reset after detection to avoid repeated triggers
      clickTimestamps.current = [];
      scrollDirections.current = [];
      tabSwitchCount.current = 0;
    }
    
    // Gradually decay tab switch count
    tabSwitchCount.current = Math.max(0, tabSwitchCount.current - 1);
    
  }, [rapidClickThreshold, erraticScrollThreshold, frustrationThreshold, onFrustrationDetected]);
  
  // Set up event listeners
  useEffect(() => {
    if (!enabled) return;
    
    window.addEventListener("click", handleClick, { passive: true });
    window.addEventListener("scroll", handleScroll, { passive: true });
    document.addEventListener("visibilitychange", handleVisibilityChange);
    
    // Analyze patterns every 3 seconds
    analysisInterval.current = setInterval(analyzePatterns, 3000);
    
    return () => {
      window.removeEventListener("click", handleClick);
      window.removeEventListener("scroll", handleScroll);
      document.removeEventListener("visibilitychange", handleVisibilityChange);
      
      if (analysisInterval.current) {
        clearInterval(analysisInterval.current);
      }
    };
  }, [enabled, handleClick, handleScroll, handleVisibilityChange, analyzePatterns]);
  
  return metrics;
}

/**
 * Frustration intervention messages - Professional language
 */
export const FRUSTRATION_INTERVENTIONS = [
  {
    message: "Hitting friction? A short break often helps. 🌬️",
    action: "Take a 2-minute break",
    actionType: "break",
  },
  {
    message: "This section seems challenging. Try an easier one? 🎯",
    action: "Switch content",
    actionType: "easier",
  },
  {
    message: "Consider stepping back for a moment. 🧠",
    action: "Quick mental reset",
    actionType: "fun",
  },
  {
    message: "Not connecting with this? You can skip ahead. 💡",
    action: "Skip section",
    actionType: "skip",
  },
];

export function getRandomIntervention() {
  return FRUSTRATION_INTERVENTIONS[
    Math.floor(Math.random() * FRUSTRATION_INTERVENTIONS.length)
  ];
}

export default useFrustrationDetector;
