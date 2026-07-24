"use client";

import { motion } from "framer-motion";
import { AlertTriangle } from "lucide-react";

const scores = [
  { label: "Logic", value: 92 },
  { label: "Evidence", value: 84 },
  { label: "Persuasion", value: 86 },
];

const fadeUp = {
  hidden: { opacity: 0, y: 16 },
  show: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: { delay: i * 0.15, duration: 0.5, ease: [0.25, 0.1, 0.25, 1] as const },
  }),
};

function ScoreRing({ score }: { score: number }) {
  const radius = 30;
  const circumference = 2 * Math.PI * radius;
  const filled = (score / 100) * circumference;

  return (
    <div className="relative size-[80px]">
      <svg className="size-full -rotate-90" viewBox="0 0 80 80">
        <circle
          cx="40"
          cy="40"
          r={radius}
          fill="none"
          stroke="oklch(1 0 0 / 8%)"
          strokeWidth="6"
        />
        <circle
          cx="40"
          cy="40"
          r={radius}
          fill="none"
          stroke="url(#ring-gradient)"
          strokeWidth="6"
          strokeLinecap="round"
          strokeDasharray={circumference}
          strokeDashoffset={circumference}
          style={{ animation: "ring-fill 1.2s ease-out 0.6s forwards" }}
        />
        <defs>
          <linearGradient id="ring-gradient" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="oklch(0.65 0.26 290)" />
            <stop offset="100%" stopColor="oklch(0.72 0.18 195)" />
          </linearGradient>
        </defs>
      </svg>
      <span className="absolute inset-0 flex items-center justify-center text-2xl font-heading font-bold text-foreground">
        {score}
      </span>
    </div>
  );
}

export default function DebatePreview() {
  return (
    <motion.section
      initial={{ opacity: 0, y: 32 }}
      whileInView={{ opacity: 1, y: 0 }}
      viewport={{ once: true, margin: "-80px" }}
      transition={{ duration: 0.7, ease: [0.25, 0.1, 0.25, 1] as const }}
      className="mx-auto w-full max-w-3xl px-6"
    >
      <div
        className="rounded-3xl p-[1px] bg-gradient-to-br from-purple-500/20 via-transparent to-cyan-500/20"
        style={{ animation: "score-glow 4s ease-in-out infinite" }}
      >
        <div className="glass rounded-3xl p-8 sm:p-10">
          {/* Header */}
          <div className="flex items-center gap-3 border-b border-white/8 pb-6 mb-6">
            <div className="flex size-10 items-center justify-center rounded-full bg-purple-500/15 text-lg">
              🎭
            </div>
            <div>
              <p className="text-xs uppercase tracking-widest text-foreground/30">
                AI Persona
              </p>
              <p className="text-sm font-semibold tracking-wide text-foreground">Socrates</p>
            </div>
          </div>

          {/* Messages */}
          <div className="space-y-5 mb-8">
            <motion.div
              custom={0}
              variants={fadeUp}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true }}
              className="flex gap-3"
            >
              <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-cyan-500/15 text-xs font-bold text-cyan-400">
                Y
              </div>
              <div className="rounded-2xl rounded-tl-sm bg-white/5 px-4 py-3 text-base text-foreground leading-relaxed">
                AI will replace software engineers.
              </div>
            </motion.div>

            <motion.div
              custom={1}
              variants={fadeUp}
              initial="hidden"
              whileInView="show"
              viewport={{ once: true }}
              className="flex gap-3"
            >
              <div className="flex size-8 shrink-0 items-center justify-center rounded-full bg-purple-500/15 text-xs">
                🎭
              </div>
              <div className="rounded-2xl rounded-tl-sm bg-purple-500/10 px-4 py-3 text-base text-foreground leading-relaxed">
                What assumptions lead you to that conclusion?
              </div>
            </motion.div>
          </div>

          {/* Fallacy badge */}
          <motion.div
            custom={2}
            variants={fadeUp}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            className="mb-8 inline-flex items-center gap-2.5 rounded-xl border border-amber-500/30 bg-amber-500/10 px-4 py-2.5"
            style={{ animation: "pulse-border 3s ease-in-out infinite" }}
          >
            <AlertTriangle className="size-4 text-amber-400" />
            <div>
              <p className="text-xs font-medium tracking-wide text-amber-300">Logical Fallacy</p>
              <p className="text-xs text-amber-400/60">Hasty Generalization</p>
            </div>
          </motion.div>

          {/* Scores */}
          <motion.div
            custom={3}
            variants={fadeUp}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true }}
            className="flex flex-col sm:flex-row items-start sm:items-center gap-8"
          >
            <div className="flex flex-col items-center gap-2">
              <ScoreRing score={87} />
              <p className="text-xs uppercase tracking-widest text-foreground/30">
                Overall Score
              </p>
            </div>

            <div className="flex-1 space-y-3 w-full">
              {scores.map((s) => (
                <div key={s.label}>
                  <div className="flex justify-between text-xs mb-1.5">
                    <span className="text-foreground/40">{s.label}</span>
                    <span className="font-medium text-foreground">{s.value}</span>
                  </div>
                  <div className="h-1.5 rounded-full bg-white/5 overflow-hidden">
                    <motion.div
                      initial={{ width: 0 }}
                      whileInView={{ width: `${s.value}%` }}
                      viewport={{ once: true }}
                      transition={{
                        duration: 1,
                        delay: 0.8,
                        ease: [0.25, 0.1, 0.25, 1] as const,
                      }}
                      className="h-full rounded-full bg-gradient-to-r from-purple-500 to-cyan-400"
                    />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </motion.section>
  );
}
