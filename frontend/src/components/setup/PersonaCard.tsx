"use client";

import { motion } from "framer-motion";
import type { Persona } from "@/types";

type PersonaCardProps = {
  persona: Persona;
  selected: boolean;
  onSelect: () => void;
};

export default function PersonaCard({
  persona,
  selected,
  onSelect,
}: PersonaCardProps) {
  return (
    <motion.button
      onClick={onSelect}
      whileHover={selected ? undefined : { y: -4 }}
      whileTap={{ scale: 0.97 }}
      animate={
        selected
          ? { scale: 1.02 }
          : { scale: 1 }
      }
      transition={{ type: "spring", stiffness: 300, damping: 25 }}
      className={`group relative w-full text-left rounded-2xl p-6 transition-all duration-500 ${
        selected
          ? "glass border-purple-500/40 shadow-xl shadow-purple-500/15"
          : "glass glass-hover"
      }`}
      aria-pressed={selected}
    >
      {selected && (
        <motion.div
          layoutId="persona-glow"
          className="absolute inset-0 rounded-2xl border border-purple-500/30 bg-purple-500/5"
          transition={{ type: "spring", stiffness: 300, damping: 30 }}
        />
      )}

      <div className="relative">
        {/* Quote — primary element */}
        <p className="mb-5 text-lg sm:text-xl font-medium italic leading-relaxed text-foreground/85 font-heading">
          &ldquo;{persona.quote}&rdquo;
        </p>

        {/* Name + title */}
        <div className="mb-3 flex items-center gap-2.5">
          <span className="text-xl" role="img" aria-hidden>
            {persona.icon}
          </span>
          <div>
            <p className="font-heading text-base font-semibold tracking-wide text-foreground">
              {persona.name}
            </p>
            <p className="text-xs text-foreground/30">
              {persona.title}
            </p>
          </div>
        </div>

        {/* Strategy — tertiary */}
        <div className="flex items-center gap-2">
          <span
            className={`inline-block size-1.5 rounded-full ${
              persona.accent === "purple" ? "bg-purple-400" : "bg-cyan-400"
            }`}
          />
          <span className="text-xs tracking-wide text-foreground/25">
            {persona.strategy}
          </span>
        </div>
      </div>
    </motion.button>
  );
}
