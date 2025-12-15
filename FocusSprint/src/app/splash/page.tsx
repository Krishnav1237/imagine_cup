"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Zap } from "lucide-react";

export default function SplashScreen() {
  const router = useRouter();

  useEffect(() => {
    const timer = setTimeout(() => {
      // Check if user has completed onboarding
      const hasOnboarded = localStorage.getItem("focusflow_onboarded");
      if (hasOnboarded) {
        router.push("/dashboard");
      } else {
        router.push("/onboarding");
      }
    }, 1500);

    return () => clearTimeout(timer);
  }, [router]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#0a0a12] via-[#1a1a28] to-[#0a0a12] flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.6, ease: [0.22, 1, 0.36, 1] }}
        className="text-center"
      >
        <div className="w-24 h-24 rounded-3xl bg-gradient-to-br from-[#ff6b4a] to-[#f59e0b] flex items-center justify-center mx-auto mb-6">
          <Zap className="w-12 h-12 text-[#0a0a12]" />
        </div>
        <motion.h1
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.2 }}
          className="text-3xl font-bold text-white mb-2"
        >
          FocusFlow
        </motion.h1>
        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ duration: 0.6, delay: 0.4 }}
          className="text-[#8888a0] text-lg"
        >
          Learn at your pace.
        </motion.p>
      </motion.div>
    </div>
  );
}
