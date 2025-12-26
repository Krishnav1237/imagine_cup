"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Play, Clock, Sparkles, ArrowRight, Trophy } from "lucide-react";
import { Button } from "@/components/ui/button";

interface MicroCommitmentProps {
  /** Content title */
  title: string;
  /** Full duration in seconds */
  fullDuration: number;
  /** Callback when user starts micro session */
  onStartMicro: () => void;
  /** Callback when user starts full session */
  onStartFull: () => void;
  /** Whether component is visible */
  isVisible: boolean;
}

/**
 * Micro-commitment prompt for ADHD users.
 * Offers "Just 30 seconds" option to lower activation energy.
 */
export function MicroCommitmentPrompt({
  title,
  fullDuration,
  onStartMicro,
  onStartFull,
  isVisible,
}: MicroCommitmentProps) {
  const [selectedOption, setSelectedOption] = useState<"micro" | "full" | null>(null);
  
  const formatDuration = (seconds: number) => {
    if (seconds < 60) return `${seconds}s`;
    const mins = Math.floor(seconds / 60);
    return `${mins} min`;
  };
  
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center bg-[#0a0a12]/95 backdrop-blur-lg"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        >
          <motion.div
            className="max-w-lg mx-4 text-center"
            initial={{ scale: 0.9, y: 20 }}
            animate={{ scale: 1, y: 0 }}
            transition={{ type: "spring", delay: 0.1 }}
          >
            {/* Header */}
            <motion.div
              initial={{ opacity: 0, y: 10 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.2 }}
            >
              <h2 className="text-2xl md:text-3xl font-bold text-white mb-2">
                How much time do you have?
              </h2>
              <p className="text-[#8888a0] mb-8">
                {title}
              </p>
            </motion.div>
            
            {/* Option cards */}
            <div className="grid gap-4 mb-8">
              {/* Micro option (Primary - Lower the barrier) */}
              <motion.button
                onClick={() => {
                  setSelectedOption("micro");
                  setTimeout(onStartMicro, 300);
                }}
                className={`group relative glass rounded-2xl p-6 text-left transition-all hover:border-[#ff6b4a]/50 ${
                  selectedOption === "micro" ? "border-[#ff6b4a] ring-2 ring-[#ff6b4a]/30" : ""
                }`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.3 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-start gap-4">
                  <div className="p-3 rounded-xl bg-[#ff6b4a]/20">
                    <Sparkles className="w-6 h-6 text-[#ff6b4a]" />
                  </div>
                  <div className="flex-1">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="text-xl font-semibold text-white">
                        Quick session (30 seconds)
                      </h3>
                      <span className="px-2 py-0.5 bg-[#ff6b4a] text-[#0a0a12] text-xs font-semibold rounded-full">
                        START HERE
                      </span>
                    </div>
                    <p className="text-[#8888a0] text-sm">
                      Low commitment. Build momentum.
                    </p>
                  </div>
                  <ArrowRight className="w-5 h-5 text-[#8888a0] group-hover:text-[#ff6b4a] transition-colors" />
                </div>
                
                {/* Progress preview */}
                <div className="mt-4 pt-4 border-t border-white/10">
                  <div className="flex items-center gap-2 text-xs text-[#8888a0]">
                    <Clock className="w-3 h-3" />
                    <span>Under a minute • Earns Focus Coins • Easy win</span>
                  </div>
                </div>
              </motion.button>
              
              {/* Full option */}
              <motion.button
                onClick={() => {
                  setSelectedOption("full");
                  setTimeout(onStartFull, 300);
                }}
                className={`group glass rounded-2xl p-6 text-left transition-all hover:border-[#7c3aed]/50 ${
                  selectedOption === "full" ? "border-[#7c3aed] ring-2 ring-[#7c3aed]/30" : ""
                }`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: 0.4 }}
                whileHover={{ scale: 1.02 }}
                whileTap={{ scale: 0.98 }}
              >
                <div className="flex items-start gap-4">
                  <div className="p-3 rounded-xl bg-[#7c3aed]/20">
                    <Trophy className="w-6 h-6 text-[#7c3aed]" />
                  </div>
                  <div className="flex-1">
                    <h3 className="text-xl font-semibold text-white mb-1">
                      Full session ({formatDuration(fullDuration)})
                    </h3>
                    <p className="text-[#8888a0] text-sm">
                      Ready to focus? Complete the entire section.
                    </p>
                  </div>
                  <ArrowRight className="w-5 h-5 text-[#8888a0] group-hover:text-[#7c3aed] transition-colors" />
                </div>
              </motion.button>
            </div>
            
            {/* Tip */}
            <motion.p
              className="text-sm text-[#8888a0]"
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ delay: 0.5 }}
            >
              💡 Starting is often the hardest part. Quick sessions build consistency.
            </motion.p>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/**
 * Continue prompt after micro session completes
 */
export function MicroContinuePrompt({
  onContinue,
  onStop,
  coinsEarned,
  isVisible,
}: {
  onContinue: () => void;
  onStop: () => void;
  coinsEarned: number;
  isVisible: boolean;
}) {
  return (
    <AnimatePresence>
      {isVisible && (
        <motion.div
          className="fixed inset-x-0 bottom-0 z-50 p-4"
          initial={{ y: 100, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: 100, opacity: 0 }}
        >
          <div className="max-w-md mx-auto glass rounded-2xl p-6 text-center">
            <motion.div
              initial={{ scale: 0 }}
              animate={{ scale: 1 }}
              transition={{ type: "spring", delay: 0.1 }}
              className="w-16 h-16 mx-auto mb-4 rounded-full bg-[#10b981]/20 flex items-center justify-center"
            >
              <Sparkles className="w-8 h-8 text-[#10b981]" />
            </motion.div>
            
            <h3 className="text-xl font-bold text-white mb-2">
              Session complete 🎯
            </h3>
            <p className="text-[#8888a0] mb-1">
              You earned <span className="text-[#f59e0b] font-semibold">{coinsEarned} coins</span>
            </p>
            <p className="text-[#8888a0] mb-6">
              Continue for another 30 seconds?
            </p>
            
            <div className="flex gap-3">
              <Button
                onClick={onStop}
                variant="outline"
                className="flex-1 border-[#2a2a3e] text-white hover:bg-[#2a2a3e]"
              >
                I'm done for now
              </Button>
              <Button
                onClick={onContinue}
                className="flex-1 bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12]"
              >
                Keep going! →
              </Button>
            </div>
          </div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}

/**
 * Hook to manage micro-commitment state
 */
export function useMicroCommitment() {
  const [showPrompt, setShowPrompt] = useState(true);
  const [isMicroMode, setIsMicroMode] = useState(false);
  const [microSessions, setMicroSessions] = useState(0);
  const [showContinue, setShowContinue] = useState(false);
  
  const startMicro = useCallback(() => {
    setShowPrompt(false);
    setIsMicroMode(true);
  }, []);
  
  const startFull = useCallback(() => {
    setShowPrompt(false);
    setIsMicroMode(false);
  }, []);
  
  const completeMicro = useCallback(() => {
    setMicroSessions((prev) => prev + 1);
    setShowContinue(true);
  }, []);
  
  const continueSession = useCallback(() => {
    setShowContinue(false);
  }, []);
  
  const endSession = useCallback(() => {
    setShowContinue(false);
    // Navigate away or show summary
  }, []);
  
  return {
    showPrompt,
    isMicroMode,
    microSessions,
    showContinue,
    startMicro,
    startFull,
    completeMicro,
    continueSession,
    endSession,
  };
}

export default MicroCommitmentPrompt;
