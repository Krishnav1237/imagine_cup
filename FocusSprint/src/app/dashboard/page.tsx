"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Play, Plus, Clock, MoreVertical, FileText, Youtube, Presentation } from "lucide-react";
import { AppNav } from "@/components/app-nav";
import { Button } from "@/components/ui/button";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

interface ContentItem {
  id: number;
  title: string;
  source_type: "youtube" | "pdf" | "pptx";
  status: "pending" | "processing" | "completed" | "failed";
  stage?: string | null;
  created_at: string;
}

export default function Dashboard() {
  const [content, setContent] = useState<ContentItem[]>([]);
  const [loading, setLoading] = useState(true);
  const router = useRouter();

  // 🔹 EXISTING useEffect (DO NOT MOVE)
  useEffect(() => {
    const fetchContent = async () => {
      const token = localStorage.getItem("focus_token");
      if (!token) {
        router.push("/signin");
        return;
      }

      try {
        const res = await fetch(`${API_URL}/content/library`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (res.ok) {
          const data = await res.json();
          setContent(data.items ?? data); // depending on backend response
        }
      } catch (error) {
        console.error("Failed to load content", error);
      } finally {
        setLoading(false);
      }
    };

    fetchContent();
  }, [router]);

  // ✅ ADD THIS useEffect HERE (AUTO-REFRESH)
  useEffect(() => {
    const hasProcessing = content.some(c => c.status === "processing");
    if (!hasProcessing) return;

    const interval = setInterval(() => {
      window.location.reload();
    }, 5000);

    return () => clearInterval(interval);
  }, [content]);

  const getIcon = (type: string) => {
    switch (type) {
      case "youtube": return <Youtube className="w-6 h-6 text-[#ff6b4a]" />;
      case "pdf": return <FileText className="w-6 h-6 text-[#7c3aed]" />;
      case "pptx": return <Presentation className="w-6 h-6 text-[#06b6d4]" />;
      default: return <FileText className="w-6 h-6" />;
    }
  };

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white">
      <AppNav />
      <div className="pt-32 px-6 pb-20 max-w-7xl mx-auto">
        
        {/* Header */}
        <div className="flex items-center justify-between mb-10">
          <div>
            <h1 className="text-3xl font-bold mb-2">My Library</h1>
            <p className="text-[#8888a0]">Continue your learning sprints</p>
          </div>
          <Link href="/upload">
            <Button className="bg-[#ff6b4a] hover:bg-[#ff8a70] text-[#0a0a12] font-semibold rounded-xl">
              <Plus className="w-4 h-4 mr-2" />
              New Sprint
            </Button>
          </Link>
        </div>

        {/* Content Grid */}
        {loading ? (
          <div className="text-center py-20 text-[#8888a0]">Loading your library...</div>
        ) : content.length === 0 ? (
          <div className="text-center py-20 border border-dashed border-[#2a2a3e] rounded-3xl bg-[#13131f]/50">
            <p className="text-[#8888a0] mb-4">You haven't uploaded any content yet.</p>
            <Link href="/upload">
              <Button variant="outline" className="border-[#2a2a3e] text-white hover:bg-[#2a2a3e]">
                Start your first Sprint
              </Button>
            </Link>
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {content.map((item, i) => (
              <motion.div
                key={item.id}
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.05 }}
                className="group relative bg-[#13131f] border border-[#2a2a3e] hover:border-[#ff6b4a]/50 rounded-2xl p-5 transition-all hover:shadow-xl hover:shadow-[#ff6b4a]/5"
              >
                <div className="flex justify-between items-start mb-4">
                  <div className="p-3 bg-[#0a0a12] rounded-xl border border-[#2a2a3e] group-hover:border-[#ff6b4a]/30 transition-colors">
                    {getIcon(item.source_type)}
                  </div>
                  <span className={`text-xs px-2 py-1 rounded-md font-medium ${
                    item.status === 'completed' ? 'bg-green-500/10 text-green-400' :
                    item.status === 'processing' ? 'bg-yellow-500/10 text-yellow-400' :
                    'bg-red-500/10 text-red-400'
                  }`}>
                    {item.status === "processing"
                      ? item.stage ?? "PROCESSING"
                      : item.status.toUpperCase()}

                  </span>
                </div>

                <h3 className="font-semibold text-lg mb-2 line-clamp-2 min-h-[3.5rem]">
                  {item.title}
                </h3>

                <div className="flex items-center text-xs text-[#8888a0] mb-6">
                  <Clock className="w-3 h-3 mr-1" />
                  {new Date(item.created_at).toLocaleDateString()}
                </div>

                {item.status === 'completed' ? (
                  <Link href={`/sprint?id=${item.id}`} className="block">
                    <Button className="w-full bg-[#1e1e2e] hover:bg-[#ff6b4a] hover:text-[#0a0a12] text-white border border-[#2a2a3e] hover:border-[#ff6b4a] transition-all rounded-xl">
                      <Play className="w-4 h-4 mr-2" />
                      Resume Sprint
                    </Button>
                  </Link>
                ) : (
                  <Button disabled className="w-full bg-[#1e1e2e] text-[#8888a0] border border-[#2a2a3e] rounded-xl opacity-50 cursor-not-allowed">
                    {item.stage ? item.stage.replace("_", " ") : "Processing..."}
                  </Button>
                )}
              </motion.div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}