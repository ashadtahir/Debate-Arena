"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Send } from "lucide-react";
import type { RoundLabel } from "@/types";

type ArgumentComposerProps = {
  roundLabel: RoundLabel;
  onSubmit: (content: string) => void;
  disabled?: boolean;
};

const placeholderMap: Record<RoundLabel, string> = {
  "Opening Arguments": "Make your opening argument...",
  "Rebuttal": "Deliver your rebuttal...",
  "Counter-Rebuttal": "Counter their challenge...",
  "Final Challenge": "Make your final challenge...",
  "Closing Statements": "Deliver your closing statement...",
};

export default function ArgumentComposer({ roundLabel, onSubmit, disabled }: ArgumentComposerProps) {
  const [content, setContent] = useState("");

  const handleSubmit = () => {
    const trimmed = content.trim();
    if (!trimmed || disabled) return;
    onSubmit(trimmed);
    setContent("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  return (
    <motion.div
      initial={{ opacity: 0, y: 12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, delay: 0.2 }}
      className="glass rounded-2xl p-4 sm:p-5"
    >
      <textarea
        value={content}
        onChange={(e) => setContent(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder={placeholderMap[roundLabel]}
        disabled={disabled}
        rows={3}
        className="w-full resize-none bg-transparent text-base leading-relaxed text-foreground/80 placeholder:text-foreground/20 focus:outline-none disabled:opacity-40"
      />
      <div className="mt-3 flex items-center justify-between">
        <p className="text-xs text-foreground/20">
          {content.length > 0 ? `${content.split(/\s+/).filter(Boolean).length} words` : "Shift+Enter for new line"}
        </p>
        <button
          onClick={handleSubmit}
          disabled={!content.trim() || disabled}
          className="inline-flex items-center gap-2 rounded-xl bg-purple-600 px-5 py-2.5 text-sm font-semibold text-white transition-all duration-200 hover:bg-purple-500 disabled:pointer-events-none disabled:opacity-30"
        >
          <Send className="size-3.5" />
          Submit Argument
        </button>
      </div>
    </motion.div>
  );
}
