"use client";

import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import { useRouter } from "next/navigation";
import type { Persona } from "@/types";

type DebateHeaderProps = {
  persona: Persona;
  currentRound: number;
  totalRounds: number;
};

export default function DebateHeader({ persona, currentRound, totalRounds }: DebateHeaderProps) {
  const router = useRouter();

  return (
    <motion.header
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="flex items-center justify-between"
    >
      <div className="flex items-center gap-4">
        <button
          onClick={() => router.push("/")}
          className="inline-flex size-9 items-center justify-center rounded-xl bg-white/5 text-muted-foreground transition-colors hover:bg-white/10 hover:text-foreground"
          aria-label="Back to home"
        >
          <ArrowLeft className="size-4" />
        </button>
        <div>
          <h1 className="font-heading text-sm font-semibold tracking-[0.2em] text-foreground/35 uppercase">
            DebateArena
          </h1>
          <p className="text-xs text-foreground/20">
            Round {currentRound} of {totalRounds}
          </p>
        </div>
      </div>

      <div className="flex items-center gap-2.5">
        <div className="flex size-8 items-center justify-center rounded-full bg-purple-500/15 text-sm">
          {persona.icon}
        </div>
        <div className="text-right">
          <p className="font-heading text-sm font-semibold tracking-wide text-foreground">
            {persona.name}
          </p>
          <p className="text-[11px] text-foreground/30">{persona.debateTitle}</p>
        </div>
      </div>
    </motion.header>
  );
}
