"use client";

import { motion } from "framer-motion";
import { AlertTriangle, Lightbulb, Sparkles } from "lucide-react";
import type { Observation } from "@/types";

const config = {
  fallacy: {
    icon: AlertTriangle,
    label: "Logical Fallacy",
    border: "border-amber-500/30",
    bg: "bg-amber-500/10",
    text: "text-amber-300",
    desc: "text-amber-400/60",
  },
  strength: {
    icon: Sparkles,
    label: "Strong Reasoning",
    border: "border-emerald-500/30",
    bg: "bg-emerald-500/10",
    text: "text-emerald-300",
    desc: "text-emerald-400/60",
  },
  suggestion: {
    icon: Lightbulb,
    label: "Coaching Tip",
    border: "border-blue-500/30",
    bg: "bg-blue-500/10",
    text: "text-blue-300",
    desc: "text-blue-400/60",
  },
};

export default function ObservationCard({ observation }: { observation: Observation }) {
  const c = config[observation.type];
  const Icon = c.icon;

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4, ease: [0.25, 0.1, 0.25, 1] }}
      className={`inline-flex items-start gap-3 rounded-xl border ${c.border} ${c.bg} px-5 py-3.5`}
    >
      <Icon className={`mt-0.5 size-4 shrink-0 ${c.text}`} />
      <div>
        <p className={`text-sm font-semibold tracking-wide ${c.text}`}>{observation.title}</p>
        <p className={`mt-0.5 text-sm ${c.desc}`}>{observation.description}</p>
      </div>
    </motion.div>
  );
}
