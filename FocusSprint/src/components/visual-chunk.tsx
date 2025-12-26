"use client";

import { motion } from "framer-motion";
import { 
  BookOpen, Lightbulb, Target, Layers, ArrowRight,
  CheckCircle2, Circle, ChevronRight
} from "lucide-react";
import { loadPreferences } from "@/lib/user-preferences";

interface VisualChunkProps {
  title: string;
  summary?: string;
  keyConceptsList?: string[];
  difficulty?: string;
  sequenceNumber: number;
  totalChunks: number;
  isCompleted?: boolean;
}

// Difficulty color mapping
const DIFFICULTY_COLORS: Record<string, { bg: string; text: string; label: string }> = {
  easy: { bg: "bg-[#10b981]/20", text: "text-[#10b981]", label: "Easy" },
  medium: { bg: "bg-[#f59e0b]/20", text: "text-[#f59e0b]", label: "Medium" },
  hard: { bg: "bg-[#ef4444]/20", text: "text-[#ef4444]", label: "Challenging" },
};

// Icons for concepts
const CONCEPT_ICONS = [
  Lightbulb,
  Target,
  Layers,
  BookOpen,
];

/**
 * Visual representation of a content chunk.
 * Designed for users who learn better visually.
 */
export function VisualChunk({
  title,
  summary,
  keyConceptsList = [],
  difficulty = "medium",
  sequenceNumber,
  totalChunks,
  isCompleted = false,
}: VisualChunkProps) {
  const difficultyStyle = DIFFICULTY_COLORS[difficulty] || DIFFICULTY_COLORS.medium;
  const prefs = loadPreferences();
  
  return (
    <div className="space-y-6">
      {/* Progress Breadcrumb */}
      <div className="flex items-center gap-2 overflow-x-auto pb-2">
        {Array.from({ length: totalChunks }).map((_, i) => (
          <div key={i} className="flex items-center">
            <div
              className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-medium transition-all ${
                i < sequenceNumber - 1
                  ? "bg-[#10b981] text-white"
                  : i === sequenceNumber - 1
                  ? "bg-[#ff6b4a] text-white"
                  : "bg-[#2a2a3e] text-[#8888a0]"
              }`}
            >
              {i < sequenceNumber - 1 ? (
                <CheckCircle2 className="w-4 h-4" />
              ) : (
                i + 1
              )}
            </div>
            {i < totalChunks - 1 && (
              <ChevronRight className="w-4 h-4 text-[#8888a0] mx-1" />
            )}
          </div>
        ))}
      </div>
      
      {/* Main Content Card */}
      <motion.div
        className="bg-[#13131f] border border-[#2a2a3e] rounded-3xl p-6"
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
      >
        {/* Header */}
        <div className="flex items-start justify-between mb-4">
          <div>
            <h2 className="text-2xl font-bold text-white mb-1">{title}</h2>
            <p className="text-sm text-[#8888a0]">
              Section {sequenceNumber} of {totalChunks}
            </p>
          </div>
          
          {/* Difficulty Badge */}
          <span className={`px-3 py-1 rounded-full text-xs font-medium ${difficultyStyle.bg} ${difficultyStyle.text}`}>
            {difficultyStyle.label}
          </span>
        </div>
        
        {/* Summary with visual styling */}
        {summary && (
          <div className="mb-6">
            <div className="flex items-start gap-3 p-4 bg-[#1e1e2e] rounded-xl border-l-4 border-[#ff6b4a]">
              <BookOpen className="w-5 h-5 text-[#ff6b4a] mt-0.5 flex-shrink-0" />
              <p className="text-[#d4d4d8] leading-relaxed">
                {summary}
              </p>
            </div>
          </div>
        )}
        
        {/* Key Concepts as visual cards */}
        {prefs.visualAidsEnabled && keyConceptsList.length > 0 && (
          <div className="space-y-3">
            <h3 className="text-sm font-medium text-[#8888a0] uppercase tracking-wider">
              Key Concepts
            </h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
              {keyConceptsList.map((concept, i) => {
                const Icon = CONCEPT_ICONS[i % CONCEPT_ICONS.length];
                return (
                  <motion.div
                    key={i}
                    className="flex items-center gap-3 p-4 bg-[#1e1e2e] rounded-xl border border-[#2a2a3e] hover:border-[#3a3a4e] transition-colors"
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.1 }}
                  >
                    <div className="p-2 rounded-lg bg-[#2a2a3e]">
                      <Icon className="w-4 h-4 text-[#8888a0]" />
                    </div>
                    <span className="text-sm text-white">{concept}</span>
                  </motion.div>
                );
              })}
            </div>
          </div>
        )}
      </motion.div>
    </div>
  );
}

/**
 * Compact visual card for cards mode display
 */
export function ConceptCard({
  concept,
  index,
  total,
  isActive,
}: {
  concept: string;
  index: number;
  total: number;
  isActive: boolean;
}) {
  return (
    <motion.div
      className={`min-h-[200px] flex flex-col items-center justify-center p-8 rounded-3xl border-2 transition-all ${
        isActive
          ? "bg-[#ff6b4a]/10 border-[#ff6b4a]"
          : "bg-[#13131f] border-[#2a2a3e]"
      }`}
      initial={{ scale: 0.95, opacity: 0 }}
      animate={{ scale: 1, opacity: 1 }}
    >
      <div className="w-12 h-12 rounded-full bg-[#ff6b4a]/20 flex items-center justify-center mb-6">
        <Lightbulb className="w-6 h-6 text-[#ff6b4a]" />
      </div>
      
      <p className="text-xl text-white text-center font-medium mb-4">
        {concept}
      </p>
      
      <p className="text-sm text-[#8888a0]">
        {index + 1} of {total}
      </p>
    </motion.div>
  );
}

/**
 * Mind map style concept visualization
 */
export function ConceptMindMap({
  title,
  concepts,
}: {
  title: string;
  concepts: string[];
}) {
  if (concepts.length === 0) return null;
  
  return (
    <div className="relative py-8">
      {/* Center node */}
      <div className="flex justify-center mb-8">
        <div className="px-6 py-3 bg-[#ff6b4a] rounded-full text-[#0a0a12] font-bold">
          {title.length > 30 ? title.substring(0, 30) + "..." : title}
        </div>
      </div>
      
      {/* Concept nodes */}
      <div className="flex flex-wrap justify-center gap-4">
        {concepts.map((concept, i) => (
          <motion.div
            key={i}
            className="px-4 py-2 bg-[#1e1e2e] border border-[#2a2a3e] rounded-full text-sm text-white"
            initial={{ opacity: 0, scale: 0.8 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: i * 0.1 }}
          >
            {concept}
          </motion.div>
        ))}
      </div>
    </div>
  );
}

export default VisualChunk;
