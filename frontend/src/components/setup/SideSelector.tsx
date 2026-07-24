"use client";

import { motion } from "framer-motion";
import { Shield, Swords } from "lucide-react";
import type { Side, Topic } from "@/types";

type SideSelectorProps = {
  topic: Topic;
  selected: Side | null;
  onSelect: (side: Side) => void;
};

const sides = [
  {
    id: "for" as Side,
    label: "Defend",
    icon: Shield,
    description: "Defend this belief",
    gradient: "from-purple-500/20 to-purple-500/5",
    border: "border-purple-500/30",
    text: "text-purple-300",
    glow: "shadow-purple-500/15",
  },
  {
    id: "against" as Side,
    label: "Challenge",
    icon: Swords,
    description: "Challenge this belief",
    gradient: "from-cyan-500/20 to-cyan-500/5",
    border: "border-cyan-500/30",
    text: "text-cyan-300",
    glow: "shadow-cyan-500/15",
  },
];

export default function SideSelector({
  topic,
  selected,
  onSelect,
}: SideSelectorProps) {
  return (
    <div>
      <motion.h2
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="mb-2 font-heading text-5xl sm:text-6xl font-bold tracking-tighter leading-none text-foreground"
      >
        Your Stance
      </motion.h2>
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1, duration: 0.4 }}
        className="mb-10 text-xl font-light text-foreground/35"
      >
        Will you defend or challenge this belief?
      </motion.p>

      {/* Topic proclamation */}
      <motion.div
        initial={{ opacity: 0, y: 8 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.15, duration: 0.4 }}
        className="mb-10 rounded-xl border border-white/8 bg-white/3 px-6 py-5 text-center"
      >
        <p className="font-heading text-xl font-medium text-foreground leading-relaxed">
          &ldquo;{topic.title}&rdquo;
        </p>
      </motion.div>

      <div className="grid gap-4 sm:grid-cols-2">
        {sides.map((side, i) => (
          <motion.button
            key={side.id}
            onClick={() => onSelect(side.id)}
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{
              delay: 0.2 + i * 0.1,
              duration: 0.4,
              ease: [0.25, 0.1, 0.25, 1] as const,
            }}
            whileHover={{ y: -4 }}
            whileTap={{ scale: 0.97 }}
            className={`group relative rounded-2xl p-8 text-center transition-all duration-300 ${
              selected === side.id
                ? `glass bg-gradient-to-b ${side.gradient} border ${side.border} shadow-lg ${side.glow}`
                : "glass glass-hover"
            }`}
            aria-pressed={selected === side.id}
          >
            <div
              className={`mb-4 inline-flex size-12 items-center justify-center rounded-xl bg-white/5 transition-colors ${side.text}`}
            >
              <side.icon className="size-5" />
            </div>
            <p className="mb-1 font-heading text-xl font-semibold tracking-wide text-foreground">
              {side.label}
            </p>
            <p className="text-base text-foreground/40">
              {side.description}
            </p>
          </motion.button>
        ))}
      </div>
    </div>
  );
}
