"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import type {
  SetupState,
  DebateState,
  Argument,
  Observation,
  RoundLabel,
  Score,
  Side,
} from "@/types";
import { personas } from "@/constants/personas";
import DebateHeader from "@/components/debate/DebateHeader";
import PropositionBar from "@/components/debate/PropositionBar";
import ArgumentCard from "@/components/debate/ArgumentCard";
import ObservationCard from "@/components/debate/ObservationCard";
import ArgumentComposer from "@/components/debate/ArgumentComposer";
import AnalysisPanel from "@/components/debate/AnalysisPanel";

const roundLabels: RoundLabel[] = [
  "Opening Arguments",
  "Rebuttal",
  "Counter-Rebuttal",
  "Final Challenge",
  "Closing Statements",
];

const totalRounds = roundLabels.length;

// Mock AI responses per persona, per round pattern
const mockResponses: Record<string, string[]> = {
  socrates: [
    "What assumptions lead you to that conclusion? Have you considered that your premise might be built on an unexamined foundation?",
    "You say this with conviction, but can you define your terms precisely? What exactly do you mean by 'replace' — and by what measure do you judge 'most'?",
    "Interesting. But if we accept your definition, doesn't that contradict what you claimed in your opening? Let us examine this tension.",
    "I notice you've shifted your argument. That is not necessarily weakness — but it does suggest your original position was not as solid as you believed. What have you learned?",
    "Your closing is more measured than your opening. Perhaps this exchange has sharpened your thinking. But I ask you: do you still believe what you believed when you entered this arena?",
  ],
  prosecutor: [
    "Your claim lacks evidentiary support. 'Many domains' is not a dataset — it is a handwave. Present your evidence or withdraw the assertion.",
    "The data does not support your conclusion. Let me show you where your reasoning breaks down: you've confused correlation with causation.",
    "You've introduced new evidence, but it contradicts your opening statement. Which position do you actually hold?",
    "Your argument has a structural weakness: you're relying on authority rather than evidence. Who says this, and why should we believe them?",
    "In closing, I note that you've failed to address three of my five challenges. The record will reflect this.",
  ],
  philosopher: [
    "Let us step back. You are arguing about a symptom, but what about the underlying principle? What is the nature of the work you claim AI will replace?",
    "Your argument assumes that 'replacement' means something simple. But does a tool that augments human capability 'replace' the human? Or does it transform the nature of the work itself?",
    "You are thinking in binaries — replace or not replace. But reality is a spectrum. Where on that spectrum does your argument actually sit?",
    "Consider this: every technological revolution has been preceded by the same fear. What makes this moment fundamentally different from the printing press, the steam engine, or the computer?",
    "You've moved from prediction to philosophy in this debate. That is a sign of depth, not retreat. Your closing reflects a more nuanced understanding than your opening.",
  ],
  "devils-advocate": [
    "Oh, so AI will replace white-collar jobs? That's adorable. Have you considered that white-collar workers will simply adapt, like every other group threatened by technology?",
    "I'll take the opposite position just to show how weak yours is: AI will create MORE white-collar jobs than it destroys. Prove me wrong.",
    "You're defending a position that even AI researchers don't fully agree on. Doesn't that give you pause?",
    "I notice you're getting frustrated. Good. Debate should be uncomfortable. Your discomfort means you're actually thinking.",
    "I've been arguing against you this entire time, and honestly? Your closing was the strongest thing you said. You actually convinced me of something — that you can think under pressure.",
  ],
};

// Mock observations per round
const mockObservations: Observation[][] = [
  [
    {
      id: "obs-1-1",
      round: 1,
      type: "strength",
      title: "Clear Opening Position",
      description: "You stated your claim directly. A strong start establishes credibility.",
    },
  ],
  [
    {
      id: "obs-2-1",
      round: 2,
      type: "fallacy",
      title: "Hasty Generalization",
      description: "Your claim generalizes without specifying which domains or providing evidence. Anchor your argument in specifics.",
    },
    {
      id: "obs-2-2",
      round: 2,
      type: "suggestion",
      title: "Consider Counter-Evidence",
      description: "Addressing the strongest objection to your position — not the weakest — strengthens your credibility.",
    },
  ],
  [
    {
      id: "obs-3-1",
      round: 3,
      type: "strength",
      title: "Responsive Reasoning",
      description: "You engaged directly with your opponent's challenge rather than deflecting. This builds intellectual honesty.",
    },
  ],
  [
    {
      id: "obs-4-1",
      round: 4,
      type: "fallacy",
      title: "Appeal to Authority",
      description: "You cited an expert without explaining why their authority is relevant to this specific claim. Explain the connection.",
    },
    {
      id: "obs-4-2",
      round: 4,
      type: "suggestion",
      title: "Tighten Your Argument",
      description: "Your last two points were strong but scattered. Pick one thread and develop it fully.",
    },
  ],
  [
    {
      id: "obs-5-1",
      round: 5,
      type: "strength",
      title: "Strong Closing",
      description: "Your closing synthesized your earlier points rather than repeating them. This shows growth through the debate.",
    },
  ],
];

