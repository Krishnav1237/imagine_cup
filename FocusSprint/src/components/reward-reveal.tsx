"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Coins, Sparkles, Gift, Star, Trophy, Zap } from "lucide-react";

interface MysteryReward {
  tier: string;
  tier_display: string;
  base_coins: number;
  multiplier: number;
  final_coins: number;
  bonus_item: string | null;
  message: string;
  celebration_level: number;
  is_jackpot: boolean;
  show_mystery_animation: boolean;
}

interface RewardRevealProps {
  reward: MysteryReward | null;
  isVisible: boolean;
  onClose: () => void;
}

// Confetti particle component
function ConfettiParticle({ delay, color }: { delay: number; color: string }) {
  const randomX = Math.random() * 400 - 200;
  const randomRotate = Math.random() * 720 - 360;
  
  return (
    <motion.div
      className="absolute w-3 h-3 rounded-sm"
      style={{ backgroundColor: color }}
      initial={{ 
        x: 0, 
        y: 0, 
        opacity: 1, 
        rotate: 0,
        scale: 0
      }}
      animate={{ 
        x: randomX, 
        y: -300 + Math.random() * 100, 
        opacity: 0, 
        rotate: randomRotate,
        scale: [0, 1, 1, 0.5]
      }}
      transition={{ 
        duration: 1.5, 
        delay: delay,
        ease: "easeOut"
      }}
    />
  );
}

/**
 * Reward Reveal Component with mystery animation and celebrations.
 */
export function RewardReveal({ reward, isVisible, onClose }: RewardRevealProps) {
  const [showConfetti, setShowConfetti] = useState(false);
  const [revealStage, setRevealStage] = useState(0);
  
  const confettiColors = ["#ff6b4a", "#f59e0b", "#10b981", "#7c3aed", "#06b6d4"];
  
  // Tier-specific styling
  const tierStyles: Record<string, { color: string; bgColor: string; icon: React.ReactNode }> = {
    common: { 
      color: "#8888a0", 
      bgColor: "rgba(136, 136, 160, 0.1)",
      icon: <Coins className="w-8 h-8" />
    },
    uncommon: { 
      color: "#10b981", 
      bgColor: "rgba(16, 185, 129, 0.1)",
      icon: <Star className="w-8 h-8" />
    },
    rare: { 
      color: "#06b6d4", 
      bgColor: "rgba(6, 182, 212, 0.1)",
      icon: <Sparkles className="w-8 h-8" />
    },
    epic: { 
      color: "#7c3aed", 
      bgColor: "rgba(124, 58, 237, 0.1)",
      icon: <Zap className="w-8 h-8" />
    },
    legendary: { 
      color: "#f59e0b", 
      bgColor: "rgba(245, 158, 11, 0.1)",
      icon: <Trophy className="w-8 h-8" />
    },
  };
  
  useEffect(() => {
    if (!isVisible || !reward) return;
    
    // Stage progression for reveal animation
    const stages = [
      () => setRevealStage(1),  // Show box
      () => setRevealStage(2),  // Open box
      () => setRevealStage(3),  // Show reward
      () => {
        if (reward.celebration_level >= 3) {
          setShowConfetti(true);
        }
      },
    ];
    
    const delays = reward.show_mystery_animation 
      ? [0, 500, 1000, 1200] 
      : [0, 0, 0, 200];
    
    const timers = stages.map((fn, i) => 
      setTimeout(fn, delays[i])
    );
    
    return () => timers.forEach(clearTimeout);
  }, [isVisible, reward]);
  
  // Reset on close
  useEffect(() => {
    if (!isVisible) {
      setRevealStage(0);
      setShowConfetti(false);
    }
  }, [isVisible]);
  
  if (!reward) return null;
  
  const style = tierStyles[reward.tier] || tierStyles.common;
  
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          {/* Backdrop */}
          <div className="absolute inset-0 bg-black/80 backdrop-blur-md" />
          
          {/* Confetti container */}
          {showConfetti && (
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none overflow-hidden">
              {Array.from({ length: 50 }).map((_, i) => (
                <ConfettiParticle
                  key={i}
                  delay={i * 0.02}
                  color={confettiColors[i % confettiColors.length]}
                />
              ))}
            </div>
          )}
          
          {/* Content */}
          <motion.div
            className="relative z-10 max-w-sm mx-4 text-center"
            onClick={(e) => e.stopPropagation()}
            initial={{ scale: 0.8 }}
            animate={{ scale: 1 }}
            transition={{ type: "spring" }}
          >
            {/* Mystery box (stages 1-2) */}
            {reward.show_mystery_animation && revealStage < 3 && (
              <motion.div
                className="relative"
                animate={{
                  scale: revealStage === 2 ? [1, 1.1, 0.8] : 1,
                  rotate: revealStage === 2 ? [0, -5, 5, 0] : 0,
                }}
                transition={{ duration: 0.5 }}
              >
                <div className="w-32 h-32 mx-auto rounded-2xl bg-gradient-to-br from-[#7c3aed] to-[#ff6b4a] flex items-center justify-center">
                  <Gift className="w-16 h-16 text-white" />
                </div>
                <motion.div
                  className="mt-4 text-white text-lg"
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 1, repeat: Infinity }}
                >
                  Opening...
                </motion.div>
              </motion.div>
            )}
            
            {/* Revealed reward (stage 3+) */}
            {revealStage >= 3 && (
              <motion.div
                initial={{ opacity: 0, scale: 0.5, y: 20 }}
                animate={{ opacity: 1, scale: 1, y: 0 }}
                transition={{ type: "spring", bounce: 0.4 }}
              >
                {/* Tier badge */}
                <motion.div
                  className="inline-block px-4 py-1 rounded-full text-sm font-bold mb-4"
                  style={{ 
                    backgroundColor: style.bgColor,
                    color: style.color,
                    border: `2px solid ${style.color}`
                  }}
                  initial={{ scale: 0 }}
                  animate={{ scale: 1 }}
                  transition={{ delay: 0.1, type: "spring" }}
                >
                  {reward.tier_display} REWARD!
                </motion.div>
                
                {/* Icon */}
                <motion.div
                  className="w-24 h-24 mx-auto mb-6 rounded-full flex items-center justify-center"
                  style={{ 
                    backgroundColor: style.bgColor,
                    color: style.color
                  }}
                  initial={{ scale: 0, rotate: -180 }}
                  animate={{ scale: 1, rotate: 0 }}
                  transition={{ delay: 0.2, type: "spring" }}
                >
                  {style.icon}
                </motion.div>
                
                {/* Coins earned */}
                <motion.div
                  className="mb-4"
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ delay: 0.3 }}
                >
                  <div className="flex items-center justify-center gap-2 mb-2">
                    <Coins className="w-8 h-8 text-[#f59e0b]" />
                    <span className="text-4xl font-bold text-[#f59e0b]">
                      +{reward.final_coins}
                    </span>
                  </div>
                  {reward.multiplier > 1 && (
                    <p className="text-sm text-[#8888a0]">
                      {reward.base_coins} × {reward.multiplier}x multiplier
                    </p>
                  )}
                </motion.div>
                
                {/* Bonus item */}
                {reward.bonus_item && (
                  <motion.div
                    className="glass rounded-xl px-4 py-3 mb-4"
                    initial={{ opacity: 0, scale: 0.8 }}
                    animate={{ opacity: 1, scale: 1 }}
                    transition={{ delay: 0.4 }}
                  >
                    <p className="text-sm text-[#8888a0]">Bonus drop:</p>
                    <p className="text-lg text-white font-semibold">
                      {reward.bonus_item}
                    </p>
                  </motion.div>
                )}
                
                {/* Message */}
                <motion.p
                  className="text-xl text-white mb-6"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  transition={{ delay: 0.5 }}
                >
                  {reward.message}
                </motion.p>
                
                {/* Tap to continue */}
                <motion.p
                  className="text-sm text-[#8888a0]"
                  animate={{ opacity: [0.5, 1, 0.5] }}
                  transition={{ duration: 2, repeat: Infinity }}
                >
                  Tap anywhere to continue
                </motion.p>
              </motion.div>
            )}
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/**
 * Streak celebration component
 */
