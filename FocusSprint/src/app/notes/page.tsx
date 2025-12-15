"use client";

import { motion } from "framer-motion";
import { useState } from "react";
import { BookOpen, Plus, Download, Edit, Trash2 } from "lucide-react";
import { AppNav } from "@/components/app-nav";
import { useUser } from "@/lib/user-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

interface Note {
  id: string;
  content: string;
  timestamp: number;
  sprintId: string;
  sprintConcept: string;
  isPersonal: boolean;
}

export default function NotesPage() {
  const { completedSprints } = useUser();
  const [notes, setNotes] = useState<Note[]>(() => {
    // Auto-generate notes from completed sprints
    return completedSprints.map((sprint) => ({
      id: `note-${sprint.id}`,
      content: sprint.summary,
      timestamp: sprint.timestamp,
      sprintId: sprint.id,
      sprintConcept: sprint.concept,
      isPersonal: false,
    }));
  });

  const [newNote, setNewNote] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [selectedSprint, setSelectedSprint] = useState<string | null>(null);

  const handleAddNote = () => {
    if (!newNote.trim() || !selectedSprint) return;

    const sprint = completedSprints.find((s) => s.id === selectedSprint);
    if (!sprint) return;

    const note: Note = {
      id: `note-${Date.now()}`,
      content: newNote,
      timestamp: Date.now(),
      sprintId: sprint.id,
      sprintConcept: sprint.concept,
      isPersonal: true,
    };

    setNotes([...notes, note]);
    setNewNote("");
    setSelectedSprint(null);
  };

  const handleDeleteNote = (id: string) => {
    setNotes(notes.filter((n) => n.id !== id));
  };

  const handleExportPDF = () => {
    const content = notes
      .map((n) => `${n.sprintConcept}\n${new Date(n.timestamp).toLocaleDateString()}\n\n${n.content}\n\n---\n\n`)
      .join("");

    const blob = new Blob([content], { type: "text/plain" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `focusflow-notes-${Date.now()}.txt`;
    a.click();
  };

  return (
    <div className="min-h-screen bg-[#0a0a12] text-white">
      <AppNav />

      <div className="pt-32 pb-20 px-6">
        <div className="max-w-5xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
            className="mb-12"
          >
            <div className="inline-flex items-center gap-2 glass px-4 py-2 rounded-full mb-6">
              <BookOpen className="w-4 h-4 text-[#06b6d4]" />
              <span className="text-sm text-[#8888a0]">Your Learning Archive</span>
            </div>
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-5xl md:text-6xl font-bold mb-4">
                  <span className="gradient-text">Notes & Highlights</span>
                </h1>
                <p className="text-xl text-[#8888a0]">
                  {notes.length} notes • Auto-generated & editable
                </p>
              </div>
              <Button
                onClick={handleExportPDF}
                className="bg-[#7c3aed] hover:bg-[#8b5cf6] px-6"
              >
                <Download className="w-4 h-4 mr-2" />
                Export PDF
              </Button>
            </div>
          </motion.div>

          {/* Add Note Section */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="glass rounded-3xl p-8 mb-8"
          >
            <h3 className="text-xl font-semibold mb-4 flex items-center gap-2">
              <Plus className="w-5 h-5" />
              Add Personal Note
            </h3>

            <div className="space-y-4">
              <div>
                <label className="block text-sm text-[#8888a0] mb-2">
                  Select Sprint Topic
                </label>
                <select
                  value={selectedSprint || ""}
                  onChange={(e) => setSelectedSprint(e.target.value)}
                  className="w-full px-4 py-3 rounded-xl bg-[#1e1e2e] border border-[#2a2a3e] text-white focus:outline-none focus:border-[#7c3aed]"
                >
                  <option value="">Choose a topic...</option>
                  {completedSprints.map((sprint) => (
                    <option key={sprint.id} value={sprint.id}>
                      {sprint.concept}
                    </option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm text-[#8888a0] mb-2">Note</label>
                <textarea
                  value={newNote}
                  onChange={(e) => setNewNote(e.target.value)}
                  placeholder="Add your thoughts, examples, or reminders..."
                  className="w-full px-4 py-3 rounded-xl bg-[#1e1e2e] border border-[#2a2a3e] text-white placeholder:text-[#8888a0] focus:outline-none focus:border-[#7c3aed] resize-none h-24"
                />
              </div>

              <Button
                onClick={handleAddNote}
                disabled={!newNote.trim() || !selectedSprint}
                className="bg-[#7c3aed] hover:bg-[#8b5cf6] disabled:opacity-50"
              >
                Add Note
              </Button>
            </div>
          </motion.div>

          {/* Notes List */}
          <div className="space-y-4">
            {notes.length === 0 ? (
              <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                className="glass rounded-3xl p-12 text-center"
              >
                <BookOpen className="w-20 h-20 text-[#8888a0] mx-auto mb-6" />
                <h2 className="text-2xl font-bold mb-3">No notes yet</h2>
                <p className="text-[#8888a0]">
                  Complete sprints to auto-generate notes, or add your own
                </p>
              </motion.div>
            ) : (
              notes.map((note, index) => (
                <motion.div
                  key={note.id}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  transition={{ duration: 0.3, delay: index * 0.05 }}
                  className="glass rounded-2xl p-6"
                >
                  <div className="flex items-start justify-between mb-4">
                    <div className="flex-1">
                      <div className="flex items-center gap-3 mb-2">
                        <h3 className="text-xl font-semibold">
                          {note.sprintConcept}
                        </h3>
                        {note.isPersonal && (
                          <span className="px-2 py-1 rounded-lg bg-[#7c3aed]/20 text-[#7c3aed] text-xs font-semibold">
                            Personal
                          </span>
                        )}
                      </div>
                      <p className="text-sm text-[#8888a0]">
                        {new Date(note.timestamp).toLocaleDateString("en-US", {
                          month: "long",
                          day: "numeric",
                          year: "numeric",
                        })}
                      </p>
                    </div>
                    <div className="flex gap-2">
                      {note.isPersonal && (
                        <>
                          <button
                            onClick={() => setEditingId(note.id)}
                            className="p-2 rounded-lg hover:bg-[#1e1e2e] transition-colors"
                          >
                            <Edit className="w-4 h-4 text-[#8888a0]" />
                          </button>
                          <button
                            onClick={() => handleDeleteNote(note.id)}
                            className="p-2 rounded-lg hover:bg-[#1e1e2e] transition-colors"
                          >
                            <Trash2 className="w-4 h-4 text-[#ff6b4a]" />
                          </button>
                        </>
                      )}
                    </div>
                  </div>

                  <div className="text-[#8888a0] leading-relaxed whitespace-pre-wrap">
                    {note.content}
                  </div>
                </motion.div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
