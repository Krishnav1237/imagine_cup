"use client";

import { motion, AnimatePresence } from "framer-motion";
import { useState, useEffect, useRef } from "react";
import { useRouter } from "next/navigation";
import {
  Eye,
  EyeOff,
  Play,
  Pause,
  Clock,
  Target,
  Coins,
  Sparkles,
  ChevronRight,
  Trophy,
  Home,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { useUser } from "@/lib/user-context";
import { Progress } from "@/components/ui/progress";

export default function SprintPage() {
  const router = useRouter();
  const { currentProgress, addCoins, completeSprint, incrementStreak, focusCoins, streak, setProgress, isLoaded } = useUser();
  const [isLooking, setIsLooking] = useState(true);
  const [isPaused, setIsPaused] = useState(false);
  const [timeElapsed, setTimeElapsed] = useState(0);
  const [sprintPhase, setSprintPhase] = useState<'video' | 'infographic' | 'quiz'>('video');
  const [selectedAnswer, setSelectedAnswer] = useState<number | null>(null);
  const [isCorrect, setIsCorrect] = useState<boolean | null>(null);
  const [earnedCoins, setEarnedCoins] = useState(0);
  const [focusTime, setFocusTime] = useState(0);
  const [distractionCount, setDistractionCount] = useState(0);
  const [showMicroRecap, setShowMicroRecap] = useState(false);
  const timerRef = useRef<NodeJS.Timeout | null>(null);
  const lastLookingStateRef = useRef(true);

  const currentSprint = currentProgress?.sprints[currentProgress.currentSprintIndex];
  const sprintDuration = 300;

  useEffect(() => {
    if (isLoaded && !currentProgress) {
      router.push("/upload");
      return;
    }
  }, [currentProgress, router, isLoaded]);

  useEffect(() => {
    if (!isPaused && isLooking && timeElapsed < sprintDuration) {
      timerRef.current = setInterval(() => {
        setTimeElapsed((prev) => {
          const next = prev + 1;
          if (next >= sprintDuration) {
            handleSprintComplete();
            return sprintDuration;
          }
          return next;
        });
        setFocusTime((prev) => prev + 1);
      }, 1000);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPaused, isLooking, timeElapsed]);

  useEffect(() => {
    if (!isLooking) {
      setIsPaused(true);
      
      // Track distraction and show Micro-Recap after 3 look-aways
      if (lastLookingStateRef.current === true) {
        setDistractionCount(prev => {
          const newCount = prev + 1;
          if (newCount >= 3 && sprintPhase === 'video') {
            setShowMicroRecap(true);
          }
          return newCount;
        });
      }
    }
    lastLookingStateRef.current = isLooking;
  }, [isLooking, sprintPhase]);

  const handleSprintComplete = () => {
    setSprintPhase('infographic');
    const focusPercentage = (focusTime / sprintDuration) * 100;
    let coins = 50;
    if (focusPercentage >= 90) coins += 25;
    if (streak >= 2) coins *= 2;
    setEarnedCoins(coins);
  };

  const handleAnswerSubmit = () => {
    if (selectedAnswer === null) return;
    const correct = selectedAnswer === 1;
    setIsCorrect(correct);
    
    setTimeout(() => {
      if (correct) {
        addCoins(earnedCoins + 10);
        incrementStreak();
      } else {
        addCoins(earnedCoins);
      }
      
      if (currentSprint) {
        completeSprint({
          ...currentSprint,
          completed: true,
        });
      }

      if (currentProgress && currentProgress.currentSprintIndex < currentProgress.totalSprints - 1) {
        const updatedProgress = {
          ...currentProgress,
          currentSprintIndex: currentProgress.currentSprintIndex + 1,
        };
        setProgress(updatedProgress);
        setTimeElapsed(0);
        setFocusTime(0);
        setSprintPhase('video');
        setSelectedAnswer(null);
        setIsCorrect(null);
        setDistractionCount(0);
      } else {
        router.push("/session-end");
      }
    }, 2000);
  };

  if (!currentProgress || !currentSprint) {
    return <div className="min-h-screen bg-[#0a0a12] flex items-center justify-center text-white">Loading...</div>;
  }

  const progress = (timeElapsed / sprintDuration) * 100;
  const focusPercentage = timeElapsed > 0 ? (focusTime / timeElapsed) * 100 : 100;

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white">
      <div className="fixed top-0 left-0 right-0 z-50 glass">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <Button
                onClick={() => router.push('/dashboard')}
                variant="ghost"
                size="sm"
                className="text-[#8888a0] hover:text-white"
              >
                ← Home
              </Button>
              <div className="text-sm text-[#8888a0]">
                Sprint {currentSprint.sprintNumber} of {currentSprint.totalSprints}
              </div>
              <div className="text-sm font-semibold text-white">{currentSprint.concept}</div>
            </div>
            <div className="flex items-center gap-4">
              {sprintPhase === 'video' && (
                <Button
                  onClick={() => {
                    setSprintPhase('infographic');
                    if (timerRef.current) clearInterval(timerRef.current);
                  }}
                  variant="outline"
                  size="sm"
                  className="border-[#2a2a3e] bg-[#1e1e2e] hover:bg-[#2a2a3e] text-xs"
                >
                  Skip to Next →
                </Button>
              )}
              {streak > 0 && (
                <div className="glass px-3 py-2 rounded-full text-sm">
                  🔥 {streak}x
                </div>
              )}
              <div className="flex items-center gap-2 glass px-4 py-2 rounded-full">
                <Coins className="w-4 h-4 text-[#f59e0b]" />
                <span className="font-semibold">{focusCoins}</span>
              </div>
            </div>
          </div>
          <div className="mt-3">
            <Progress value={progress} className="h-2" />
          </div>
        </div>
      </div>

      {/* Micro-Recap Modal for Distraction */}
      <AnimatePresence>
        {showMicroRecap && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 bg-black/80 backdrop-blur-md z-50 flex items-center justify-center px-6"
            onClick={() => setShowMicroRecap(false)}
          >
            <motion.div
              initial={{ scale: 0.9, y: 20 }}
              animate={{ scale: 1, y: 0 }}
              exit={{ scale: 0.9, y: 20 }}
              className="glass rounded-3xl p-8 max-w-2xl w-full"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="flex items-center gap-3 mb-6">
                <div className="w-12 h-12 rounded-xl bg-[#06b6d4]/20 flex items-center justify-center">
                  <Sparkles className="w-6 h-6 text-[#06b6d4]" />
                </div>
                <div>
                  <h3 className="text-2xl font-bold">Quick Recap</h3>
                  <p className="text-sm text-[#8888a0]">Let's get you back on track</p>
                </div>
              </div>
              
              <div className="space-y-4 mb-6">
                <div className="p-4 rounded-xl bg-[#1e1e2e] border border-[#2a2a3e]">
                  <h4 className="font-semibold mb-2 text-[#06b6d4]">Main Concept</h4>
                  <p className="text-[#8888a0]">{currentSprint?.concept}</p>
                </div>
                <div className="p-4 rounded-xl bg-[#1e1e2e] border border-[#2a2a3e]">
                  <h4 className="font-semibold mb-2 text-[#7c3aed]">Key Points</h4>
                  <ul className="list-disc list-inside space-y-1 text-[#8888a0]">
                    <li>Core definition and purpose</li>
                    <li>Real-world application</li>
                    <li>Common misconceptions</li>
                  </ul>
                </div>
              </div>
              
              <div className="flex gap-3">
                <Button
                  onClick={() => {
                    setShowMicroRecap(false);
                    setDistractionCount(0);
                  }}
                  className="flex-1 bg-[#06b6d4] hover:bg-[#06b6d4]/80 text-[#0a0a12]"
                >
                  Got it, continue
                </Button>
                <Button
                  onClick={() => {
                    setShowMicroRecap(false);
                    setTimeElapsed(Math.max(0, timeElapsed - 60));
                    setDistractionCount(0);
                  }}
                  variant="outline"
                  className="flex-1 border-[#2a2a3e] bg-[#1e1e2e] hover:bg-[#2a2a3e]"
                >
                  Explain differently
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence mode="wait">
        {sprintPhase === 'video' ? (
          <motion.div
            key="video"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="pt-32 pb-12 px-6"
          >
            <div className="max-w-7xl mx-auto flex gap-6">
              <div className="flex-1 flex flex-col gap-6">
                <div
                  className={`relative flex-1 rounded-2xl overflow-hidden transition-all duration-500 ${
                    !isLooking ? "blur-md" : ""
                  }`}
                  style={{
                    backgroundImage: currentSprint.infographic ? `url(${currentSprint.infographic})` : "none",
                    backgroundSize: "cover",
                    backgroundPosition: "center",
                    minHeight: "500px",
                  }}
                >
                  <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent" />
                  <div className="absolute bottom-6 left-6 right-6">
                    <h2 className="text-2xl font-bold mb-2">{currentSprint.concept}</h2>
                    <div className="flex items-center gap-4 text-sm text-[#8888a0]">
                      <div className="flex items-center gap-2">
                        <Clock className="w-4 h-4" />
                        {Math.floor((sprintDuration - timeElapsed) / 60)}:
                        {String((sprintDuration - timeElapsed) % 60).padStart(2, "0")} remaining
                      </div>
                      <div className="flex items-center gap-2">
                        <Target className="w-4 h-4" />
                        {focusPercentage.toFixed(0)}% focus
                      </div>
                    </div>
                  </div>

                  {!isLooking && (
                    <div className="absolute inset-0 flex flex-col items-center justify-center bg-black/70 backdrop-blur-sm">
                      <EyeOff className="w-16 h-16 text-[#ff6b4a] mb-4" />
                      <p className="text-xl font-semibold mb-2">Look at the screen to continue</p>
                      <p className="text-[#8888a0]">Sprint paused due to distraction</p>
                    </div>
                  )}
                </div>

                <div className="flex gap-4 mb-4">
                  <Button
                    onClick={() => setIsLooking(!isLooking)}
                    variant="outline"
                    className="flex-1 border-[#2a2a3e] bg-[#1e1e2e] hover:bg-[#2a2a3e]"
                  >
                    {isLooking ? "Simulate Looking Away" : "Simulate Looking Back"}
                  </Button>
                  <Button
                    onClick={() => setIsPaused(!isPaused)}
                    variant="outline"
                    className="px-8 border-[#2a2a3e] bg-[#1e1e2e] hover:bg-[#2a2a3e]"
                  >
                    {isPaused ? <Play className="w-5 h-5" /> : <Pause className="w-5 h-5" />}
                  </Button>
                </div>

                {/* Adaptive Complexity Controls */}
                <div className="grid grid-cols-3 gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-[#2a2a3e] bg-[#1e1e2e] hover:bg-[#7c3aed]/20 hover:border-[#7c3aed] text-xs"
                    onClick={() => {/* Make shorter logic */}}
                  >
                    Make shorter
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-[#2a2a3e] bg-[#1e1e2e] hover:bg-[#06b6d4]/20 hover:border-[#06b6d4] text-xs"
                    onClick={() => {/* Show example logic */}}
                  >
                    Show example
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    className="border-[#2a2a3e] bg-[#1e1e2e] hover:bg-[#f59e0b]/20 hover:border-[#f59e0b] text-xs"
                    onClick={() => {/* Pause & recap logic */}}
                  >
                    Pause & recap
                  </Button>
                </div>
              </div>

              <div className="w-80 space-y-6">
                <div className="glass rounded-2xl p-6">
                  <div className="flex items-center gap-3 mb-4">
                    <Eye className={`w-6 h-6 ${isLooking ? "text-[#10b981]" : "text-[#ff6b4a]"}`} />
                    <div>
                      <div className="text-sm text-[#8888a0]">Eye Tracking</div>
                      <div className={`text-lg font-semibold ${isLooking ? "text-[#10b981]" : "text-[#ff6b4a]"}`}>
                        {isLooking ? "Focused" : "Distracted"}
                      </div>
                    </div>
                  </div>
                  <div className="h-2 bg-[#1e1e2e] rounded-full overflow-hidden">
                    <motion.div
                      className="h-full bg-gradient-to-r from-[#10b981] to-[#06b6d4]"
                      style={{ width: `${focusPercentage}%` }}
                      transition={{ duration: 0.3 }}
                    />
                  </div>
                  <p className="text-xs text-[#8888a0] mt-2">
                    {isLooking
                      ? "Great job staying focused!"
                      : "Look back at the screen to earn full rewards"}
                  </p>
                </div>

                <div className="glass rounded-2xl p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Target className="w-5 h-5 text-[#7c3aed]" />
                    <span className="font-semibold">Sprint Queue</span>
                  </div>
                  <div className="space-y-2">
                    {currentProgress.sprints.slice(
                      currentProgress.currentSprintIndex,
                      currentProgress.currentSprintIndex + 3
                    ).map((sprint, i) => (
                      <div
                        key={sprint.id}
                        className={`p-3 rounded-lg text-sm ${
                          i === 0
                            ? "bg-[#7c3aed]/20 text-[#a78bfa] border border-[#7c3aed]/30"
                            : "bg-[#1e1e2e] text-[#8888a0]"
                        }`}
                      >
                        {i === 0 && <span className="text-xs text-[#7c3aed] font-semibold mr-2">NOW</span>}
                        {sprint.concept}
                      </div>
                    ))}
                  </div>
                </div>

                <div className="glass rounded-2xl p-6">
                  <div className="flex items-center gap-2 mb-4">
                    <Coins className="w-5 h-5 text-[#f59e0b]" />
                    <span className="font-semibold">Potential Rewards</span>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-[#8888a0]">Base reward</span>
                      <span className="text-[#f59e0b] font-semibold">+50</span>
                    </div>
                    {focusPercentage >= 90 && (
                      <div className="flex justify-between">
                        <span className="text-[#8888a0]">Perfect focus bonus</span>
                        <span className="text-[#10b981] font-semibold">+25</span>
                      </div>
                    )}
                    {streak >= 2 && (
                      <div className="flex justify-between">
                        <span className="text-[#8888a0]">Streak multiplier</span>
                        <span className="text-[#ff6b4a] font-semibold">×2</span>
                      </div>
                    )}
                  </div>
                </div>
              </div>
            </div>
          </motion.div>
        ) : sprintPhase === 'infographic' ? (
          <motion.div
            key="infographic"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="min-h-screen flex items-center justify-center px-6 pt-32"
          >
            <div className="max-w-4xl w-full">
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="text-center mb-8"
              >
                <div className="inline-flex items-center gap-2 glass px-4 py-2 rounded-full mb-4">
                  <Sparkles className="w-4 h-4 text-[#f59e0b]" />
                  <span className="text-sm text-[#8888a0]">Video Complete!</span>
                </div>
                <h2 className="text-4xl font-bold mb-2">
                  <span className="gradient-text">{currentSprint.concept}</span>
                </h2>
                <p className="text-[#8888a0]">Here's a visual summary of what you just learned</p>
              </motion.div>

              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="glass rounded-3xl p-8 mb-6"
              >
                <div className="aspect-[16/9] rounded-2xl overflow-hidden mb-6 bg-gradient-to-br from-[#7c3aed]/20 to-[#06b6d4]/20 flex items-center justify-center">
                  {currentSprint.infographic ? (
                    <img
                      src={currentSprint.infographic}
                      alt="Sprint infographic"
                      className="w-full h-full object-cover"
                    />
                  ) : (
                    <div className="text-center p-12">
                      <h3 className="text-3xl font-bold mb-4">{currentSprint.concept}</h3>
                      <p className="text-[#8888a0] text-lg max-w-2xl">{currentSprint.summary}</p>
                    </div>
                  )}
                </div>
              </motion.div>

              <Button
                onClick={() => setSprintPhase('quiz')}
                className="w-full bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold px-8 py-6 text-lg rounded-xl"
              >
                Take Quick Quiz
                <ChevronRight className="w-5 h-5 ml-2" />
              </Button>
            </div>
          </motion.div>
        ) : (

          <motion.div
            key="quiz"
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.95 }}
            className="min-h-screen flex items-center justify-center px-6 pt-32"
          >
            <div className="max-w-3xl w-full">
              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.2 }}
                className="text-center mb-8"
              >
                <div className="inline-flex items-center gap-2 glass px-4 py-2 rounded-full mb-4">
                  <Target className="w-4 h-4 text-[#7c3aed]" />
                  <span className="text-sm text-[#8888a0]">Knowledge Check</span>
                </div>
                <h2 className="text-3xl font-bold mb-2">Quick Quiz</h2>
                <p className="text-[#8888a0]">Lock in what you just learned</p>
              </motion.div>

              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.3 }}
                className="glass rounded-3xl p-8 mb-6"
              >
                <h3 className="text-xl font-semibold mb-4">Quick Knowledge Check</h3>
                <p className="text-[#8888a0] mb-6">
                  What was the main concept covered in this sprint?
                </p>
                <div className="space-y-3">
                  {[
                    currentSprint.concept,
                    "Something completely different",
                    "Another random topic",
                    "Not covered in this sprint",
                  ].map((option, i) => (
                    <button
                      key={i}
                      onClick={() => {
                        if (isCorrect === null) setSelectedAnswer(i);
                      }}
                      disabled={isCorrect !== null}
                      className={`w-full p-4 rounded-xl text-left transition-all ${
                        selectedAnswer === i
                          ? isCorrect === null
                            ? "bg-[#7c3aed]/20 border border-[#7c3aed]"
                            : isCorrect
                            ? "bg-[#06b6d4]/20 border border-[#06b6d4]"
                            : "bg-[#f59e0b]/20 border border-[#f59e0b]"
                          : "bg-[#1e1e2e] border border-[#2a2a3e] hover:border-white/20"
                      } ${isCorrect !== null ? "cursor-not-allowed" : ""}`}
                    >
                      <div className="flex items-center justify-between">
                        <span>{option}</span>
                        {selectedAnswer === i && isCorrect !== null && (
                          <div className="text-sm font-semibold">
                            {isCorrect ? "You're on track ✓" : "Let's revisit this"}
                          </div>
                        )}
                      </div>
                    </button>
                  ))}
                </div>
              </motion.div>

              <motion.div
                initial={{ y: 20, opacity: 0 }}
                animate={{ y: 0, opacity: 1 }}
                transition={{ delay: 0.5 }}
                className="glass rounded-2xl p-6 mb-6"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-[#f59e0b]/20 flex items-center justify-center">
                      <Trophy className="w-6 h-6 text-[#f59e0b]" />
                    </div>
                    <div>
                      <div className="text-sm text-[#8888a0]">You earned</div>
                      <div className="text-2xl font-bold text-[#f59e0b]">
                        +{earnedCoins} {selectedAnswer === 1 && "+ 10 bonus"} Focus Coins
                      </div>
                    </div>
                  </div>
                </div>
              </motion.div>

              <Button
                onClick={handleAnswerSubmit}
                disabled={selectedAnswer === null || isCorrect !== null}
                className="w-full bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold px-8 py-6 text-lg rounded-xl disabled:opacity-50"
              >
                {isCorrect === null ? (
                  <>
                    Continue to Next Sprint
                    <ChevronRight className="w-5 h-5 ml-2" />
                  </>
                ) : (
                  "Loading next sprint..."
                )}
              </Button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}