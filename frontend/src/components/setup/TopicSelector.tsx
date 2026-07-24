"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import type { Topic } from "@/types";
import { topics, categories } from "@/constants/topics";

type TopicSelectorProps = {
  selected: Topic | null;
  onSelect: (topic: Topic) => void;
};

export default function TopicSelector({
  selected,
  onSelect,
}: TopicSelectorProps) {
  const [activeCategory, setActiveCategory] = useState<string | null>(null);

  const filtered = activeCategory
    ? topics.filter((t) => t.category === activeCategory)
    : topics;

  return (
    <div>
      <motion.h2
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="mb-2 font-heading text-5xl sm:text-6xl font-bold tracking-tighter leading-none text-foreground"
      >
        The Proposition
      </motion.h2>
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1, duration: 0.4 }}
        className="mb-10 text-xl font-light text-foreground/35"
      >
        Choose the belief you will defend.
      </motion.p>

      {/* Category filter */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.15, duration: 0.4 }}
        className="mb-6 flex flex-wrap gap-2"
      >
        <button
          onClick={() => setActiveCategory(null)}
          className={`rounded-full px-3.5 py-1.5 text-xs font-medium transition-all duration-200 ${
            activeCategory === null
              ? "bg-purple-500/20 text-purple-300 border border-purple-500/30"
              : "bg-white/5 text-muted-foreground border border-transparent hover:bg-white/10"
          }`}
        >
          All
        </button>
        {categories.map((cat) => (
          <button
            key={cat}
            onClick={() => setActiveCategory(cat)}
            className={`rounded-full px-3.5 py-1.5 text-xs font-medium transition-all duration-200 ${
              activeCategory === cat
                ? "bg-purple-500/20 text-purple-300 border border-purple-500/30"
                : "bg-white/5 text-muted-foreground border border-transparent hover:bg-white/10"
            }`}
          >
            {cat}
          </button>
        ))}
      </motion.div>

      {/* Topic list */}
      <div className="space-y-2">
        {filtered.map((topic) => (
          <motion.button
            key={topic.id}
            onClick={() => onSelect(topic)}
            layout
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.3 }}
            className={`w-full text-left rounded-xl px-5 py-4 transition-all duration-300 ${
              selected?.id === topic.id
                ? "glass border-l-2 border-l-purple-500 border-purple-500/40 shadow-lg shadow-purple-500/10"
                : "glass glass-hover"
            }`}
            aria-pressed={selected?.id === topic.id}
          >
            <div className="flex items-center justify-between gap-4">
              <p
                className={`text-base leading-relaxed font-heading ${
                  selected?.id === topic.id
                    ? "font-semibold text-foreground"
                    : "font-medium text-foreground/70"
                }`}
              >
                {topic.title}
              </p>
              <span className="shrink-0 rounded-full bg-white/5 px-2.5 py-1 text-[11px] font-medium text-foreground/30 uppercase tracking-widest">
                {topic.category}
              </span>
            </div>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
