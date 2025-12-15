"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Camera, CheckSquare, Brain, Zap, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";

type OnboardingStep = "welcome" | "camera" | "style" | "baseline";

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState<OnboardingStep>("welcome");
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const [learningStyles, setLearningStyles] = useState<string[]>([]);
  const [wantsBaseline, setWantsBaseline] = useState(false);

  const handleStyleToggle = (style: string) => {
    setLearningStyles((prev) =>
      prev.includes(style) ? prev.filter((s) => s !== style) : [...prev, style]
    );
  };

  const completeOnboarding = () => {
    localStorage.setItem("focusflow_onboarded", "true");
    localStorage.setItem(
      "focusflow_preferences",
      JSON.stringify({
        cameraEnabled,
        learningStyles,
        wantsBaseline,
      })
    );
    router.push("/dashboard");
  };

  const steps: Record<OnboardingStep, React.ReactElement> = {
    welcome: (
      <motion.div
        key="welcome"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
        className="text-center max-w-lg mx-auto"
      >
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#ff6b4a] to-[#f59e0b] flex items-center justify-center mx-auto mb-8">
          <Zap className="w-10 h-10 text-[#0a0a12]" />
        </div>
        <h1 className="text-4xl md:text-5xl font-bold mb-4">
          Welcome to <span className="gradient-text">FocusFlow</span>
        </h1>
        <p className="text-xl text-[#8888a0] mb-12 leading-relaxed">
          This app adapts to your attention.
          <br />
          <span className="text-white">You stay in control.</span>
        </p>
        <Button
          onClick={() => setStep("camera")}
          className="bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold px-8 py-6 text-lg rounded-xl"
        >
          Continue
          <ChevronRight className="w-5 h-5 ml-2" />
        </Button>
      </motion.div>
    ),

    camera: (
      <motion.div
        key="camera"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
        className="max-w-lg mx-auto"
      >
        <div className="w-16 h-16 rounded-2xl bg-[#7c3aed]/20 flex items-center justify-center mx-auto mb-8">
          <Camera className="w-8 h-8 text-[#7c3aed]" />
        </div>
        <h2 className="text-3xl font-bold text-center mb-4">
          Camera-based focus tracking
        </h2>
        <p className="text-[#8888a0] text-center mb-8 text-lg">(Optional)</p>

        <div className="glass rounded-2xl p-8 mb-8">
          <ul className="space-y-4 text-[#8888a0]">
            <li className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-[#10b981]/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <div className="w-2 h-2 rounded-full bg-[#10b981]" />
              </div>
              <span>Detects if you're looking at the screen</span>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-[#10b981]/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <div className="w-2 h-2 rounded-full bg-[#10b981]" />
              </div>
              <span>Pauses when you look away</span>
            </li>
            <li className="flex items-start gap-3">
              <div className="w-6 h-6 rounded-full bg-[#10b981]/20 flex items-center justify-center flex-shrink-0 mt-0.5">
                <div className="w-2 h-2 rounded-full bg-[#10b981]" />
              </div>
              <span className="text-white font-semibold">Runs only on your device</span>
            </li>
          </ul>
        </div>

        <div className="flex gap-4">
          <Button
            onClick={() => {
              setCameraEnabled(true);
              setStep("style");
            }}
            className="flex-1 bg-[#7c3aed] hover:bg-[#8b5cf6] text-white font-semibold px-8 py-6 text-lg rounded-xl"
          >
            Enable Camera
          </Button>
          <Button
            onClick={() => {
              setCameraEnabled(false);
              setStep("style");
            }}
            variant="outline"
            className="flex-1 border-[#2a2a3e] bg-transparent hover:bg-[#1e1e2e] px-8 py-6 text-lg rounded-xl"
          >
            Skip for now
          </Button>
        </div>
      </motion.div>
    ),

    style: (
      <motion.div
        key="style"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
        className="max-w-lg mx-auto"
      >
        <div className="w-16 h-16 rounded-2xl bg-[#06b6d4]/20 flex items-center justify-center mx-auto mb-8">
          <Brain className="w-8 h-8 text-[#06b6d4]" />
        </div>
        <h2 className="text-3xl font-bold text-center mb-4">
          How do you prefer learning?
        </h2>
        <p className="text-[#8888a0] text-center mb-8">
          Select all that apply. We'll adapt the content.
        </p>

        <div className="space-y-3 mb-8">
          {[
            "Short explanations",
            "Examples first",
            "Visual diagrams",
            "Exam-focused",
          ].map((style) => (
            <button
              key={style}
              onClick={() => handleStyleToggle(style)}
              className={`w-full p-5 rounded-xl text-left transition-all ${
                learningStyles.includes(style)
                  ? "bg-[#06b6d4]/20 border-2 border-[#06b6d4]"
                  : "glass border-2 border-transparent hover:border-white/10"
              }`}
            >
              <div className="flex items-center justify-between">
                <span className="text-lg">{style}</span>
                {learningStyles.includes(style) && (
                  <CheckSquare className="w-5 h-5 text-[#06b6d4]" />
                )}
              </div>
            </button>
          ))}
        </div>

        <Button
          onClick={() => setStep("baseline")}
          className="w-full bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold px-8 py-6 text-lg rounded-xl"
        >
          Continue
          <ChevronRight className="w-5 h-5 ml-2" />
        </Button>
      </motion.div>
    ),

    baseline: (
      <motion.div
        key="baseline"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
        className="max-w-lg mx-auto text-center"
      >
        <div className="w-16 h-16 rounded-2xl bg-[#f59e0b]/20 flex items-center justify-center mx-auto mb-8">
          <Zap className="w-8 h-8 text-[#f59e0b]" />
        </div>
        <h2 className="text-3xl font-bold mb-4">
          Want us to learn your focus span?
        </h2>
        <p className="text-[#8888a0] mb-8 text-lg">
          2-minute calibration session
          <br />
          <span className="text-sm">(You can skip this and do it later)</span>
        </p>

        <div className="glass rounded-2xl p-6 mb-8 text-left">
          <p className="text-[#8888a0]">
            We'll show you a short piece of content and learn:
          </p>
          <ul className="mt-4 space-y-2 text-sm text-[#8888a0]">
            <li>• Your natural attention span</li>
            <li>• When you typically look away</li>
            <li>• Optimal chunk size for you</li>
          </ul>
        </div>

        <div className="flex gap-4">
          <Button
            onClick={() => {
              setWantsBaseline(true);
              completeOnboarding();
            }}
            className="flex-1 bg-[#f59e0b] hover:bg-[#fbbf24] text-[#0a0a12] font-semibold px-8 py-6 text-lg rounded-xl"
          >
            Start
          </Button>
          <Button
            onClick={() => {
              setWantsBaseline(false);
              completeOnboarding();
            }}
            variant="outline"
            className="flex-1 border-[#2a2a3e] bg-transparent hover:bg-[#1e1e2e] px-8 py-6 text-lg rounded-xl"
          >
            Skip
          </Button>
        </div>
      </motion.div>
    ),
  };

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white flex items-center justify-center px-6 py-12">
      <AnimatePresence mode="wait">{steps[step]}</AnimatePresence>

      {/* Progress indicator */}
      <div className="fixed bottom-8 left-1/2 -translate-x-1/2 flex gap-2">
        {["welcome", "camera", "style", "baseline"].map((s, i) => (
          <div
            key={s}
            className={`h-1.5 rounded-full transition-all ${
              step === s
                ? "w-8 bg-[#ff6b4a]"
                : i < ["welcome", "camera", "style", "baseline"].indexOf(step)
                ? "w-1.5 bg-white/40"
                : "w-1.5 bg-white/20"
            }`}
          />
        ))}
      </div>
    </div>
  );
}
