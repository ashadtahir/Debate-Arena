"use client";

import { motion } from "framer-motion";
import type { Topic, Side, Difficulty } from "@/types";

type PropositionBarProps = {
  topic: Topic;
  side: Side;
  difficulty: Difficulty;
};

const sideLabel = { for: "Defending", against: "Challenging" };
const difficultyLabel = { apprentice: "Apprentice", scholar: "Scholar", master: "Master" };

export default function PropositionBar({ topic, side, difficulty }: PropositionBarProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="glass rounded-2xl px-6 py-5"
    >
      <p className="font-heading text-lg sm:text-xl font-medium text-foreground/80 leading-relaxed">
        &ldquo;{topic.title}&rdquo;
      </p>
      <div className="mt-3 flex items-center gap-3">
        <span className="rounded-full bg-purple-500/15 px-3 py-1 text-xs font-semibold tracking-wide text-purple-300">
          {sideLabel[side]}
        </span>
        <span className="rounded-full bg-white/5 px-3 py-1 text-xs font-medium tracking-wide text-foreground/30">
          {difficultyLabel[difficulty]}
        </span>
      </div>
    </motion.div>
  );
}
