"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Camera, CheckSquare, Brain, Zap, ChevronRight, User, 
  Sparkles, BarChart3, Clock, ArrowLeft 
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { 
  AgeGroup, 
  FocusStyle, 
  SessionLength, 
  applyAgeGroupDefaults 
} from "@/lib/user-preferences";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

type OnboardingStep = "welcome" | "profile" | "camera" | "style" | "session" | "ready";

// Age group options
const AGE_GROUPS: { id: AgeGroup; label: string; description: string; icon: React.ReactNode }[] = [
  { 
    id: "teen", 
    label: "Student (13-18)", 
    description: "Vibrant, gamified experience",
    icon: <Sparkles className="w-5 h-5" />
  },
  { 
    id: "young-adult", 
    label: "Young Adult (18-30)", 
    description: "Modern, balanced approach",
    icon: <Zap className="w-5 h-5" />
  },
  { 
    id: "professional", 
    label: "Professional (30+)", 
    description: "Minimal, data-focused",
    icon: <BarChart3 className="w-5 h-5" />
  },
  { 
    id: "senior", 
    label: "Accessible Mode", 
    description: "High contrast, simplified",
    icon: <User className="w-5 h-5" />
  },
];

// Focus style options
const FOCUS_STYLES: { id: FocusStyle; label: string; description: string }[] = [
  { id: "gamified", label: "Gamified", description: "Coins, rewards, achievements" },
  { id: "data-driven", label: "Data-Driven", description: "Metrics and progress charts" },
  { id: "minimal", label: "Minimal", description: "Just the content, no extras" },
];

// Session length options
const SESSION_LENGTHS: { id: SessionLength; label: string; duration: string }[] = [
  { id: "micro", label: "Micro", duration: "30 sec" },
  { id: "short", label: "Short", duration: "2 min" },
  { id: "standard", label: "Standard", duration: "5 min" },
  { id: "long", label: "Extended", duration: "10 min" },
];

