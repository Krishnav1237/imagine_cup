"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { Youtube, FileText, Presentation, Loader2, Sparkles } from "lucide-react";
import { Button } from "@/components/ui/button";
import { AppNav } from "@/components/app-nav";

// Use environment variable for API URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

export default function UploadPage() {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<"youtube" | "pdf" | "ppt">("youtube");
  const [input, setInput] = useState("");
  const [file, setFile] = useState<File | null>(null);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState("");
  const [statusMessage, setStatusMessage] = useState("");

  // Poll the backend until status is 'completed' or 'failed'
  const pollStatus = async (contentId: number, token: string) => {
    const maxRetries = 60; // ~2 minutes timeout
    let retries = 0;

    const interval = setInterval(async () => {
      retries++;
      try {
        const res = await fetch(`${API_URL}/content/${contentId}`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        
        if (!res.ok) throw new Error("Failed to check status");
        
        const data = await res.json();
        
        if (data.status === "completed") {
          clearInterval(interval);
          setStatusMessage("Ready! Redirecting...");
          router.push(`/sprint?id=${contentId}`);
        } else if (data.status === "failed") {
          clearInterval(interval);
          setProcessing(false);
          setError(data.error_message || "Processing failed. Please try again.");
        } else {
          // Update status message based on backend state (pending, processing)
          setStatusMessage(`Analyzing content... (${data.status})`);
        }

        if (retries >= maxRetries) {
          clearInterval(interval);
          setProcessing(false);
          setError("Processing timed out. Please check 'My Content' later.");
        }
      } catch (err) {
        console.error(err);
        // Don't stop polling on transient network errors, but you could add logic here
      }
    }, 2000);
  };

  const handleProcess = async () => {
    if (!input && !file) return;
    setProcessing(true);
    setError("");
    setStatusMessage("Uploading...");

    try {
      const token = localStorage.getItem("focus_token");
      if (!token) {
        router.push("/signin");
        return;
      }

      const formData = new FormData();
      // Map frontend tabs to backend enums
      let type = "youtube";
      if (activeTab === "pdf") type = "pdf";
      if (activeTab === "ppt") type = "pptx";

      formData.append("source_type", type);
      
      if (activeTab === "youtube") {
        formData.append("source_url", input);
      } else if (file) {
        formData.append("file", file);
      }

      // 1. Upload
      const res = await fetch(`${API_URL}/content/upload`, {
        method: "POST",
        headers: { Authorization: `Bearer ${token}` },
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Upload failed");
      }

      const data = await res.json();
      
      // 2. Start Polling
      setStatusMessage("Queued for processing...");
      pollStatus(data.id, token);

    } catch (err: any) {
      setError(err.message);
      setProcessing(false);
    }
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
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} className="text-center mb-12">
            <h1 className="text-5xl font-bold mb-4">Transform Content Into <span className="text-[#ff6b4a]">Sprints</span></h1>
            <p className="text-[#8888a0]">Upload material to generate AI-powered learning chunks.</p>
          </motion.div>

          <motion.div className="glass rounded-3xl p-8 bg-[#13131f] border border-[#2a2a3e]">
            {error && (
              <div className="mb-4 p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-400 text-sm">
                {error}
              </div>
            )}

            {/* Tabs */}
            <div className="flex gap-2 mb-8">
              {tabs.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => { setActiveTab(tab.id); setInput(""); setFile(null); }}
                  className={`flex-1 flex items-center justify-center gap-2 px-6 py-4 rounded-xl border transition-all ${
                    activeTab === tab.id 
                      ? "bg-[#1e1e2e] border-white/20 text-white" 
                      : "border-transparent hover:bg-[#1e1e2e] text-[#8888a0]"
                  }`}
                >
                  <tab.icon className="w-5 h-5" style={{ color: tab.color }} />
                  <span>{tab.label}</span>
                </button>
              ))}
            </div>

            {/* Input Area */}
            <div className="min-h-[200px] flex flex-col justify-center">
              {activeTab === "youtube" ? (
                <div className="space-y-4">
                  <input
                    type="text"
                    value={input}
                    onChange={(e) => setInput(e.target.value)}
                    placeholder="https://www.youtube.com/watch?v=..."
                    className="w-full px-6 py-4 rounded-xl bg-[#0a0a12] border border-[#2a2a3e] text-white focus:border-[#ff6b4a] outline-none"
                  />
                  <p className="text-sm text-[#8888a0]">Our AI will transcribe and analyze the video.</p>
                </div>
              ) : (
                <div 
                  onClick={() => document.getElementById("file-input")?.click()}
                  className="border-2 border-dashed border-[#2a2a3e] rounded-xl p-12 text-center cursor-pointer hover:border-[#ff6b4a]/50 transition-colors"
                >
                  {file ? (
                    <div className="flex items-center justify-center gap-3">
                      <FileText className="w-8 h-8 text-[#7c3aed]" />
                      <div className="text-left">
                        <p className="font-medium text-white">{file.name}</p>
                        <p className="text-sm text-[#8888a0]">{(file.size / 1024 / 1024).toFixed(2)} MB</p>
                      </div>
                    </div>
                  ) : (
                    <div>
                      <p className="text-white mb-2">Click to upload {activeTab.toUpperCase()}</p>
                      <p className="text-sm text-[#8888a0]">Max size 50MB</p>
                    </div>
                  )}
                  <input 
                    id="file-input" 
                    type="file" 
                    accept={activeTab === "pdf" ? ".pdf" : ".ppt,.pptx"}
                    className="hidden" 
                    onChange={(e) => setFile(e.target.files?.[0] || null)} 
                  />
                </div>
              )}
            </div>

            <Button
              onClick={handleProcess}
              disabled={processing || (!input && !file)}
              className="w-full bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold px-8 py-6 text-lg rounded-xl mt-8 disabled:opacity-50"
            >
              {processing ? (
                <><Loader2 className="animate-spin mr-2"/> {statusMessage || "Processing Content..."}</>
              ) : (
                <><Sparkles className="mr-2 w-5 h-5"/> Start Sprint Session</>
              )}
            </Button>
          </motion.div>
        </div>
      </div>
    </div>
  );
}