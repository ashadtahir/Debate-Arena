"use client";

import { motion } from "framer-motion";
import type { Argument, Persona } from "@/types";

type ArgumentCardProps = {
  argument: Argument;
  persona: Persona;
  isUser: boolean;
  stance: "for" | "against";
};

const stanceLabels = {
  for: { user: "Defending", ai: "Challenging" },
  against: { user: "Challenging", ai: "Defending" },
};

export default function ArgumentCard({ argument, persona, isUser, stance }: ArgumentCardProps) {
  const accent = isUser ? "cyan" : "purple";
  const label = isUser ? "YOU" : persona.name.toUpperCase();
  const role = isUser ? stanceLabels[stance].user : stanceLabels[stance].ai;

  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.5, ease: [0.25, 0.1, 0.25, 1] }}
      className="glass rounded-2xl p-6 sm:p-8"
    >
      {/* Speaker label */}
      <div className="mb-4 flex items-center gap-3">
        {isUser ? (
          <div className="flex size-8 items-center justify-center rounded-full bg-cyan-500/15 text-xs font-bold text-cyan-400">
            Y
          </div>
        ) : (
          <div className="flex size-8 items-center justify-center rounded-full bg-purple-500/15 text-sm">
            {persona.icon}
          </div>
        )}
        <div>
          <p className={`font-heading text-sm font-semibold tracking-wide ${accent === "cyan" ? "text-cyan-300" : "text-purple-300"}`}>
            {label}
          </p>
          <p className="text-[11px] tracking-wide text-foreground/30">{isUser ? role : persona.debateTitle}</p>
        </div>
      </div>

      {/* Argument content */}
      <p className="text-base leading-relaxed text-foreground/80">
        {argument.content}
      </p>
    </motion.div>
  );
}
