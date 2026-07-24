"use client";

import { motion } from "framer-motion";
import type { Persona } from "@/types";
import { personas } from "@/constants/personas";
import PersonaCard from "./PersonaCard";

type PersonaGridProps = {
  selected: Persona | null;
  onSelect: (persona: Persona) => void;
};

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.4, ease: [0.25, 0.1, 0.25, 1] as const },
  },
};

export default function PersonaGrid({ selected, onSelect }: PersonaGridProps) {
  return (
    <div>
      <motion.h2
        initial={{ opacity: 0, y: 12 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.4 }}
        className="mb-2 font-heading text-5xl sm:text-6xl font-bold tracking-tighter leading-none text-foreground"
      >
        Your Opponent
      </motion.h2>
      <motion.p
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ delay: 0.1, duration: 0.4 }}
        className="mb-10 text-xl font-light text-foreground/35"
      >
        Who will challenge your reasoning?
      </motion.p>

      <motion.div
        variants={container}
        initial="hidden"
        animate="show"
        className="grid gap-4 sm:grid-cols-2"
      >
        {personas.map((persona) => (
          <motion.div
            key={persona.id}
            variants={item}
            animate={
              selected && selected.id !== persona.id
                ? { opacity: 0.35 }
                : { opacity: 1 }
            }
            transition={{ duration: 0.4, ease: "easeInOut" }}
          >
            <PersonaCard
              persona={persona}
              selected={selected?.id === persona.id}
              onSelect={() => onSelect(persona)}
            />
          </motion.div>
        ))}
      </motion.div>
    </div>
  );
}
