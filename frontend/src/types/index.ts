export type Persona = {
  id: string;
  name: string;
  title: string;
  quote: string;
  description: string;
  icon: string;
  strategy: string;
  accent: string;
  debateTitle: string;
  debateSubtitle: string;
  thinkingLabel: string;
};

export type Topic = {
  id: string;
  title: string;
  category: string;
};

export type Side = "for" | "against";

export type Difficulty = "apprentice" | "scholar" | "master";

export type SetupState = {
  persona: Persona | null;
  topic: Topic | null;
  side: Side | null;
  difficulty: Difficulty | null;
};

export type Argument = {
  id: string;
  round: number;
  speaker: "user" | "ai";
  content: string;
};

export type ObservationType = "fallacy" | "strength" | "suggestion";

export type Observation = {
  id: string;
  round: number;
  type: ObservationType;
  title: string;
  description: string;
};

export type RoundLabel =
  | "Opening Arguments"
  | "Rebuttal"
  | "Counter-Rebuttal"
  | "Final Challenge"
  | "Closing Statements";

export type Round = {
  number: number;
  label: RoundLabel;
  arguments: Argument[];
  observations: Observation[];
};

export type Score = {
  overall: number;
  logic: number;
  evidence: number;
  persuasion: number;
};

export type DebateStatus = "intro" | "active" | "completed";

export type DebateState = {
  setup: SetupState;
  rounds: Round[];
  currentRound: number;
  score: Score;
  status: DebateStatus;
};

export type DebateAnalysisScores = {
  overall: number;
  logic: number;
  evidence: number;
  coherence: number;
  persuasion: number;
};

export type DebateAnalysisObservation = {
  type: "fallacy" | "strength" | "suggestion";
  title: string;
  description: string;
};

export type DebateFallacy = {
  type: string;
  name: string;
  confidence: number;
  explanation: string;
  evidence: string;
};

export type DebateAnalysis = {
  scores: DebateAnalysisScores;
  observations: DebateAnalysisObservation[];
  fallacies: DebateFallacy[];
  strengths: string[];
  improvements: string[];
  insight: string;
};

export type DebateApiResponse = {
  response: string;
  thinking_style: string;
  next_focus: string;
  tone: string;
  persona_id: string;
  round_number: number;
  parse_success: boolean;
  analysis: DebateAnalysis | null;
};
