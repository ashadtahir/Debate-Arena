import type { Persona } from "@/types";

export const personas: Persona[] = [
  {
    id: "socrates",
    name: "Socrates",
    title: "The Relentless Questioner",
    quote: "The unexamined life is not worth living.",
    description:
      "Dissects your arguments through probing questions. Never accepts an answer at face value.",
    icon: "🏛️",
    strategy: "Dialectic questioning",
    accent: "purple",
    debateTitle: "Questions Assumptions",
    debateSubtitle: "Probing the foundations of your argument",
    thinkingLabel: "examining your reasoning",
  },
  {
    id: "prosecutor",
    name: "The Prosecutor",
    title: "Champion of Evidence",
    quote: "The truth will set you free — but first, it will make you miserable.",
    description:
      "Demands proof for every claim. Builds airtight cases and exploits logical weak points.",
    icon: "⚖️",
    strategy: "Evidence-based reasoning",
    accent: "cyan",
    debateTitle: "Cross-Examining Evidence",
    debateSubtitle: "Demanding proof for every claim",
    thinkingLabel: "reviewing the evidence",
  },
  {
    id: "philosopher",
    name: "The Philosopher",
    title: "Big Picture Thinker",
    quote: "He who has a why to live can bear almost any how.",
    description:
      "Challenges your foundational assumptions. Explores ethics, logic, and first principles.",
    icon: "🌀",
    strategy: "First principles analysis",
    accent: "purple",
    debateTitle: "Exploring First Principles",
    debateSubtitle: "Challenging what you take for granted",
    thinkingLabel: "reflecting on deeper principles",
  },
  {
    id: "devils-advocate",
    name: "Devil's Advocate",
    title: "The Contrarian",
    quote: "I learned long ago to never wrestle with a pig. You get dirty, and besides, the pig likes it.",
    description:
      "Takes the opposing position by design. Finds counterarguments you never considered.",
    icon: "🔥",
    strategy: "Adversarial counterpoint",
    accent: "cyan",
    debateTitle: "Stress-Testing Your Position",
    debateSubtitle: "Finding the cracks in your reasoning",
    thinkingLabel: "finding weaknesses",
  },
];
