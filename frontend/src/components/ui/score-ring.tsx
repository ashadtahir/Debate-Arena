"use client";

import { motion } from "framer-motion";

type ScoreRingProps = {
  score: number;
  size?: number;
  label?: string;
};

export default function ScoreRing({ score, size = 80, label }: ScoreRingProps) {
  const radius = 30;
  const circumference = 2 * Math.PI * radius;
  const id = `ring-${size}`;

  return (
    <div className="flex flex-col items-center gap-2">
      <div className="relative" style={{ width: size, height: size }}>
        <svg className="size-full -rotate-90" viewBox="0 0 80 80">
          <circle
            cx="40"
            cy="40"
            r={radius}
            fill="none"
            stroke="oklch(1 0 0 / 8%)"
            strokeWidth="6"
          />
          <motion.circle
            cx="40"
            cy="40"
            r={radius}
            fill="none"
            stroke={`url(#${id})`}
            strokeWidth="6"
            strokeLinecap="round"
            strokeDasharray={circumference}
            initial={{ strokeDashoffset: circumference }}
            animate={{ strokeDashoffset: circumference - (score / 100) * circumference * 0.85 }}
            transition={{ duration: 1.2, ease: [0.25, 0.1, 0.25, 1], delay: 0.3 }}
          />
          <defs>
            <linearGradient id={id} x1="0%" y1="0%" x2="100%" y2="100%">
              <stop offset="0%" stopColor="oklch(0.65 0.26 290)" />
              <stop offset="100%" stopColor="oklch(0.72 0.18 195)" />
            </linearGradient>
          </defs>
        </svg>
        <span className="absolute inset-0 flex items-center justify-center font-heading font-bold text-foreground" style={{ fontSize: size * 0.3 }}>
          {score}
        </span>
      </div>
      {label && (
        <p className="text-xs uppercase tracking-widest text-foreground/30">{label}</p>
      )}
    </div>
  );
}
