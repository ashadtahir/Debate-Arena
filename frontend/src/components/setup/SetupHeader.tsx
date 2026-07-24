"use client";

import { motion } from "framer-motion";
import { ArrowLeft } from "lucide-react";
import { useRouter } from "next/navigation";

export default function SetupHeader() {
  const router = useRouter();

  return (
    <motion.header
      initial={{ opacity: 0, y: -12 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ duration: 0.4 }}
      className="flex items-center gap-4"
    >
      <button
        onClick={() => router.push("/")}
        className="inline-flex size-9 items-center justify-center rounded-xl bg-white/5 text-muted-foreground transition-colors hover:bg-white/10 hover:text-foreground"
        aria-label="Back to home"
      >
        <ArrowLeft className="size-4" />
      </button>
      <h1 className="font-heading text-sm font-semibold tracking-[0.2em] text-foreground/35 uppercase">
        Enter the Arena
      </h1>
    </motion.header>
  );
}
