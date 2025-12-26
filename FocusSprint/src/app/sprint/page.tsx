"use client";

import { useEffect, useState, Suspense, useCallback } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { ArrowRight, Trophy, PlayCircle, Coins, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useUser } from "@/lib/user-context";
import { AppNav } from "@/components/app-nav";

// ADHD Components
import { VisualTimer } from "@/components/ui/visual-timer";
import { HyperfocusGuard } from "@/components/hyperfocus-guard";
import { AttentionOverlay } from "@/components/attention-overlay";
import { MicroCommitmentPrompt, MicroContinuePrompt, useMicroCommitment } from "@/components/micro-commitment";
import { RewardReveal } from "@/components/reward-reveal";
import { useFrustrationDetector, getRandomIntervention } from "@/hooks/use-frustration-detector";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface QuizQuestion {
  question: string;
  options: string[];
  correct_answer: number;
  explanation: string;
}

interface Chunk {
  id: number;
  title: string;
  summary?: string;
  text_content?: string;
  duration_seconds?: number;
  sequence_number: number;
  key_concepts?: string[];
  quiz_questions?: QuizQuestion[];
  generation_model?: string;
  generation_strategy?: string;
}

interface ContentDetail {
  id: number;
  title: string;
  source_type: string;
  source_url?: string;
  chunks: Chunk[];
}

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

function SprintContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const contentId = searchParams.get("id");
  const { addCoins } = useUser();

  // Core state
  const [content, setContent] = useState<ContentDetail | null>(null);
  const [currentChunkIndex, setCurrentChunkIndex] = useState(0);
  const [loading, setLoading] = useState(true);
  const [authMissing, setAuthMissing] = useState(false);
  
  // Timer state
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const [isPaused, setIsPaused] = useState(false);
  
  // ADHD Feature state
  const [showReward, setShowReward] = useState(false);
  const [currentReward, setCurrentReward] = useState<MysteryReward | null>(null);
  const [showFrustrationPrompt, setShowFrustrationPrompt] = useState(false);
  const [attentionEnabled, setAttentionEnabled] = useState(true);
  
  // Micro-commitment hook
  const {
    showPrompt,
    isMicroMode,
    showContinue,
    startMicro,
    startFull,
    completeMicro,
    continueSession,
    endSession,
  } = useMicroCommitment();
  
  // Frustration detection
  const frustrationMetrics = useFrustrationDetector({
    enabled: !showPrompt,
    onFrustrationDetected: () => {
      setShowFrustrationPrompt(true);
      setTimeout(() => setShowFrustrationPrompt(false), 8000);
    },
  });

  // Fetch content data
  useEffect(() => {
    if (!contentId) return;
    const fetchData = async () => {
      const token = localStorage.getItem("focus_token");
      if (!token) {
        setAuthMissing(true);
        router.push("/signin");
        return;
      }
      try {
        const res = await fetch(`${API_URL}/content/${contentId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setContent(data);
        }
      } catch (e) {
        console.error(e);
      } finally {
        setLoading(false);
      }
    };
    fetchData();
  }, [contentId, router]);
  
  // Timer
  useEffect(() => {
    if (showPrompt || isPaused) return;
    
    const timer = setInterval(() => {
      setElapsedSeconds(prev => prev + 1);
    }, 1000);
    
    return () => clearInterval(timer);
  }, [showPrompt, isPaused]);
  
  // Check for micro mode completion
  useEffect(() => {
    if (isMicroMode && elapsedSeconds >= 30) {
      completeMicro();
    }
  }, [isMicroMode, elapsedSeconds, completeMicro]);

  const handleChunkComplete = async () => {
    const token = localStorage.getItem("focus_token");
    const simulatedAttention = Math.floor(Math.random() * (100 - 80 + 1) + 80);
    
    try {
      const res = await fetch(`${API_URL}/content/${contentId}/chunks/${currentChunk.id}/complete`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({
          quiz_score: 100,
          average_attention: simulatedAttention,
          time_spent_seconds: elapsedSeconds,
        }),
      });

      if (res.ok) {
        const data = await res.json();
        
        // Create mystery reward display (enhanced from API response)
        const mysteryReward: MysteryReward = {
          tier: data.reward_tier || "common",
          tier_display: (data.reward_tier || "COMMON").toUpperCase(),
          base_coins: data.base_coins || 10,
          multiplier: data.multiplier || 1,
          final_coins: data.coins_earned || 15,
          bonus_item: data.bonus_item || null,
          message: data.message || "Nice work! 🎯",
          celebration_level: data.celebration_level || 1,
          is_jackpot: data.is_jackpot || false,
          show_mystery_animation: (data.reward_tier === "rare" || data.reward_tier === "epic" || data.reward_tier === "legendary"),
        };
        
        setCurrentReward(mysteryReward);
        setShowReward(true);
        
        if (data.coins_earned > 0) {
          addCoins(data.coins_earned);
        }
      }
    } catch (e) {
      console.error("Failed to record progress", e);
      // Still show a reward even if API fails
      setCurrentReward({
        tier: "common",
        tier_display: "COMMON",
        base_coins: 10,
        multiplier: 1,
        final_coins: 10,
        bonus_item: null,
        message: "Progress saved! 🎯",
        celebration_level: 1,
        is_jackpot: false,
        show_mystery_animation: false,
      });
      setShowReward(true);
    }
  };
  
  const handleRewardClose = () => {
    setShowReward(false);
    setElapsedSeconds(0);
    
    if (isLastChunk) {
      router.push("/session-end?id=" + contentId);
    } else {
      setCurrentChunkIndex(prev => prev + 1);
    }
  };
  
  const handleMicroContinue = () => {
    continueSession();
    setElapsedSeconds(0);
  };
  
  const handleMicroEnd = () => {
    endSession();
    handleChunkComplete();
  };

  if (authMissing) {
    return (
      <div className="min-h-screen bg-[#0a0a12] flex items-center justify-center text-white">
        Redirecting to sign in...
      </div>
    );
  }

  if (loading || !content) {
    return (
      <div className="min-h-screen bg-[#0a0a12] flex items-center justify-center text-white">
        Loading Sprint...
      </div>
    );
  }

  const currentChunk = content.chunks[currentChunkIndex];
  const isLastChunk = currentChunkIndex === content.chunks.length - 1;
  const chunkDuration = isMicroMode ? 30 : (currentChunk.duration_seconds ?? 300);
  const intervention = getRandomIntervention();

  return (
    <HyperfocusGuard enabled={!showPrompt} thresholdMinutes={45}>
      <AttentionOverlay 
        enabled={attentionEnabled && !showPrompt} 
        lookAwayThreshold={5}
      >
        <div className="min-h-screen bg-[#0a0a12] text-white flex flex-col">
          <AppNav />

          {/* Progress Bar */}
          <div className="fixed top-[72px] left-0 right-0 h-1 bg-[#1e1e2e] z-40">
            <motion.div
              className="h-full bg-[#ff6b4a]"
              initial={{ width: 0 }}
              animate={{ width: `${((currentChunkIndex) / content.chunks.length) * 100}%` }}
            />
          </div>

          <main className="flex-1 flex flex-col pt-24 px-6 max-w-5xl mx-auto w-full pb-10">
            {/* Header */}
            <header className="mb-8 flex items-center justify-between">
              <div>
                <div className="flex items-center gap-2 text-[#8888a0] mb-2 text-sm">
                  <span>{content.title}</span>
                  <span>•</span>
                  <span>Sprint {currentChunk.sequence_number} of {content.chunks.length}</span>
                  {isMicroMode && (
                    <span className="ml-2 px-2 py-0.5 bg-[#ff6b4a]/20 text-[#ff6b4a] text-xs rounded-full">
                      ⚡ MICRO MODE
                    </span>
                  )}
                </div>
                <h1 className="text-3xl font-bold">{currentChunk.title}</h1>
              </div>
              
              {/* Visual Timer */}
              <VisualTimer
                duration={chunkDuration}
                elapsed={elapsedSeconds}
                isPaused={isPaused}
                size={100}
                showComparison={true}
              />
            </header>

            {/* Content Area */}
            <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-8">
              {/* Left: Main Content */}
              <div className="lg:col-span-2 space-y-6">
                <div className="bg-[#13131f] border border-[#2a2a3e] rounded-3xl overflow-hidden aspect-video relative group">
                  {content.source_type === "youtube" ? (
                    <div className="w-full h-full flex items-center justify-center bg-black/50">
                      <PlayCircle className="w-16 h-16 text-white/50 group-hover:text-[#ff6b4a] transition-colors" />
                      <p className="absolute bottom-4 text-sm text-white/70">
                        Video Sync active for timestamp {currentChunk.sequence_number * 5}:00
                      </p>
                    </div>
                  ) : (
                    <div className="p-8 h-full overflow-y-auto">
                      <p className="whitespace-pre-wrap text-lg leading-relaxed text-[#d4d4d8]">
                        {currentChunk.text_content || currentChunk.summary}
                      </p>
                    </div>
                  )}
                </div>

                <div className="bg-[#13131f] border border-[#2a2a3e] rounded-3xl p-6">
                  <h3 className="font-semibold mb-3 flex items-center gap-2">
                    <Trophy className="w-4 h-4 text-[#f59e0b]" />
                    Key Concepts
                  </h3>
                  <div className="flex flex-wrap gap-2">
                    {currentChunk.key_concepts?.length
                      ? currentChunk.key_concepts.map((concept, i) => (
                          <span
                            key={i}
                            className="px-3 py-1 bg-[#1e1e2e] rounded-full text-sm border border-[#2a2a3e] text-[#8888a0]"
                          >
                            {concept}
                          </span>
                        ))
                      : <span className="text-sm text-[#8888a0]">No key concepts</span>}
                  </div>
                </div>
              </div>

              {/* Right: Interaction / Summary */}
              <div className="space-y-6">
                <div className="bg-[#13131f] border border-[#2a2a3e] rounded-3xl p-6 h-full flex flex-col">
                  <h3 className="text-xl font-bold mb-4">Summary</h3>
                  <p className="text-[#8888a0] leading-relaxed mb-8 flex-1">
                    {currentChunk.summary}
                  </p>

                  {/* Coins preview */}
                  <div className="flex items-center gap-2 mb-4 text-[#f59e0b]">
                    <Coins className="w-5 h-5" />
                    <span className="font-semibold">~10-50 coins</span>
                    <Zap className="w-4 h-4 ml-2" />
                    <span className="text-xs text-[#8888a0]">Mystery reward!</span>
                  </div>

                  <Button
                    onClick={handleChunkComplete}
                    className="w-full h-14 bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-bold text-lg rounded-xl"
                  >
                    {isLastChunk ? "Complete Sprint" : "Next Sprint"} <ArrowRight className="ml-2" />
                  </Button>
                </div>
              </div>
            </div>
          </main>
          
          {/* Micro-Commitment Prompt */}
          <MicroCommitmentPrompt
            title={content.title}
            fullDuration={currentChunk.duration_seconds ?? 300}
            onStartMicro={startMicro}
            onStartFull={startFull}
            isVisible={showPrompt}
          />
          
          {/* Micro Continue Prompt */}
          <MicroContinuePrompt
            onContinue={handleMicroContinue}
            onStop={handleMicroEnd}
            coinsEarned={10}
            isVisible={showContinue}
          />
          
          {/* Reward Reveal */}
          <RewardReveal
            reward={currentReward}
            isVisible={showReward}
            onClose={handleRewardClose}
          />
          
          {/* Frustration Intervention */}
          {showFrustrationPrompt && (
            <motion.div
              className="fixed bottom-20 left-1/2 z-50 transform -translate-x-1/2"
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: 20 }}
            >
              <div className="glass rounded-2xl px-6 py-4 max-w-sm text-center">
                <p className="text-white mb-2">{intervention.message}</p>
                <Button
                  onClick={() => setShowFrustrationPrompt(false)}
                  variant="outline"
                  size="sm"
                  className="border-[#2a2a3e] text-white"
                >
                  {intervention.action}
                </Button>
              </div>
            </motion.div>
          )}
        </div>
      </AttentionOverlay>
    </HyperfocusGuard>
  );
}

export default function SprintPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#0a0a12] text-white flex items-center justify-center">Loading...</div>}>
      <SprintContent />
    </Suspense>
  );
}