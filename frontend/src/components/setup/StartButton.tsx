"use client";

import { motion } from "framer-motion";
import { Swords } from "lucide-react";

type StartButtonProps = {
  disabled: boolean;
  onClick: () => void;
};

export default function StartButton({ disabled, onClick }: StartButtonProps) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 16 }}
      animate={{ opacity: disabled ? 0.4 : 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="pt-4"
    >
      <button
        onClick={onClick}
        disabled={disabled}
        className="group relative w-full rounded-xl bg-purple-600 px-8 py-4 text-lg font-bold tracking-wide text-white transition-all duration-300 hover:bg-purple-500 hover:scale-[1.01] active:scale-[0.99] disabled:pointer-events-none disabled:cursor-not-allowed ring-2 ring-purple-400/20 hover:ring-purple-400/40"
        style={
          disabled
            ? undefined
            : { animation: "breathe-glow 3s ease-in-out infinite" }
        }
      >
        <span className="inline-flex items-center gap-2.5">
          <Swords className="size-5" />
          Enter the Arena
        </span>
      </button>
    </motion.div>
  );
}
