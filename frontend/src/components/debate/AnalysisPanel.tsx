"use client";

import { motion, AnimatePresence } from "framer-motion";
import { Lightbulb, ShieldAlert, Sparkles, Target } from "lucide-react";
import type { Score, Observation } from "@/types";

type AnalysisPanelProps = {
  score: Score;
  observations: Observation[];
  currentRound: number;
  totalRounds: number;
  personaName: string;
};

export default function AnalysisPanel({ score, observations, currentRound, totalRounds, personaName }: AnalysisPanelProps) {
  const latestObservation = observations.length > 0 ? observations[observations.length - 1] : null;
  const latestStrength = [...observations].reverse().find((o) => o.type === "strength");
  const latestFallacy = [...observations].reverse().find((o) => o.type === "fallacy");

  return (
    <div className="glass rounded-2xl p-6 space-y-5">
      {/* Section label */}
      <p className="text-xs uppercase tracking-widest text-foreground/25">Debate Insights</p>

      {/* Latest Insight — primary content */}
      <AnimatePresence mode="wait">
        {latestObservation ? (
          <motion.div
            key={latestObservation.id}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -4 }}
            transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
            className={`rounded-xl border px-4 py-3.5 ${
              latestObservation.type === "fallacy"
                ? "border-amber-500/25 bg-amber-500/8"
                : latestObservation.type === "strength"
                ? "border-emerald-500/25 bg-emerald-500/8"
                : "border-blue-500/25 bg-blue-500/8"
            }`}
          >
            <div className="flex items-center gap-2 mb-1.5">
              {latestObservation.type === "fallacy" ? (
                <ShieldAlert className="size-3.5 text-amber-400" />
              ) : latestObservation.type === "strength" ? (
                <Sparkles className="size-3.5 text-emerald-400" />
              ) : (
                <Lightbulb className="size-3.5 text-blue-400" />
              )}
              <span className={`text-xs font-semibold tracking-wide ${
                latestObservation.type === "fallacy"
                  ? "text-amber-300"
                  : latestObservation.type === "strength"
                  ? "text-emerald-300"
                  : "text-blue-300"
              }`}>
                {latestObservation.type === "fallacy" ? "Fallacy Detected" :
                 latestObservation.type === "strength" ? "Strong Reasoning" : "Coaching Tip"}
              </span>
            </div>
            <p className="text-sm font-medium text-foreground/80">{latestObservation.title}</p>
            <p className="mt-1 text-xs leading-relaxed text-foreground/40">{latestObservation.description}</p>
          </motion.div>
        ) : (
          <motion.div
            key="empty"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="rounded-xl border border-white/8 bg-white/3 px-4 py-5 text-center"
          >
            <Target className="mx-auto mb-2 size-5 text-foreground/15" />
            <p className="text-xs text-foreground/25">
              Submit your argument. {personaName}&apos;s response and coaching insights will appear here.
            </p>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Current Strength / Needs Improvement — two-column */}
      <div className="grid grid-cols-2 gap-3">
        <div className="rounded-xl bg-emerald-500/5 border border-emerald-500/15 px-3.5 py-3">
          <p className="text-[10px] uppercase tracking-widest text-emerald-400/50 mb-1.5">Strength</p>
          {latestStrength ? (
            <p className="text-xs font-medium text-emerald-300/80 leading-relaxed">{latestStrength.title}</p>
          ) : (
            <p className="text-xs text-foreground/20">—</p>
          )}
        </div>
        <div className="rounded-xl bg-amber-500/5 border border-amber-500/15 px-3.5 py-3">
          <p className="text-[10px] uppercase tracking-widest text-amber-400/50 mb-1.5">Improve</p>
          {latestFallacy ? (
            <p className="text-xs font-medium text-amber-300/80 leading-relaxed">{latestFallacy.title}</p>
          ) : (
            <p className="text-xs text-foreground/20">—</p>
          )}
        </div>
      </div>

      {/* Reasoning Score — compact */}
      <div className="border-t border-white/8 pt-4">
        <div className="flex items-baseline justify-between mb-3">
          <p className="text-xs uppercase tracking-widest text-foreground/25">Reasoning Score</p>
          <motion.span
            key={score.overall}
            initial={{ opacity: 0, y: -4 }}
            animate={{ opacity: 1, y: 0 }}
            className="font-heading text-2xl font-bold text-foreground"
          >
            {score.overall}
          </motion.span>
        </div>
        <div className="space-y-2">
          {[
            { key: "logic" as const, label: "Logic" },
            { key: "evidence" as const, label: "Evidence" },
            { key: "persuasion" as const, label: "Persuasion" },
          ].map((d) => (
            <div key={d.key} className="flex items-center gap-3">
              <span className="text-[11px] text-foreground/30 w-16">{d.label}</span>
              <div className="flex-1 h-1 rounded-full bg-white/5 overflow-hidden">
                <motion.div
                  key={score[d.key]}
                  initial={{ width: 0 }}
                  animate={{ width: `${score[d.key]}%` }}
                  transition={{ duration: 0.6, ease: [0.25, 0.1, 0.25, 1] }}
                  className="h-full rounded-full bg-gradient-to-r from-purple-500 to-cyan-400"
                />
              </div>
              <span className="text-[11px] font-medium text-foreground/40 w-5 text-right">{score[d.key]}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Round progress */}
      <div className="border-t border-white/8 pt-4 flex items-center justify-between">
        <span className="text-[11px] text-foreground/25">Round {currentRound} of {totalRounds}</span>
        <div className="flex gap-1">
          {Array.from({ length: totalRounds }, (_, i) => (
            <div
              key={i}
              className={`size-1.5 rounded-full transition-all duration-300 ${
                i < currentRound - 1
                  ? "bg-purple-500"
                  : i === currentRound - 1
                  ? "bg-purple-400"
                  : "bg-white/10"
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
}
