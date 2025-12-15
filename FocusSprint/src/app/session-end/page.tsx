"use client";

import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import { CheckCircle, Coffee, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useEffect, useState } from "react";

export default function SessionEndPage() {
  const router = useRouter();
  const [focusQuality, setFocusQuality] = useState(87);

  useEffect(() => {
    // Calculate focus quality from session data
    const sessionData = localStorage.getItem("last_session_focus");
    if (sessionData) {
      setFocusQuality(parseInt(sessionData));
    }
  }, []);

  const getMessage = () => {
    if (focusQuality >= 90) {
      return "You stayed incredibly focused throughout this session.";
    } else if (focusQuality >= 70) {
      return "You stayed focused for most of this session.";
    } else {
      return "You made progress in this session.";
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white flex items-center justify-center px-6">
      <div className="max-w-2xl w-full text-center">
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          transition={{ duration: 0.5, ease: [0.22, 1, 0.36, 1] }}
          className="mb-8"
        >
          <div className="w-32 h-32 rounded-full bg-gradient-to-br from-[#10b981] to-[#06b6d4] flex items-center justify-center mx-auto">
            <CheckCircle className="w-16 h-16 text-white" />
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
        >
          <h1 className="text-4xl md:text-5xl font-bold mb-4">
            Session <span className="gradient-text">complete</span>
          </h1>
          <p className="text-xl text-[#8888a0] mb-8 max-w-md mx-auto">
            {getMessage()}
            <br />
            <span className="text-white font-semibold">That's progress.</span>
          </p>

          <div className="glass rounded-2xl p-8 mb-12 max-w-md mx-auto">
            <div className="flex items-center justify-between mb-4">
              <span className="text-[#8888a0]">Session Focus Quality</span>
              <span className="text-2xl font-bold text-[#10b981]">{focusQuality}%</span>
            </div>
            <div className="h-2 bg-[#1e1e2e] rounded-full overflow-hidden">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${focusQuality}%` }}
                transition={{ duration: 1, delay: 0.5 }}
                className="h-full bg-gradient-to-r from-[#10b981] to-[#06b6d4]"
              />
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Button
              onClick={() => router.push("/dashboard")}
              className="bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold px-8 py-6 text-lg"
            >
              Continue Learning
              <ArrowRight className="w-5 h-5 ml-2" />
            </Button>
            <Button
              onClick={() => router.push("/dashboard")}
              variant="outline"
              className="border-[#2a2a3e] bg-transparent hover:bg-[#1e1e2e] px-8 py-6 text-lg"
            >
              Take a break
              <Coffee className="w-5 h-5 ml-2" />
            </Button>
          </div>

          <p className="text-sm text-[#8888a0] mt-8">
            Remember: Consistency matters more than perfection
          </p>
        </motion.div>
      </div>
    </div>
  );
}