export default function OnboardingPage() {
  const router = useRouter();
  const [step, setStep] = useState<OnboardingStep>("welcome");
  
  // New preferences
  const [ageGroup, setAgeGroup] = useState<AgeGroup>("young-adult");
  const [focusStyle, setFocusStyle] = useState<FocusStyle>("gamified");
  const [sessionLength, setSessionLength] = useState<SessionLength>("standard");
  
  // Existing preferences
  const [cameraEnabled, setCameraEnabled] = useState(false);
  const [learningStyles, setLearningStyles] = useState<string[]>([]);

  const handleStyleToggle = (style: string) => {
    setLearningStyles((prev) =>
      prev.includes(style) ? prev.filter((s) => s !== style) : [...prev, style]
    );
  };

  const completeOnboarding = async () => {
    // Save locally
    localStorage.setItem("focusflow_onboarded", "true");
    applyAgeGroupDefaults(ageGroup);
    
    localStorage.setItem(
      "focusflow_preferences",
      JSON.stringify({
        cameraEnabled,
        learningStyles,
        ageGroup,
        focusStyle,
        sessionLength,
      })
    );
    
    // Save to backend if logged in
    try {
      const token = localStorage.getItem("focus_token");
      if (token) {
        await fetch(`${API_URL}/preferences/onboarding`, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
          body: JSON.stringify({
            ageGroup,
            focusStyle,
            sessionLength,
          }),
        });
      }
    } catch (e) {
      console.error("Failed to save preferences to backend:", e);
    }
    
    router.push("/dashboard");
  };

  const requestCameraPermission = async () => {
    if (typeof navigator === "undefined" || !navigator.mediaDevices?.getUserMedia) {
      return;
    }

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: true });
      stream.getTracks().forEach((track) => track.stop());
      localStorage.setItem("focusflow_camera_permission", "granted");
    } catch (e) {
      console.error("Camera permission denied or failed", e);
      localStorage.setItem("focusflow_camera_permission", "denied");
    }
  };

  const stepOrder: OnboardingStep[] = ["welcome", "profile", "camera", "style", "session", "ready"];
  const currentIndex = stepOrder.indexOf(step);
  
  const goNext = () => {
    const nextIndex = currentIndex + 1;
    if (nextIndex < stepOrder.length) {
      setStep(stepOrder[nextIndex]);
    }
  };
  
  const goBack = () => {
    const prevIndex = currentIndex - 1;
    if (prevIndex >= 0) {
      setStep(stepOrder[prevIndex]);
    }
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
          Welcome to <span className="gradient-text">FocusSprint</span>
        </h1>
        <p className="text-xl text-[#8888a0] mb-12 leading-relaxed">
          Smart learning that adapts to how you focus.
          <br />
          <span className="text-white">Let&apos;s personalize your experience.</span>
        </p>
        <Button
          onClick={goNext}
          className="bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold px-8 py-6 text-lg rounded-xl"
        >
          Get Started
          <ChevronRight className="w-5 h-5 ml-2" />
        </Button>
      </motion.div>
    ),

    profile: (
      <motion.div
        key="profile"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
        className="max-w-lg mx-auto"
      >
        <h2 className="text-3xl font-bold text-center mb-4">
          Tell us about yourself
        </h2>
        <p className="text-[#8888a0] text-center mb-8">
          This helps us customize your experience
        </p>

        <div className="space-y-3 mb-8">
          {AGE_GROUPS.map((group) => (
            <button
              key={group.id}
              onClick={() => setAgeGroup(group.id)}
              className={`w-full flex items-center gap-4 p-4 rounded-xl transition-all ${
                ageGroup === group.id
                  ? "bg-[#ff6b4a]/20 border-2 border-[#ff6b4a]"
                  : "glass border-2 border-transparent hover:border-white/10"
              }`}
            >
              <div className={`p-2 rounded-lg ${
                ageGroup === group.id ? "bg-[#ff6b4a]/30 text-[#ff6b4a]" : "bg-[#2a2a3e] text-[#8888a0]"
              }`}>
                {group.icon}
              </div>
              <div className="flex-1 text-left">
                <span className="font-medium">{group.label}</span>
                <p className="text-sm text-[#8888a0]">{group.description}</p>
              </div>
              {ageGroup === group.id && (
                <CheckSquare className="w-5 h-5 text-[#ff6b4a]" />
              )}
            </button>
          ))}
        </div>

        <div className="flex gap-4">
          <Button
            onClick={goBack}
            variant="outline"
            className="border-[#2a2a3e] bg-transparent hover:bg-[#1e1e2e] px-6 py-6 rounded-xl"
          >
            <ArrowLeft className="w-4 h-4 mr-2" />
            Back
          </Button>
          <Button
            onClick={goNext}
            className="flex-1 bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold py-6 rounded-xl"
          >
            Continue
            <ChevronRight className="w-5 h-5 ml-2" />
          </Button>
        </div>
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
          Focus tracking
        </h2>
        <p className="text-[#8888a0] text-center mb-8 text-lg">(Optional)</p>

        <div className="glass rounded-2xl p-6 mb-8">
          <ul className="space-y-3 text-[#8888a0]">
            <li className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-[#10b981]" />
              <span>Detects when you look away</span>
            </li>
            <li className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-[#10b981]" />
              <span>Pauses content automatically</span>
            </li>
            <li className="flex items-center gap-3">
              <div className="w-2 h-2 rounded-full bg-[#10b981]" />
              <span className="text-white font-medium">Runs only on your device</span>
            </li>
          </ul>
        </div>

        <div className="flex gap-4">
          <Button
            onClick={() => {
              setCameraEnabled(false);
              goNext();
            }}
            variant="outline"
            className="flex-1 border-[#2a2a3e] bg-transparent hover:bg-[#1e1e2e] px-8 py-6 rounded-xl"
          >
            Skip
          </Button>
          <Button
            onClick={() => {
              setCameraEnabled(true);
              requestCameraPermission();
              goNext();
            }}
            className="flex-1 bg-[#7c3aed] hover:bg-[#8b5cf6] text-white font-semibold px-8 py-6 rounded-xl"
          >
            Enable
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
          What motivates you?
        </h2>
        <p className="text-[#8888a0] text-center mb-8">
          Choose your experience style
        </p>

        <div className="space-y-3 mb-8">
          {FOCUS_STYLES.map((style) => (
            <button
              key={style.id}
              onClick={() => setFocusStyle(style.id)}
              className={`w-full p-5 rounded-xl text-left transition-all ${
                focusStyle === style.id
                  ? "bg-[#06b6d4]/20 border-2 border-[#06b6d4]"
                  : "glass border-2 border-transparent hover:border-white/10"
              }`}
            >
              <div className="flex items-center justify-between">
                <div>
                  <span className="text-lg font-medium">{style.label}</span>
                  <p className="text-sm text-[#8888a0]">{style.description}</p>
                </div>
                {focusStyle === style.id && (
                  <CheckSquare className="w-5 h-5 text-[#06b6d4]" />
                )}
              </div>
            </button>
          ))}
        </div>

        <Button
          onClick={goNext}
          className="w-full bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold px-8 py-6 text-lg rounded-xl"
        >
          Continue
          <ChevronRight className="w-5 h-5 ml-2" />
        </Button>
      </motion.div>
    ),

    session: (
      <motion.div
        key="session"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
        className="max-w-lg mx-auto"
      >
        <div className="w-16 h-16 rounded-2xl bg-[#f59e0b]/20 flex items-center justify-center mx-auto mb-8">
          <Clock className="w-8 h-8 text-[#f59e0b]" />
        </div>
        <h2 className="text-3xl font-bold text-center mb-4">
          Typical focus window?
        </h2>
        <p className="text-[#8888a0] text-center mb-8">
          How long can you usually focus before needing a break?
        </p>

        <div className="grid grid-cols-2 gap-4 mb-8">
          {SESSION_LENGTHS.map((length) => (
            <button
              key={length.id}
              onClick={() => setSessionLength(length.id)}
              className={`p-6 rounded-xl text-center transition-all ${
                sessionLength === length.id
                  ? "bg-[#f59e0b]/20 border-2 border-[#f59e0b]"
                  : "glass border-2 border-transparent hover:border-white/10"
              }`}
            >
              <span className="text-lg font-medium block">{length.label}</span>
              <span className="text-sm text-[#8888a0]">{length.duration}</span>
            </button>
          ))}
        </div>

        <Button
          onClick={goNext}
          className="w-full bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold px-8 py-6 text-lg rounded-xl"
        >
          Continue
          <ChevronRight className="w-5 h-5 ml-2" />
        </Button>
      </motion.div>
    ),

    ready: (
      <motion.div
        key="ready"
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        exit={{ opacity: 0, y: -20 }}
        transition={{ duration: 0.3 }}
        className="max-w-lg mx-auto text-center"
      >
        <div className="w-20 h-20 rounded-2xl bg-gradient-to-br from-[#10b981] to-[#06b6d4] flex items-center justify-center mx-auto mb-8">
          <CheckSquare className="w-10 h-10 text-white" />
        </div>
        <h2 className="text-3xl font-bold mb-4">
          You&apos;re all set!
        </h2>
        <p className="text-[#8888a0] mb-8 text-lg">
          Your experience is personalized. You can change settings anytime.
        </p>

        <div className="glass rounded-2xl p-6 mb-8 text-left">
          <h3 className="font-medium mb-4">Your preferences:</h3>
          <ul className="space-y-2 text-sm text-[#8888a0]">
            <li>• Profile: {AGE_GROUPS.find(g => g.id === ageGroup)?.label}</li>
            <li>• Style: {FOCUS_STYLES.find(s => s.id === focusStyle)?.label}</li>
            <li>• Sessions: {SESSION_LENGTHS.find(l => l.id === sessionLength)?.duration}</li>
            <li>• Camera: {cameraEnabled ? "Enabled" : "Disabled"}</li>
          </ul>
        </div>

        <Button
          onClick={completeOnboarding}
          className="w-full bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold px-8 py-6 text-lg rounded-xl"
        >
          Start Learning
          <ChevronRight className="w-5 h-5 ml-2" />
        </Button>
      </motion.div>
    ),
  };

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white flex items-center justify-center px-6 py-12">
      <AnimatePresence mode="wait">{steps[step]}</AnimatePresence>

      {/* Progress indicator */}
      <div className="fixed bottom-8 left-1/2 -translate-x-1/2 flex gap-2">
        {stepOrder.map((s, i) => (
          <div
            key={s}
            className={`h-1.5 rounded-full transition-all ${
              step === s
                ? "w-8 bg-[#ff6b4a]"
                : i < currentIndex
                ? "w-1.5 bg-white/40"
                : "w-1.5 bg-white/20"
            }`}
          />
        ))}
      </div>
    </div>
  );
}
