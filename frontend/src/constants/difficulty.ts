import type { Difficulty } from "@/types";

export const difficulties: {
  id: Difficulty;
  label: string;
  description: string;
  icon: string;
}[] = [
  {
    id: "apprentice",
    label: "Apprentice",
    description: "A measured exchange, accessible reasoning",
    icon: "🌱",
  },
  {
    id: "scholar",
    label: "Scholar",
    description: "Sharper rebuttals, deeper analysis",
    icon: "📚",
  },
  {
    id: "master",
    label: "Master",
    description: "Relentless logic, no easy wins",
    icon: "👑",
  },
];
