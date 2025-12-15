"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Youtube, FileText, Presentation, Loader2, Sparkles, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AppNav } from "@/components/app-nav";
import { useUser } from "@/lib/user-context";
import { UserProgress, SprintData } from "@/lib/user-context";

export default function UploadPage() {
  const router = useRouter();
  const { setProgress } = useUser();
  const [activeTab, setActiveTab] = useState<"youtube" | "pdf" | "ppt">("youtube");
  const [input, setInput] = useState("");
  const [processing, setProcessing] = useState(false);
  const [file, setFile] = useState<File | null>(null);

  const handleProcess = async () => {
    if (!input && !file) return;

    setProcessing(true);

    await new Promise((resolve) => setTimeout(resolve, 3000));

    const mockSprints: SprintData[] = Array.from({ length: 12 }, (_, i) => ({
      id: `sprint-${i + 1}`,
      contentTitle: activeTab === "youtube" ? "Introduction to Python Programming" : file?.name || "Uploaded Content",
      sprintNumber: i + 1,
      totalSprints: 12,
      duration: 300,
      completed: false,
      infographic: `https://images.unsplash.com/photo-${1550000000000 + i * 1000000}?w=800&h=1200&fit=crop`,
      summary: `Sprint ${i + 1} covers key concepts and practical applications. This segment focuses on fundamental principles and hands-on examples.`,
      concept: [
        "Variables & Data Types",
        "Control Flow",
        "Functions",
        "Lists & Dictionaries",
        "Loops",
        "String Operations",
        "File Handling",
        "Error Handling",
        "Modules",
        "Object-Oriented Programming",
        "Advanced Concepts",
        "Final Review",
      ][i],
      timestamp: Date.now(),
    }));

    const progress: UserProgress = {
      currentContentId: `content-${Date.now()}`,
      currentSprintIndex: 0,
      sprints: mockSprints,
      totalSprints: 12,
      contentTitle: activeTab === "youtube" ? "Introduction to Python Programming" : file?.name || "Uploaded Content",
      contentType: activeTab,
      contentUrl: activeTab === "youtube" ? input : file?.name || "",
    };

    setProgress(progress);
    setProcessing(false);
    router.push("/sprint");
  };

  const tabs = [
    { id: "youtube" as const, label: "YouTube", icon: Youtube, color: "#ff6b4a" },
    { id: "pdf" as const, label: "PDF", icon: FileText, color: "#7c3aed" },
    { id: "ppt" as const, label: "Slides", icon: Presentation, color: "#06b6d4" },
  ];

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white">
      <AppNav />
      
      <div className="pt-32 pb-20 px-6">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="text-center mb-12"
          >
            <div className="inline-flex items-center gap-2 glass px-4 py-2 rounded-full mb-6">
              <Sparkles className="w-4 h-4 text-[#f59e0b]" />
              <span className="text-sm text-[#8888a0]">AI-Powered Content Metabolizer</span>
            </div>
            <h1 className="text-5xl md:text-6xl font-bold mb-4">
              Transform Content Into <span className="gradient-text">Sprints</span>
            </h1>
            <p className="text-xl text-[#8888a0] max-w-2xl mx-auto">
              Upload any learning material. Our AI will break it down into focused 5-minute sprints.
            </p>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, y: 40 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="glass rounded-3xl p-8"
          >
            <div className="flex gap-2 mb-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => {
                    setActiveTab(tab.id);
                    setInput("");
                    setFile(null);
                  }}
                  className={`flex-1 flex items-center justify-center gap-2 px-6 py-4 rounded-xl transition-all ${
                    activeTab === tab.id
                      ? "bg-[#1e1e2e] border border-white/20"
                      : "bg-transparent border border-[#2a2a3e] hover:border-white/10"
                  }`}
                >
                  <tab.icon className="w-5 h-5" style={{ color: activeTab === tab.id ? tab.color : "#8888a0" }} />
                  <span className={activeTab === tab.id ? "text-white" : "text-[#8888a0]"}>{tab.label}</span>
                </button>
              ))}
            </div>

            {activeTab === "youtube" ? (
              <div className="space-y-4">
                <label className="block text-sm text-[#8888a0] mb-2">YouTube URL</label>
                <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder="https://www.youtube.com/watch?v=..."
                  className="w-full px-6 py-4 rounded-xl bg-[#1e1e2e] border border-[#2a2a3e] text-white placeholder:text-[#8888a0] focus:outline-none focus:border-[#ff6b4a] transition-colors"
                />
                <p className="text-sm text-[#8888a0]">
                  Paste any YouTube video URL. The AI will transcribe and analyze the content.
                </p>
              </div>
            ) : (
              <div className="space-y-4">
                <label className="block text-sm text-[#8888a0] mb-2">
                  Upload {activeTab === "pdf" ? "PDF" : "PowerPoint"} File
                </label>
                <div
                  className="border-2 border-dashed border-[#2a2a3e] rounded-xl p-12 text-center hover:border-white/20 transition-colors cursor-pointer"
                  onClick={() => document.getElementById("file-input")?.click()}
                >
                  {file ? (
                    <div className="flex items-center justify-center gap-3">
                      <FileText className="w-8 h-8 text-[#7c3aed]" />
                      <div className="text-left">
                        <p className="font-medium">{file.name}</p>
                        <p className="text-sm text-[#8888a0]">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <div className="w-16 h-16 rounded-2xl bg-[#1e1e2e] flex items-center justify-center mx-auto mb-4">
                        {activeTab === "pdf" ? (
                          <FileText className="w-8 h-8 text-[#7c3aed]" />
                        ) : (
                          <Presentation className="w-8 h-8 text-[#06b6d4]" />
                        )}
                      </div>
                      <p className="text-white mb-2">Click to upload or drag and drop</p>
                      <p className="text-sm text-[#8888a0]">
                        {activeTab === "pdf" ? "PDF files up to 50MB" : "PPT/PPTX files up to 50MB"}
                      </p>
                    </div>
                  )}
                </div>
                <input
                  id="file-input"
                  type="file"
                  accept={activeTab === "pdf" ? ".pdf" : ".ppt,.pptx"}
                  onChange={(e) => setFile(e.target.files?.[0] || null)}
                  className="hidden"
                />
              </div>
            )}

            <div className="mt-8 p-6 rounded-xl bg-gradient-to-br from-[#ff6b4a]/10 to-[#7c3aed]/10 border border-[#ff6b4a]/20">
              <h3 className="font-semibold mb-3 flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-[#f59e0b]" />
                What happens next?
              </h3>
              <ul className="space-y-2 text-sm text-[#8888a0]">
                <li className="flex items-start gap-2">
                  <ChevronRight className="w-4 h-4 text-[#ff6b4a] mt-0.5 flex-shrink-0" />
                  <span>AI analyzes your content and identifies key concepts</span>
                </li>
                <li className="flex items-start gap-2">
                  <ChevronRight className="w-4 h-4 text-[#ff6b4a] mt-0.5 flex-shrink-0" />
                  <span>Content is broken into 5-minute micro-sprints</span>
                </li>
                <li className="flex items-start gap-2">
                  <ChevronRight className="w-4 h-4 text-[#ff6b4a] mt-0.5 flex-shrink-0" />
                  <span>Each sprint ends with a visual summary and quiz</span>
                </li>
                <li className="flex items-start gap-2">
                  <ChevronRight className="w-4 h-4 text-[#ff6b4a] mt-0.5 flex-shrink-0" />
                  <span>Earn Focus Coins for completing sprints with good focus</span>
                </li>
              </ul>
            </div>

            <Button
              onClick={handleProcess}
              disabled={processing || (!input && !file)}
              className="w-full bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold px-8 py-6 text-lg rounded-xl mt-8 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {processing ? (
                <>
                  <Loader2 className="w-5 h-5 animate-spin mr-2" />
                  Processing Content...
                </>
              ) : (
                <>
                  Start Sprint Session
                  <ChevronRight className="w-5 h-5 ml-2" />
                </>
              )}
            </Button>
          </motion.div>

          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ duration: 0.6, delay: 0.4 }}
            className="mt-8 text-center text-sm text-[#8888a0]"
          >
            <p>Your content is processed locally and securely. We respect your privacy.</p>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
