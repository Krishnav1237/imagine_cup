"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { BookOpen, Search, Filter, Calendar, Target, Sparkles, Eye } from "lucide-react";
import { AppNav } from "@/components/app-nav";
import { useUser } from "@/lib/user-context";
import { Input } from "@/components/ui/input";

export default function KnowledgeBankPage() {
  const { completedSprints } = useUser();
  const [searchQuery, setSearchQuery] = useState("");
  const [selectedSprint, setSelectedSprint] = useState<typeof completedSprints[0] | null>(null);

  const filteredSprints = completedSprints.filter(
    (sprint) =>
      sprint.concept.toLowerCase().includes(searchQuery.toLowerCase()) ||
      sprint.contentTitle.toLowerCase().includes(searchQuery.toLowerCase())
  );

  const groupedByContent = filteredSprints.reduce((acc, sprint) => {
    if (!acc[sprint.contentTitle]) {
      acc[sprint.contentTitle] = [];
    }
    acc[sprint.contentTitle].push(sprint);
    return acc;
  }, {} as Record<string, typeof completedSprints>);

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white">
      <AppNav />
      
      <div className="pt-32 pb-20 px-6">
        <div className="max-w-7xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <div className="inline-flex items-center gap-2 glass px-4 py-2 rounded-full mb-6">
              <BookOpen className="w-4 h-4 text-[#06b6d4]" />
              <span className="text-sm text-[#8888a0]">Your Learning Archive</span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-4">
              Knowledge <span className="gradient-text">Bank</span>
            </h1>
            <p className="text-xl text-[#8888a0] max-w-2xl mx-auto">
              Review all your completed sprints and visual summaries in one place
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="mb-8 flex flex-col md:flex-row gap-4"
          >
            <div className="flex-1 relative">
              <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-[#8888a0]" />
              <Input
                type="text"
                placeholder="Search sprints by concept or content..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="pl-12 bg-[#1e1e2e] border-[#2a2a3e] text-white h-12 rounded-xl"
              />
            </div>
            <div className="flex gap-2">
              <button className="glass px-6 py-3 rounded-xl flex items-center gap-2 text-sm hover:border-white/20 transition-colors">
                <Filter className="w-4 h-4" />
                Filter
              </button>
              <button className="glass px-6 py-3 rounded-xl flex items-center gap-2 text-sm hover:border-white/20 transition-colors">
                <Calendar className="w-4 h-4" />
                Sort
              </button>
            </div>
          </motion.div>

          {completedSprints.length === 0 ? (
            <motion.div
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6, delay: 0.3 }}
              className="glass rounded-3xl p-12 text-center"
            >
              <BookOpen className="w-20 h-20 text-[#8888a0] mx-auto mb-6" />
              <h2 className="text-2xl font-bold mb-3">Your Knowledge Bank is Empty</h2>
              <p className="text-[#8888a0] mb-8 max-w-md mx-auto">
                Complete your first sprint to start building your visual learning archive
              </p>
              <a
                href="/upload"
                className="inline-block bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold px-8 py-4 rounded-xl transition-colors"
              >
                Start Learning
              </a>
            </motion.div>
          ) : (
            <div className="space-y-8">
              {Object.entries(groupedByContent).map(([contentTitle, sprints], groupIndex) => (
                <motion.div
                  key={contentTitle}
                  initial={{ opacity: 0, y: 40 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.6, delay: 0.3 + groupIndex * 0.1 }}
                  className="glass rounded-2xl p-6"
                >
                  <div className="flex items-center gap-3 mb-6">
                    <div className="w-12 h-12 rounded-xl bg-[#7c3aed]/20 flex items-center justify-center">
                      <Target className="w-6 h-6 text-[#7c3aed]" />
                    </div>
                    <div>
                      <h2 className="text-xl font-bold">{contentTitle}</h2>
                      <p className="text-sm text-[#8888a0]">{sprints.length} sprints completed</p>
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
                    {sprints.map((sprint, i) => (
                      <motion.button
                        key={sprint.id}
                        onClick={() => setSelectedSprint(sprint)}
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        transition={{ duration: 0.3, delay: i * 0.05 }}
                        className="group text-left"
                      >
                        <div className="relative aspect-[3/4] rounded-xl overflow-hidden mb-3 bg-[#1e1e2e]">
                          <img
                            src={sprint.infographic}
                            alt={sprint.concept}
                            className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-500"
                          />
                          <div className="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent" />
                          <div className="absolute top-3 left-3">
                            <div className="px-2 py-1 rounded-lg bg-[#7c3aed]/80 backdrop-blur-sm text-xs font-semibold">
                              Sprint {sprint.sprintNumber}
                            </div>
                          </div>
                          <div className="absolute bottom-3 left-3 right-3">
                            <p className="text-sm font-semibold text-white line-clamp-2">{sprint.concept}</p>
                          </div>
                        </div>
                        <div className="px-2">
                          <p className="text-xs text-[#8888a0]">
                            {new Date(sprint.timestamp).toLocaleDateString()}
                          </p>
                        </div>
                      </motion.button>
                    ))}
                  </div>
                </motion.div>
              ))}
            </div>
          )}

          {selectedSprint && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/80 backdrop-blur-sm z-50 flex items-center justify-center p-6"
              onClick={() => setSelectedSprint(null)}
            >
              <motion.div
                initial={{ scale: 0.9, y: 20 }}
                animate={{ scale: 1, y: 0 }}
                exit={{ scale: 0.9, y: 20 }}
                onClick={(e) => e.stopPropagation()}
                className="glass rounded-3xl p-8 max-w-4xl w-full max-h-[90vh] overflow-y-auto"
              >
                <div className="flex items-start justify-between mb-6">
                  <div>
                    <div className="flex items-center gap-2 mb-2">
                      <div className="px-3 py-1 rounded-full bg-[#7c3aed]/20 text-[#7c3aed] text-xs font-semibold">
                        Sprint {selectedSprint.sprintNumber} of {selectedSprint.totalSprints}
                      </div>
                      <div className="px-3 py-1 rounded-full bg-[#10b981]/20 text-[#10b981] text-xs font-semibold flex items-center gap-1">
                        <Eye className="w-3 h-3" />
                        Completed
                      </div>
                    </div>
                    <h2 className="text-3xl font-bold mb-1">{selectedSprint.concept}</h2>
                    <p className="text-[#8888a0]">{selectedSprint.contentTitle}</p>
                  </div>
                  <button
                    onClick={() => setSelectedSprint(null)}
                    className="w-10 h-10 rounded-xl bg-[#1e1e2e] hover:bg-[#2a2a3e] flex items-center justify-center transition-colors"
                  >
                    <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                    </svg>
                  </button>
                </div>

                <div className="aspect-[4/3] rounded-2xl overflow-hidden mb-6">
                  <img
                    src={selectedSprint.infographic}
                    alt={selectedSprint.concept}
                    className="w-full h-full object-cover"
                  />
                </div>

                <div className="glass rounded-xl p-6 mb-6">
                  <div className="flex items-center gap-2 mb-3">
                    <Sparkles className="w-5 h-5 text-[#f59e0b]" />
                    <h3 className="font-semibold">Summary</h3>
                  </div>
                  <p className="text-[#8888a0] leading-relaxed">{selectedSprint.summary}</p>
                </div>

                <div className="flex items-center justify-between text-sm text-[#8888a0]">
                  <div>Completed on {new Date(selectedSprint.timestamp).toLocaleDateString()}</div>
                  <div>Duration: {Math.floor(selectedSprint.duration / 60)} minutes</div>
                </div>
              </motion.div>
            </motion.div>
          )}
        </div>
      </div>
    </div>
  );
}
