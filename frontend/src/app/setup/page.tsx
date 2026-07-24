"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import type { Persona, Topic, Side, Difficulty } from "@/types";
import SetupHeader from "@/components/setup/SetupHeader";
import PersonaGrid from "@/components/setup/PersonaGrid";
import TopicSelector from "@/components/setup/TopicSelector";
import SideSelector from "@/components/setup/SideSelector";
import DifficultySelector from "@/components/setup/DifficultySelector";
import StartButton from "@/components/setup/StartButton";

type Step = "persona" | "topic" | "side" | "difficulty";

const steps: Step[] = ["persona", "topic", "side", "difficulty"];

const stepLabels: Record<Step, string> = {
  persona: "Your Opponent",
  topic: "The Proposition",
  side: "Your Stance",
  difficulty: "The Challenge",
};

const stepNumerals: Record<Step, string> = {
  persona: "I",
  topic: "II",
  side: "III",
  difficulty: "IV",
};

export default function SetupPage() {
  const router = useRouter();
  const [step, setStep] = useState<Step>("persona");
  const [persona, setPersona] = useState<Persona | null>(null);
  const [topic, setTopic] = useState<Topic | null>(null);
  const [side, setSide] = useState<Side | null>(null);
  const [difficulty, setDifficulty] = useState<Difficulty | null>(null);

  const currentIndex = steps.indexOf(step);
  const allSelected = persona && topic && side && difficulty;

  const canAdvance = () => {
    if (step === "persona") return !!persona;
    if (step === "topic") return !!topic;
    if (step === "side") return !!side;
    if (step === "difficulty") return !!difficulty;
    return false;
  };

  const advance = () => {
    const next = steps[currentIndex + 1];
    if (next) setStep(next);
  };

  const goBack = () => {
    const prev = steps[currentIndex - 1];
    if (prev) setStep(prev);
  };

  return (
    <div className="relative min-h-screen bg-background">
      {/* Background */}
      <div className="pointer-events-none absolute inset-0" aria-hidden>
        <div className="grid-pattern absolute inset-0" />
        <div className="absolute -top-40 left-1/2 h-[500px] w-[500px] -translate-x-1/2 rounded-full bg-purple-600/15 blur-[120px]" />
        <div className="absolute bottom-0 right-0 h-[300px] w-[300px] rounded-full bg-cyan-500/10 blur-[100px]" />
      </div>

      <div className="relative mx-auto max-w-3xl px-6 py-10">
        {/* Header */}
        <div className="mb-10">
          <SetupHeader />
        </div>

        {/* Step indicator — minimal, chapter-style */}
        <motion.nav
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.15, duration: 0.4 }}
          className="mb-12 flex items-center gap-6"
          aria-label="Setup progress"
        >
          {steps.map((s, i) => (
            <div key={s} className="flex items-center gap-6">
              <button
                onClick={() => {
                  if (i <= currentIndex) setStep(s);
                }}
                disabled={i > currentIndex}
                className={`flex items-baseline gap-2 transition-all duration-300 ${
                  s === step
                    ? "text-foreground"
                    : i < currentIndex
                    ? "text-muted-foreground/50 hover:text-muted-foreground cursor-pointer"
                    : "text-muted-foreground/20 cursor-not-allowed"
                }`}
                aria-current={s === step ? "step" : undefined}
              >
                <span className="font-heading text-sm font-bold tracking-widest uppercase">
                  {stepNumerals[s]}
                </span>
                <span className="text-sm font-medium tracking-wide">
                  {stepLabels[s]}
                </span>
              </button>
              {i < steps.length - 1 && (
                <div
                  className={`h-px w-8 transition-colors duration-300 ${
                    i < currentIndex
                      ? "bg-purple-500/30"
                      : "bg-white/8"
                  }`}
                />
              )}
            </div>
          ))}
        </motion.nav>

        {/* Step content */}
        <AnimatePresence mode="wait">
          <motion.div
            key={step}
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -20 }}
            transition={{ duration: 0.3, ease: [0.25, 0.1, 0.25, 1] as const }}
          >
            {step === "persona" && (
              <PersonaGrid selected={persona} onSelect={setPersona} />
            )}
            {step === "topic" && (
              <TopicSelector selected={topic} onSelect={setTopic} />
            )}
            {step === "side" && topic && (
              <SideSelector topic={topic} selected={side} onSelect={setSide} />
            )}
            {step === "difficulty" && (
              <DifficultySelector
                selected={difficulty}
                onSelect={setDifficulty}
              />
            )}
          </motion.div>
        </AnimatePresence>

        {/* Navigation */}
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.3, duration: 0.4 }}
          className="mt-12 flex items-center gap-4"
        >
          {currentIndex > 0 && (
            <button
              onClick={goBack}
              className="rounded-xl bg-white/5 px-5 py-3 text-base font-medium text-foreground/40 transition-all hover:bg-white/10 hover:text-foreground"
            >
              ←
            </button>
          )}

          {step === "difficulty" ? (
            <div className="flex-1">
              <StartButton
                disabled={!allSelected}
                onClick={() => {
                  localStorage.setItem("debate-setup", JSON.stringify({ persona, topic, side, difficulty }));
                  router.push("/debate");
                }}
              />
            </div>
          ) : (
            <button
              onClick={advance}
              disabled={!canAdvance()}
              className="flex-1 rounded-xl bg-purple-600/80 px-5 py-3 text-base font-semibold text-white transition-all duration-200 hover:bg-purple-500 disabled:pointer-events-none disabled:opacity-30"
            >
              Next Challenge
            </button>
          )}
        </motion.div>

        {/* Dramatic summary */}
        {allSelected && (
          <motion.div
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1, duration: 0.4 }}
            className="mt-8 rounded-xl border border-white/8 bg-white/3 p-6 text-center"
          >
            <p className="font-heading text-lg font-medium text-foreground/70 leading-relaxed">
              <span className="text-lg" role="img" aria-hidden>
                {persona.icon}
              </span>{" "}
              {persona.name} will challenge your belief that{" "}
              <span className="italic text-purple-300">
                &ldquo;{topic.title}&rdquo;
              </span>
            </p>
          </motion.div>
        )}
      </div>
    </div>
  );
}
