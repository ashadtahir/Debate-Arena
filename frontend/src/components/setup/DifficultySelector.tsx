"use client";

import { motion } from "framer-motion";
import type { Difficulty } from "@/types";
import { difficulties } from "@/constants/difficulty";

type DifficultySelectorProps = {
  selected: Difficulty | null;
  onSelect: (difficulty: Difficulty) => void;
};

const intensityMap: Record<Difficulty, string> = {
  apprentice: "",
  scholar: "shadow-purple-500/10 shadow-lg",
  master: "shadow-purple-500/20 shadow-xl border-purple-500/30",
};

export default function DifficultySelector({
  selected,
  onSelect,
}: DifficultySelectorProps) {
  return (
    <div>
      <motion.h2
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="mb-2 font-heading text-5xl sm:text-6xl font-bold tracking-tighter leading-none text-foreground"
      >
        The Challenge
      </motion.h2>
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1, duration: 0.4 }}
        className="mb-10 text-xl font-light text-foreground/35"
      >
        How relentless should your opponent be?
      </motion.p>

      <div className="grid gap-4 sm:grid-cols-3">
        {difficulties.map((diff, i) => (
          <motion.button
            key={diff.id}
            onClick={() => onSelect(diff.id)}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              delay: 0.15 + i * 0.08,
              duration: 0.4,
              ease: [0.25, 0.1, 0.25, 1] as const,
            }}
            whileHover={{ y: -3 }}
            whileTap={{ scale: 0.97 }}
            className={`group rounded-2xl p-6 text-left transition-all duration-300 ${
              selected === diff.id
                ? `glass border-purple-500/40 ${intensityMap[diff.id]}`
                : `glass glass-hover ${diff.id !== "apprentice" ? intensityMap[diff.id] : ""}`
            }`}
            aria-pressed={selected === diff.id}
          >
            <span className="mb-3 block text-2xl" role="img" aria-hidden>
              {diff.icon}
            </span>
            <p className="mb-1 font-heading text-base font-semibold tracking-wide text-foreground">
              {diff.label}
            </p>
            <p className="text-sm text-foreground/35">{diff.description}</p>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
