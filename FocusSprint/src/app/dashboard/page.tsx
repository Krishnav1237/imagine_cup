"use client";

import { motion } from "framer-motion";
import { useRouter } from "next/navigation";
import Link from "next/link";
import { Play, Upload, Youtube, FileText, Presentation } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AppNav } from "@/components/app-nav";
import { useUser } from "@/lib/user-context";
import { useEffect, useState } from "react";

export default function DashboardPage() {
  const router = useRouter();
  const { currentProgress, completedSprints } = useUser();
  const [greeting, setGreeting] = useState("Good evening");
  const [userName, setUserName] = useState("Learner");

  useEffect(() => {
    const hour = new Date().getHours();
    if (hour < 12) setGreeting("Good morning");
    else if (hour < 18) setGreeting("Good afternoon");
    else setGreeting("Good evening");

    const savedName = localStorage.getItem("focusflow_username");
    if (savedName) setUserName(savedName);
  }, []);

  const focusRingProgress = completedSprints.length % 7;

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white">
      <AppNav />

      <div className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto">
          {/* Greeting */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-12"
          >
            <h1 className="text-4xl md:text-5xl font-bold mb-2">
              {greeting}, <span className="gradient-text">{userName}</span>
            </h1>
          </motion.div>

          {/* Continue Learning Section */}
          {currentProgress && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.6, delay: 0.1 }}
              className="mb-8"
            >
              <button
                onClick={() => router.push("/sprint")}
                className="w-full glass rounded-3xl p-8 hover:border-white/20 transition-all group text-left"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center gap-3">
                    <div className="w-12 h-12 rounded-xl bg-[#ff6b4a]/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                      <Play className="w-6 h-6 text-[#ff6b4a]" />
                    </div>
                    <div>
                      <h2 className="text-2xl font-bold">Continue Learning</h2>
                      <p className="text-[#8888a0]">
                        Last topic: {currentProgress.sprints[currentProgress.currentSprintIndex]?.concept}
                      </p>
                    </div>
                  </div>
                  <div className="text-right">
                    <div className="text-3xl font-bold text-[#ff6b4a]">
                      {Math.ceil((currentProgress.totalSprints - currentProgress.currentSprintIndex) * 5 / 60)}m
                    </div>
                    <div className="text-sm text-[#8888a0]">left</div>
                  </div>
                </div>
                <div className="h-2 bg-[#1e1e2e] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-[#ff6b4a] to-[#f59e0b]"
                    style={{
                      width: `${(currentProgress.currentSprintIndex / currentProgress.totalSprints) * 100}%`,
                    }}
                  />
                </div>
              </button>
            </motion.div>
          )}

          {/* Today's Focus - GitHub Style Heatmap */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="glass rounded-3xl p-8 mb-8"
          >
            <div className="flex items-center justify-between mb-6">
              <h3 className="text-xl font-semibold">Your Focus Activity</h3>
              <div className="text-sm text-[#8888a0]">
                {completedSprints.length} sessions this week
              </div>
            </div>
            
            {/* GitHub-style contribution graph */}
            <div className="space-y-2">
              <div className="flex gap-2 items-end">
                <div className="flex flex-col gap-1 text-xs text-[#8888a0] justify-between" style={{height: '91px'}}>
                  <span>Mon</span>
                  <span>Wed</span>
                  <span>Fri</span>
                </div>
                <div className="flex-1 grid grid-cols-53 gap-[3px]">
                  {[...Array(371)].map((_, i) => {
                    const dayOffset = 370 - i;
                    // Only show activity on today's square (last square) based on completed sprints
                    // In the future, this should track actual dates from sprint completion timestamps
                    const isToday = dayOffset === 0;
                    const activity = isToday ? completedSprints.length : 0;
                    const intensity = activity === 0 ? 0 : activity <= 2 ? 1 : activity <= 4 ? 2 : activity <= 6 ? 3 : 4;
                    
                    return (
                      <div
                        key={i}
                        className={`w-[10px] h-[10px] rounded-[2px] transition-all hover:ring-1 hover:ring-white/50 cursor-pointer ${
                          intensity === 0
                            ? "bg-[#161b22]"
                            : intensity === 1
                            ? "bg-[#0e4429]"
                            : intensity === 2
                            ? "bg-[#006d32]"
                            : intensity === 3
                            ? "bg-[#26a641]"
                            : "bg-[#39d353]"
                        }`}
                        title={`${activity} sessions ${dayOffset} days ago`}
                      />
                    );
                  })}
                </div>
              </div>
              <div className="flex items-center justify-end gap-2 mt-4 text-xs text-[#8888a0]">
                <span>Less</span>
                <div className="flex gap-[3px]">
                  <div className="w-[10px] h-[10px] bg-[#161b22] rounded-[2px]" />
                  <div className="w-[10px] h-[10px] bg-[#0e4429] rounded-[2px]" />
                  <div className="w-[10px] h-[10px] bg-[#006d32] rounded-[2px]" />
                  <div className="w-[10px] h-[10px] bg-[#26a641] rounded-[2px]" />
                  <div className="w-[10px] h-[10px] bg-[#39d353] rounded-[2px]" />
                </div>
                <span>More</span>
              </div>
            </div>
          </motion.div>

          {/* Add New Content */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.3 }}
            className="glass rounded-3xl p-8"
          >
            <h3 className="text-xl font-semibold mb-6">Add New Content</h3>

            <div className="space-y-4">
              <Link href="/upload" className="block">
                <button className="w-full p-6 rounded-xl bg-[#1e1e2e] border border-[#2a2a3e] hover:border-white/20 transition-all text-left group">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-[#ff6b4a]/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                      <Youtube className="w-6 h-6 text-[#ff6b4a]" />
                    </div>
                    <div>
                      <div className="font-semibold mb-1">Paste YouTube URL</div>
                      <div className="text-sm text-[#8888a0]">
                        We'll break it into focus-sized chunks
                      </div>
                    </div>
                  </div>
                </button>
              </Link>

              <Link href="/upload" className="block">
                <button className="w-full p-6 rounded-xl bg-[#1e1e2e] border border-[#2a2a3e] hover:border-white/20 transition-all text-left group">
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-[#7c3aed]/20 flex items-center justify-center group-hover:scale-110 transition-transform">
                      <Upload className="w-6 h-6 text-[#7c3aed]" />
                    </div>
                    <div>
                      <div className="font-semibold mb-1">Upload File</div>
                      <div className="text-sm text-[#8888a0] flex gap-2">
                        <span className="flex items-center gap-1">
                          <FileText className="w-3 h-3" /> PDF
                        </span>
                        <span className="flex items-center gap-1">
                          <Presentation className="w-3 h-3" /> PPT
                        </span>
                        <span className="flex items-center gap-1">
                          <FileText className="w-3 h-3" /> DOC
                        </span>
                      </div>
                    </div>
                  </div>
                </button>
              </Link>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
