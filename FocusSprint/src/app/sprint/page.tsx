"use client";

import { useEffect, useState, Suspense } from "react";
import { useSearchParams, useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowRight, CheckCircle2, ChevronLeft, Trophy, PlayCircle } from "lucide-react";
import { Button } from "@/components/ui/button";
import { useUser } from "@/lib/user-context";
import { AppNav } from "@/components/app-nav";

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
  summary: string;
  text_content: string;
  duration_seconds: number;
  sequence_number: number;
  quiz_questions: QuizQuestion[];
}

interface ContentDetail {
  id: number;
  title: string;
  source_type: string;
  source_url?: string;
  chunks: Chunk[];
}

function SprintContent() {
  const searchParams = useSearchParams();
  const router = useRouter();
  const contentId = searchParams.get("id");
  const { addCoins, syncWithBackend } = useUser();

  const [content, setContent] = useState<ContentDetail | null>(null);
  const [currentChunkIndex, setCurrentChunkIndex] = useState(0);
  const [mode, setMode] = useState<"learn" | "quiz" | "summary">("learn");
  const [quizScore, setQuizScore] = useState(0);
  const [loading, setLoading] = useState(true);
  const [authMissing, setAuthMissing] = useState(false);

  // Fetch Data
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

  if (authMissing) {
    return (
      <div className="min-h-screen bg-[#0a0a12] flex items-center justify-center text-white">
        Redirecting to sign in...
      </div>
    );
  }

  if (loading || !content) {
    return <div className="min-h-screen bg-[#0a0a12] flex items-center justify-center text-white">Loading Sprint...</div>;
  }

  const currentChunk = content.chunks[currentChunkIndex];
  const isLastChunk = currentChunkIndex === content.chunks.length - 1;

  const handleChunkComplete = async () => {
    const token = localStorage.getItem("focus_token");
    
    // Simulate attention score (in a real app, integrate eye-tracking or interaction rates)
    const simulatedAttention = Math.floor(Math.random() * (100 - 80 + 1) + 80); 
    
    // Call API
    try {
      const res = await fetch(`${API_URL}/content/${contentId}/chunks/${currentChunk.id}/complete`, {
        method: "POST",
        headers: { 
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({
          quiz_score: 100, // Assuming 100 for simple completion flow
          average_attention: simulatedAttention,
          time_spent_seconds: currentChunk.duration_seconds
        })
      });

      if (res.ok) {
        const data = await res.json();
        if (data.coins_earned > 0) {
          addCoins(data.coins_earned);
        }
      }
    } catch (e) {
      console.error("Failed to record progress", e);
    }

    if (isLastChunk) {
      router.push("/dashboard"); // Or a summary page
    } else {
      setCurrentChunkIndex(prev => prev + 1);
      setMode("learn");
    }
  };

  return (
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
            </div>
            <h1 className="text-3xl font-bold">{currentChunk.title}</h1>
          </div>
          <div className="text-right">
             <div className="text-2xl font-bold font-mono text-[#ff6b4a]">
               {Math.floor(currentChunk.duration_seconds / 60)}:{(currentChunk.duration_seconds % 60).toString().padStart(2, '0')}
             </div>
             <span className="text-xs text-[#8888a0]">Est. Time</span>
          </div>
        </header>

        {/* Content Area */}
        <div className="flex-1 grid grid-cols-1 lg:grid-cols-3 gap-8">
          
          {/* Left: Main Content */}
          <div className="lg:col-span-2 space-y-6">
            <div className="bg-[#13131f] border border-[#2a2a3e] rounded-3xl overflow-hidden aspect-video relative group">
              {content.source_type === "youtube" ? (
                 <div className="w-full h-full flex items-center justify-center bg-black/50">
                    {/* Placeholder for actual YouTube Embed */}
                    <PlayCircle className="w-16 h-16 text-white/50 group-hover:text-[#ff6b4a] transition-colors" />
                    <p className="absolute bottom-4 text-sm text-white/70">Video Sync active for timestamp {currentChunk.sequence_number * 5}:00</p>
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
                {/* Fallback if key_concepts is missing in API response for now */}
                {(['Focus', 'Attention', 'Dopamine']).map((concept, i) => (
                  <span key={i} className="px-3 py-1 bg-[#1e1e2e] rounded-full text-sm border border-[#2a2a3e] text-[#8888a0]">
                    {concept}
                  </span>
                ))}
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
    </div>
  );
}

export default function SprintPage() {
  return (
    <Suspense fallback={<div className="min-h-screen bg-[#0a0a12] text-white flex items-center justify-center">Loading...</div>}>
      <SprintContent />
    </Suspense>
  );
}