"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  FileText, Image, Layers, Volume2, 
  ChevronLeft, ChevronRight 
} from "lucide-react";
import { Button } from "@/components/ui/button";
import { ContentDisplayMode, loadPreferences } from "@/lib/user-preferences";

interface ContentDisplayModesProps {
  textContent: string;
  keyConcepts?: string[];
  mode?: ContentDisplayMode;
  onModeChange?: (mode: ContentDisplayMode) => void;
  children?: React.ReactNode;
}

// Mode configurations
const DISPLAY_MODES: { id: ContentDisplayMode; label: string; icon: React.ReactNode }[] = [
  { id: "text", label: "Text", icon: <FileText className="w-4 h-4" /> },
  { id: "visual", label: "Visual", icon: <Image className="w-4 h-4" /> },
  { id: "cards", label: "Cards", icon: <Layers className="w-4 h-4" /> },
  { id: "audio", label: "Audio", icon: <Volume2 className="w-4 h-4" /> },
];

/**
 * Content display with multiple modes for different learning preferences.
 */
export function ContentDisplayModes({
  textContent,
  keyConcepts = [],
  mode: controlledMode,
  onModeChange,
  children,
}: ContentDisplayModesProps) {
  const prefs = loadPreferences();
  const [internalMode, setInternalMode] = useState<ContentDisplayMode>(
    prefs.preferredDisplayMode
  );
  const [cardIndex, setCardIndex] = useState(0);
  const [isSpeaking, setIsSpeaking] = useState(false);
  
  const mode = controlledMode ?? internalMode;
  
  const handleModeChange = (newMode: ContentDisplayMode) => {
    if (onModeChange) {
      onModeChange(newMode);
    } else {
      setInternalMode(newMode);
    }
    
    // Stop speech if switching away from audio
    if (newMode !== "audio" && isSpeaking) {
      window.speechSynthesis?.cancel();
      setIsSpeaking(false);
    }
  };
  
  // Split content into sentences for cards mode
  const sentences = textContent
    .split(/[.!?]+/)
    .map(s => s.trim())
    .filter(s => s.length > 10);
  
  // Text-to-speech for audio mode
  const handleSpeak = () => {
    if (!window.speechSynthesis) return;
    
    if (isSpeaking) {
      window.speechSynthesis.cancel();
      setIsSpeaking(false);
    } else {
      const utterance = new SpeechSynthesisUtterance(textContent);
      utterance.rate = 0.9;
      utterance.onend = () => setIsSpeaking(false);
      window.speechSynthesis.speak(utterance);
      setIsSpeaking(true);
    }
  };
  
  return (
    <div className="space-y-4">
      {/* Mode Switcher */}
      <div className="flex items-center justify-center gap-2 p-1 bg-[#1e1e2e] rounded-xl w-fit mx-auto">
        {DISPLAY_MODES.map((m) => (
          <button
            key={m.id}
            onClick={() => handleModeChange(m.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg transition-all ${
              mode === m.id
                ? "bg-[#ff6b4a] text-[#0a0a12]"
                : "text-[#8888a0] hover:text-white"
            }`}
          >
            {m.icon}
            <span className="text-sm font-medium hidden sm:inline">{m.label}</span>
          </button>
        ))}
      </div>
      
      {/* Content Display */}
      <AnimatePresence mode="wait">
        {/* Text Mode */}
        {mode === "text" && (
          <motion.div
            key="text"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="bg-[#13131f] border border-[#2a2a3e] rounded-2xl p-6"
          >
            <p className="text-[#d4d4d8] leading-relaxed whitespace-pre-wrap text-lg">
              {textContent}
            </p>
          </motion.div>
        )}
        
        {/* Visual Mode */}
        {mode === "visual" && (
          <motion.div
            key="visual"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="bg-[#13131f] border border-[#2a2a3e] rounded-2xl p-6 space-y-6"
          >
            {/* Key points as cards */}
            {keyConcepts.length > 0 ? (
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {keyConcepts.map((concept, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-3 p-4 bg-[#1e1e2e] rounded-xl"
                  >
                    <div className="w-8 h-8 rounded-lg bg-[#ff6b4a]/20 flex items-center justify-center flex-shrink-0">
                      <span className="text-[#ff6b4a] font-bold">{i + 1}</span>
                    </div>
                    <p className="text-white">{concept}</p>
                  </div>
                ))}
              </div>
            ) : (
              // Fallback: split text into visual blocks
              <div className="space-y-4">
                {sentences.slice(0, 4).map((sentence, i) => (
                  <div
                    key={i}
                    className="flex items-start gap-3 p-4 bg-[#1e1e2e] rounded-xl border-l-4 border-[#ff6b4a]"
                  >
                    <p className="text-[#d4d4d8]">{sentence}.</p>
                  </div>
                ))}
              </div>
            )}
          </motion.div>
        )}
        
        {/* Cards Mode */}
        {mode === "cards" && sentences.length > 0 && (
          <motion.div
            key="cards"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-4"
          >
            <div className="bg-[#13131f] border border-[#2a2a3e] rounded-2xl p-8 min-h-[200px] flex items-center justify-center">
              <p className="text-xl text-white text-center leading-relaxed max-w-lg">
                {sentences[cardIndex]}.
              </p>
            </div>
            
            {/* Card Navigation */}
            <div className="flex items-center justify-center gap-4">
              <Button
                onClick={() => setCardIndex(Math.max(0, cardIndex - 1))}
                variant="outline"
                size="icon"
                disabled={cardIndex === 0}
                className="border-[#2a2a3e] hover:bg-[#2a2a3e]"
              >
                <ChevronLeft className="w-4 h-4" />
              </Button>
              
              <span className="text-sm text-[#8888a0]">
                {cardIndex + 1} / {sentences.length}
              </span>
              
              <Button
                onClick={() => setCardIndex(Math.min(sentences.length - 1, cardIndex + 1))}
                variant="outline"
                size="icon"
                disabled={cardIndex === sentences.length - 1}
                className="border-[#2a2a3e] hover:bg-[#2a2a3e]"
              >
                <ChevronRight className="w-4 h-4" />
              </Button>
            </div>
          </motion.div>
        )}
        
        {/* Audio Mode */}
        {mode === "audio" && (
          <motion.div
            key="audio"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="bg-[#13131f] border border-[#2a2a3e] rounded-2xl p-8 text-center"
          >
            <div className="w-20 h-20 mx-auto mb-6 rounded-full bg-[#7c3aed]/20 flex items-center justify-center">
              <Volume2 className={`w-10 h-10 ${isSpeaking ? "text-[#7c3aed] animate-pulse" : "text-[#8888a0]"}`} />
            </div>
            
            <h3 className="text-xl font-semibold text-white mb-2">
              {isSpeaking ? "Reading aloud..." : "Audio Mode"}
            </h3>
            <p className="text-[#8888a0] mb-6">
              {isSpeaking 
                ? "Click below to stop" 
                : "Click below to have this content read to you"
              }
            </p>
            
            <Button
              onClick={handleSpeak}
              className={`${
                isSpeaking 
                  ? "bg-red-500 hover:bg-red-600" 
                  : "bg-[#7c3aed] hover:bg-[#8b5cf6]"
              } text-white px-8`}
            >
              {isSpeaking ? "Stop" : "Start Reading"}
            </Button>
            
            {/* Show text below for reference */}
            <div className="mt-6 p-4 bg-[#1e1e2e] rounded-xl text-left">
              <p className="text-sm text-[#8888a0] leading-relaxed line-clamp-4">
                {textContent}
              </p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      
      {/* Additional content passed as children */}
      {children}
    </div>
  );
}

export default ContentDisplayModes;