// Score calculation (mock)
function calculateScore(userArgs: string[], observations: Observation[]): Score {
  const wordCount = userArgs.reduce((sum, a) => sum + a.split(/\s+/).length, 0);
  const fallacyCount = observations.filter((o) => o.type === "fallacy").length;
  const strengthCount = observations.filter((o) => o.type === "strength").length;

  const base = Math.min(60, 30 + wordCount * 0.3);
  const bonus = strengthCount * 8;
  const penalty = fallacyCount * 12;
  const overall = Math.round(Math.max(20, Math.min(98, base + bonus - penalty)));

  return {
    overall,
    logic: Math.round(Math.max(20, Math.min(98, overall + (Math.random() * 10 - 5)))),
    evidence: Math.round(Math.max(20, Math.min(98, overall + (Math.random() * 12 - 6)))),
    persuasion: Math.round(Math.max(20, Math.min(98, overall + (Math.random() * 10 - 5)))),
  };
}

function generateId() {
  return Math.random().toString(36).slice(2, 10);
}

export default function DebatePage() {
  const [setup, setSetup] = useState<SetupState | null>(null);
  const [rounds, setRounds] = useState<DebateState["rounds"]>(() =>
    roundLabels.map((label, i) => ({
      number: i + 1,
      label,
      arguments: [],
      observations: [],
    }))
  );
  const [currentRound, setCurrentRound] = useState(0);
  const [score, setScore] = useState<Score>({ overall: 0, logic: 0, evidence: 0, persuasion: 0 });
  const [status, setStatus] = useState<"intro" | "active" | "completed">("intro");
  const [isAiThinking, setIsAiThinking] = useState(false);
  const timelineRef = useRef<HTMLDivElement>(null);

  // Load setup from localStorage
  useEffect(() => {
    const raw = localStorage.getItem("debate-setup");
    if (raw) {
      try {
        const parsed = JSON.parse(raw) as SetupState;
        if (parsed.persona && parsed.topic && parsed.side && parsed.difficulty) {
          setSetup(parsed);
        }
      } catch {}
    }
  }, []);

  const persona = setup?.persona ?? personas[0];
  const side: Side = setup?.side ?? "for";
  const topic = setup?.topic ?? { id: "mock", title: "AI will replace most white-collar jobs", category: "Technology" };

  // Who goes first: if defending, user opens; if challenging, AI opens
  const userGoesFirst = side === "for";

  const allRoundArgs = rounds.flatMap((r) => r.arguments);
  const allObservations = rounds.flatMap((r) => r.observations);
  const userArgs = allRoundArgs.filter((a) => a.speaker === "user").map((a) => a.content);
  const currentRoundData = rounds[currentRound];
  const isLastRound = currentRound >= totalRounds - 1;

  const handleStart = () => {
    setStatus("active");
  };

  const handleUserSubmit = (content: string) => {
    if (!currentRoundData) return;

    const userArg: Argument = {
      id: generateId(),
      round: currentRound + 1,
      speaker: "user",
      content,
    };

    // Add user argument
    const updatedRounds = [...rounds];
    updatedRounds[currentRound] = {
      ...updatedRounds[currentRound],
      arguments: [...updatedRounds[currentRound].arguments, userArg],
    };
    setRounds(updatedRounds);

    // AI thinking delay
    setIsAiThinking(true);
    setTimeout(() => {
      const aiArg: Argument = {
        id: generateId(),
        round: currentRound + 1,
        speaker: "ai",
        content: mockResponses[persona.id]?.[currentRound] ?? "That is an interesting position. Let me challenge your reasoning.",
      };

      const withAi = [...updatedRounds];
      withAi[currentRound] = {
        ...withAi[currentRound],
        arguments: [...withAi[currentRound].arguments, aiArg],
      };

      // Add observations for this round
      const roundObs = mockObservations[currentRound] ?? [];
      withAi[currentRound] = {
        ...withAi[currentRound],
        observations: roundObs,
      };

      setRounds(withAi);
      setIsAiThinking(false);

      // Update score
      const newUserArgs = withAi.flatMap((r) => r.arguments).filter((a) => a.speaker === "user").map((a) => a.content);
      const newObs = withAi.flatMap((r) => r.observations);
      setScore(calculateScore(newUserArgs, newObs));

      // Advance to next round after a brief pause
      setTimeout(() => {
        if (currentRound < totalRounds - 1) {
          setCurrentRound(currentRound + 1);
        } else {
          setStatus("completed");
        }
      }, 800);
    }, 1200 + Math.random() * 800);
  };

  // Scroll to bottom when new content appears
  useEffect(() => {
    if (timelineRef.current) {
      timelineRef.current.scrollTo({ top: timelineRef.current.scrollHeight, behavior: "smooth" });
    }
  }, [rounds, isAiThinking]);

  // Intro screen
  if (status === "intro") {
    return (
      <div className="relative min-h-screen bg-background">
        <div className="pointer-events-none absolute inset-0" aria-hidden>
          <div className="grid-pattern absolute inset-0" />
          <div className="absolute -top-40 left-1/2 h-[500px] w-[500px] -translate-x-1/2 rounded-full bg-purple-600/15 blur-[120px]" />
        </div>
        <div className="relative flex min-h-screen flex-col items-center justify-center px-6 text-center">
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.6 }}
            className="max-w-lg"
          >
            <div className="mb-6 inline-flex size-16 items-center justify-center rounded-full bg-purple-500/15 text-3xl">
              {persona.icon}
            </div>
            <h1 className="font-heading text-4xl font-bold tracking-tighter text-foreground sm:text-5xl">
              {persona.name}
            </h1>
            <p className="mt-2 text-lg font-light text-foreground/40">
              {persona.debateTitle}
            </p>
            <p className="mt-1 text-sm text-foreground/25">
              {persona.debateSubtitle}
            </p>
            <p className="mt-6 text-base leading-relaxed text-foreground/50">
              &ldquo;{topic.title}&rdquo;
            </p>
            <p className="mt-2 text-sm text-foreground/30">
              You are {side === "for" ? "defending" : "challenging"} this position
            </p>

            <motion.button
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.4, duration: 0.5 }}
              onClick={handleStart}
              className="mt-10 rounded-xl bg-purple-600 px-10 py-4 text-lg font-bold tracking-wide text-white transition-all duration-300 hover:bg-purple-500 hover:scale-[1.02] active:scale-[0.98] ring-2 ring-purple-400/20 hover:ring-purple-400/40"
              style={{ animation: "breathe-glow 3s ease-in-out infinite" }}
            >
              Begin the Debate
            </motion.button>
          </motion.div>
        </div>
      </div>
    );
  }

  // Completed screen
  if (status === "completed") {
    return (
      <div className="relative min-h-screen bg-background">
        <div className="pointer-events-none absolute inset-0" aria-hidden>
          <div className="grid-pattern absolute inset-0" />
          <div className="absolute -top-40 left-1/2 h-[500px] w-[500px] -translate-x-1/2 rounded-full bg-purple-600/15 blur-[120px]" />
        </div>
        <div className="relative mx-auto max-w-2xl px-6 py-16 text-center">
          <motion.div
            initial={{ opacity: 0, y: 24 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <p className="text-xs uppercase tracking-widest text-foreground/25 mb-4">Debate Complete</p>
            <h1 className="font-heading text-5xl font-bold tracking-tighter text-foreground sm:text-6xl">
              {score.overall}
            </h1>
            <p className="mt-2 text-lg font-light text-foreground/40">Reasoning Score</p>

            <div className="mt-10 glass rounded-2xl p-8 text-left">
              <div className="space-y-4">
                {[
                  { label: "Logic", value: score.logic },
                  { label: "Evidence", value: score.evidence },
                  { label: "Persuasion", value: score.persuasion },
                ].map((d) => (
                  <div key={d.label}>
                    <div className="flex justify-between text-sm mb-2">
                      <span className="text-foreground/50">{d.label}</span>
                      <span className="font-semibold text-foreground">{d.value}</span>
                    </div>
                    <div className="h-2 rounded-full bg-white/5 overflow-hidden">
                      <motion.div
                        initial={{ width: 0 }}
                        animate={{ width: `${d.value}%` }}
                        transition={{ duration: 1, delay: 0.3, ease: [0.25, 0.1, 0.25, 1] }}
                        className="h-full rounded-full bg-gradient-to-r from-purple-500 to-cyan-400"
                      />
                    </div>
                  </div>
                ))}
              </div>

              <div className="mt-8 border-t border-white/8 pt-6">
                <p className="text-xs uppercase tracking-widest text-foreground/25 mb-3">Observations</p>
                <div className="flex gap-6">
                  <div>
                    <p className="text-2xl font-heading font-bold text-emerald-400">
                      {allObservations.filter((o) => o.type === "strength").length}
                    </p>
                    <p className="text-xs text-foreground/30">Strengths</p>
                  </div>
                  <div>
                    <p className="text-2xl font-heading font-bold text-amber-400">
                      {allObservations.filter((o) => o.type === "fallacy").length}
                    </p>
                    <p className="text-xs text-foreground/30">Fallacies</p>
                  </div>
                  <div>
                    <p className="text-2xl font-heading font-bold text-blue-400">
                      {allObservations.filter((o) => o.type === "suggestion").length}
                    </p>
                    <p className="text-xs text-foreground/30">Tips</p>
                  </div>
                </div>
              </div>
            </div>

            <div className="mt-8 flex justify-center gap-4">
              <button
                onClick={() => window.location.reload()}
                className="rounded-xl bg-purple-600 px-8 py-3 text-base font-semibold text-white transition-all hover:bg-purple-500"
              >
                Debate Again
              </button>
              <button
                onClick={() => window.location.href = "/"}
                className="rounded-xl bg-white/5 px-8 py-3 text-base font-medium text-foreground/50 transition-all hover:bg-white/10 hover:text-foreground"
              >
                New Match
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    );
  }

  // Active debate
  return (
    <div className="relative min-h-screen bg-background">
      {/* Background */}
      <div className="pointer-events-none absolute inset-0" aria-hidden>
        <div className="grid-pattern absolute inset-0" />
        <div className="absolute -top-40 left-1/2 h-[500px] w-[500px] -translate-x-1/2 rounded-full bg-purple-600/15 blur-[120px]" />
        <div className="absolute bottom-0 right-0 h-[300px] w-[300px] rounded-full bg-cyan-500/10 blur-[100px]" />
      </div>

      <div className="relative mx-auto max-w-7xl px-4 sm:px-6 py-6 sm:py-8">
        {/* Header */}
        <div className="mb-6">
          <DebateHeader persona={persona} currentRound={currentRound + 1} totalRounds={totalRounds} />
        </div>

        {/* Main layout: debate stage + analysis panel */}
        <div className="flex flex-col lg:flex-row gap-6">
          {/* Debate stage */}
          <div className="flex-1 min-w-0 space-y-6">
            {/* Proposition bar */}
            <PropositionBar topic={topic} side={side} difficulty={setup?.difficulty ?? "scholar"} />

            {/* Round progress dots */}
            <div className="flex items-center gap-2">
              {roundLabels.map((_, i) => (
                <div key={i} className="flex items-center gap-2">
                  <div
                    className={`size-2 rounded-full transition-all duration-300 ${
                      i < currentRound
                        ? "bg-purple-500"
                        : i === currentRound
                        ? "bg-purple-400 scale-125"
                        : "bg-white/10"
                    }`}
                  />
                  {i < roundLabels.length - 1 && (
                    <div className={`h-px w-6 ${i < currentRound ? "bg-purple-500/30" : "bg-white/5"}`} />
                  )}
                </div>
              ))}
            </div>

            {/* Debate timeline */}
            <div ref={timelineRef} className="space-y-10 max-h-[60vh] overflow-y-auto pr-2 scrollbar-thin">
              <AnimatePresence mode="popLayout">
                {rounds.slice(0, currentRound + 1).map((round) => {
                  const isActive = round.number === currentRound + 1;
                  return (
                    <motion.div
                      key={round.number}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.5, ease: [0.25, 0.1, 0.25, 1] }}
                      className={`relative rounded-2xl transition-all duration-500 ${
                        isActive
                          ? "glass ring-1 ring-purple-500/20 p-6 sm:p-8"
                          : "px-2"
                      }`}
                    >
                      {/* Chapter header */}
                      <div className="mb-5 flex items-center gap-3">
                        <div className={`flex size-7 items-center justify-center rounded-full text-xs font-bold ${
                          isActive
                            ? "bg-purple-500/20 text-purple-300"
                            : "bg-white/5 text-foreground/25"
                        }`}>
                          {round.number}
                        </div>
                        <div>
                          <p className={`text-sm font-semibold tracking-wide ${
                            isActive ? "text-foreground/80" : "text-foreground/35"
                          }`}>
                            {round.label}
                          </p>
                          {!isActive && round.number < currentRound + 1 && (
                            <p className="text-[10px] text-foreground/20">Completed</p>
                          )}
                          {isActive && (
                            <motion.p
                              initial={{ opacity: 0 }}
                              animate={{ opacity: 1 }}
                              transition={{ delay: 0.3 }}
                              className="text-[10px] text-purple-300/50"
                            >
                              {persona.debateTitle}
                            </motion.p>
                          )}
                        </div>
                      </div>

                      {/* Arguments within this chapter */}
                      <div className="space-y-4">
                        {round.arguments.map((arg, i) => (
                          <motion.div
                            key={arg.id}
                            initial={{ opacity: 0, y: 12 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.5, delay: i * 0.15, ease: [0.25, 0.1, 0.25, 1] }}
                          >
                            <ArgumentCard
                              argument={arg}
                              persona={persona}
                              isUser={arg.speaker === "user"}
                              stance={side}
                            />
                          </motion.div>
                        ))}

                        {/* AI thinking indicator */}
                        {isActive && isAiThinking && round.arguments.length > 0 && round.arguments[round.arguments.length - 1].speaker === "user" && (
                          <motion.div
                            initial={{ opacity: 0 }}
                            animate={{ opacity: 1 }}
                            className="glass rounded-2xl px-6 py-4 flex items-center gap-3"
                          >
                            <div className="flex size-8 items-center justify-center rounded-full bg-purple-500/15 text-sm">
                              {persona.icon}
                            </div>
                            <div className="flex items-center gap-1.5">
                              <span className="size-1.5 rounded-full bg-purple-400 animate-pulse" />
                              <span className="size-1.5 rounded-full bg-purple-400 animate-pulse [animation-delay:0.2s]" />
                              <span className="size-1.5 rounded-full bg-purple-400 animate-pulse [animation-delay:0.4s]" />
                            </div>
                            <span className="text-xs text-foreground/30">{persona.name} is {persona.thinkingLabel}...</span>
                          </motion.div>
                        )}
                      </div>

                      {/* Observations for this round — inside the chapter */}
                      {round.observations.length > 0 && (
                        <motion.div
                          initial={{ opacity: 0 }}
                          animate={{ opacity: 1 }}
                          transition={{ delay: 0.6, duration: 0.5 }}
                          className="mt-5 space-y-2"
                        >
                          {round.observations.map((obs) => (
                            <ObservationCard key={obs.id} observation={obs} />
                          ))}
                        </motion.div>
                      )}
                    </motion.div>
                  );
                })}
              </AnimatePresence>
            </div>

            {/* Composer */}
            {currentRoundData && !isAiThinking && (
              <ArgumentComposer
                roundLabel={currentRoundData.label}
                onSubmit={handleUserSubmit}
                disabled={isAiThinking}
              />
            )}
          </div>

          {/* Analysis panel — desktop only */}
          <div className="hidden lg:block w-80 shrink-0">
            <div className="sticky top-6">
              <AnalysisPanel
                score={score}
                observations={allObservations}
                currentRound={currentRound + 1}
                totalRounds={totalRounds}
                personaName={persona.name}
              />
            </div>
          </div>
        </div>

        {/* Mobile score bar */}
        <div className="lg:hidden fixed bottom-0 left-0 right-0 glass border-t border-white/8 px-6 py-3 flex items-center justify-between z-50">
          <div className="flex items-center gap-3">
            <span className="font-heading text-lg font-bold text-foreground">{score.overall}</span>
            <span className="text-xs text-foreground/30">score</span>
          </div>
          <div className="flex items-center gap-4 text-xs text-foreground/40">
            <span>⚠ {allObservations.filter((o) => o.type === "fallacy").length}</span>
            <span>💪 {allObservations.filter((o) => o.type === "strength").length}</span>
            <span>Round {currentRound + 1}/{totalRounds}</span>
          </div>
        </div>
      </div>
    </div>
  );
}
