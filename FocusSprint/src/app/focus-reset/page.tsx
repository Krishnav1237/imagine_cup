"use client";

import { motion } from "framer-motion";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

export default function FocusResetPage() {
  const router = useRouter();
  const [countdown, setCountdown] = useState(30);
  const [phase, setPhase] = useState<"inhale" | "exhale">("inhale");

  useEffect(() => {
    const phaseTimer = setInterval(() => {
      setPhase((prev) => (prev === "inhale" ? "exhale" : "inhale"));
    }, 4000);

    return () => clearInterval(phaseTimer);
  }, []);

  useEffect(() => {
    if (countdown > 0) {
      const timer = setTimeout(() => setCountdown(countdown - 1), 1000);
      return () => clearTimeout(timer);
    }
  }, [countdown]);

  const handleResume = () => {
    router.push("/sprint");
  };

  const handleEnd = () => {
    router.push("/dashboard");
  };

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white flex items-center justify-center px-6">
      <div className="max-w-2xl w-full text-center">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="mb-12"
        >
          <h1 className="text-4xl font-bold mb-4">
            Let's reset for <span className="text-[#f59e0b]">{countdown} seconds</span>
          </h1>
          <p className="text-xl text-[#8888a0]">
            Take a moment to breathe and refocus
          </p>
        </motion.div>

        {/* Breathing Circle */}
        <div className="relative w-80 h-80 mx-auto mb-12">
          {/* Outer ring */}
          <div className="absolute inset-0 rounded-full border-2 border-[#2a2a3e]" />

          {/* Animated breathing circle */}
          <motion.div
            animate={{
              scale: phase === "inhale" ? 1 : 0.6,
              opacity: phase === "inhale" ? 1 : 0.7,
            }}
            transition={{
              duration: 4,
              ease: "easeInOut",
            }}
            className="absolute inset-0 rounded-full bg-gradient-to-br from-[#7c3aed] to-[#06b6d4] flex items-center justify-center"
          >
            <motion.div
              animate={{
                opacity: phase === "inhale" ? 1 : 0.5,
              }}
              transition={{ duration: 4 }}
              className="text-3xl font-bold text-white"
            >
              {phase === "inhale" ? "Inhale..." : "Exhale..."}
            </motion.div>
          </motion.div>

          {/* Pulsing glow effect */}
          <motion.div
            animate={{
              scale: phase === "inhale" ? 1.2 : 0.8,
              opacity: phase === "inhale" ? 0.3 : 0,
            }}
            transition={{
              duration: 4,
              ease: "easeInOut",
            }}
            className="absolute inset-0 rounded-full bg-gradient-to-br from-[#7c3aed] to-[#06b6d4] blur-3xl -z-10"
          />
        </div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="text-[#8888a0] mb-12 text-lg"
        >
          {phase === "inhale" 
            ? "Breathe in slowly through your nose..."
            : "Breathe out slowly through your mouth..."}
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.8 }}
          className="flex gap-4 justify-center"
        >
          <Button
            onClick={handleResume}
            className="bg-[#10b981] hover:bg-[#059669] text-white px-8 py-6 text-lg"
          >
            {countdown === 0 ? "Resume Learning" : "Resume with simpler explanation"}
          </Button>
          <Button
            onClick={handleEnd}
            variant="outline"
            className="border-[#2a2a3e] bg-transparent hover:bg-[#1e1e2e] px-8 py-6 text-lg"
          >
            End session
          </Button>
        </motion.div>
      </div>
    </div>
  );
}
