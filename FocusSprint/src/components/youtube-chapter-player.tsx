"use client";

import { useEffect, useRef, useState } from "react";

type Chapter = {
  index: number;
  title: string;
  start: number;
  end: number;
  summary: string;
};

interface Props {
  videoId: string;
  chapters: Chapter[];
  activeIndex: number;
  onChapterChange: (index: number) => void;
}

declare global {
  interface Window {
    YT: any;
    onYouTubeIframeAPIReady: () => void;
  }
}

export function YouTubeChapterPlayer({
  videoId,
  chapters,
  activeIndex,
  onChapterChange,
}: Props) {
  const playerRef = useRef<any>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (window.YT) {
      createPlayer();
      return;
    }

    const tag = document.createElement("script");
    tag.src = "https://www.youtube.com/iframe_api";
    document.body.appendChild(tag);

    window.onYouTubeIframeAPIReady = createPlayer;
  }, []);

  function createPlayer() {
    if (!containerRef.current) return;

    playerRef.current = new window.YT.Player(containerRef.current, {
      videoId,
      playerVars: {
        modestbranding: 1,
        rel: 0,
      },
    });
  }

  function seekTo(seconds: number, chapterIndex: number) {
    if (!playerRef.current) return;
    playerRef.current.seekTo(seconds, true);
    // Do NOT pause or reload, just continue playback
    if (typeof playerRef.current.playVideo === "function") {
      playerRef.current.playVideo();
    }
    onChapterChange(chapterIndex);
  }

  // Auto-highlight current chapter while video plays
  useEffect(() => {
    const interval = setInterval(() => {
      const player = playerRef.current;
      if (!player || typeof player.getCurrentTime !== "function") return;

      const currentTime = player.getCurrentTime();

      let currentIndex: number | null = null;
      for (const ch of chapters) {
        if (currentTime >= ch.start && currentTime < ch.end) {
          currentIndex = ch.index;
          break;
        }
      }

      if (currentIndex !== null && currentIndex !== activeIndex) {
        onChapterChange(currentIndex);
      }
    }, 500);

    return () => clearInterval(interval);
  }, [chapters]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[2fr_1fr] gap-6">
      {/* VIDEO */}
      <div>
        <div ref={containerRef} className="aspect-video w-full rounded-lg overflow-hidden" />
      </div>

      {/* CHAPTER LIST */}
      <div className="space-y-3 max-h-[70vh] overflow-y-auto">
        {chapters.map((ch) => {
          const isActive = activeIndex === ch.index;
          return (
            <button
              key={ch.index}
              onClick={() => seekTo(ch.start, ch.index)}
              className={`w-full text-left p-3 rounded-lg border transition ${
                isActive
                  ? "border-[#ff6b4a] bg-[#1e1e2e]"
                  : "border-border hover:bg-muted"
              }`}
            >
              <div className="flex items-center justify-between gap-2">
                <div className="text-sm font-semibold">
                  {ch.index + 1}. {ch.title}
                </div>
                {isActive && (
                  <span className="text-[10px] px-2 py-0.5 rounded-full bg-[#ff6b4a]/20 text-[#ff6b4a]">
                    NOW
                  </span>
                )}
              </div>
              <div className="text-xs text-muted-foreground mt-1">
                {formatTime(ch.start)} – {formatTime(ch.end)}
              </div>
              <p className="text-xs mt-2 text-muted-foreground line-clamp-3">
                {ch.summary}
              </p>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function formatTime(seconds: number) {
  const m = Math.floor(seconds / 60);
  const s = Math.floor(seconds % 60);
  return `${m}:${s.toString().padStart(2, "0")}`;
}