export function StreakCelebration({ 
  streak, 
  isVisible, 
  onClose 
}: { 
  streak: number; 
  isVisible: boolean; 
  onClose: () => void;
}) {
  const milestoneMessages: Record<number, string> = {
    3: "3 days! 🔥 You're building momentum!",
    7: "1 WEEK STREAK! 🏆 You're unstoppable!",
    14: "2 WEEKS! 💎 True dedication!",
    30: "30 DAYS! 👑 You're a legend!",
    100: "💯 DAYS! 🌟 ABSOLUTELY INCREDIBLE!",
  };
  
  const message = milestoneMessages[streak] || `${streak} day streak! 🔥 Keep going!`;
  const isMilestone = streak in milestoneMessages;
  
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className="fixed top-20 left-1/2 z-50"
          initial={{ opacity: 0, y: -50, x: "-50%" }}
          animate={{ opacity: 1, y: 0, x: "-50%" }}
          exit={{ opacity: 0, y: -50, x: "-50%" }}
          onClick={onClose}
        >
          <motion.div
            className={`px-6 py-4 rounded-2xl shadow-2xl ${
              isMilestone 
                ? "bg-gradient-to-r from-[#ff6b4a] to-[#f59e0b]" 
                : "bg-[#1e1e2e] border border-[#ff6b4a]/50"
            }`}
            animate={isMilestone ? { scale: [1, 1.05, 1] } : {}}
            transition={{ duration: 0.5, repeat: isMilestone ? 2 : 0 }}
          >
            <p className={`text-lg font-bold ${isMilestone ? "text-[#0a0a12]" : "text-white"}`}>
              {message}
            </p>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

export default RewardReveal;
