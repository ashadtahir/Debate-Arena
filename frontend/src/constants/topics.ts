import type { Topic } from "@/types";

export const topics: Topic[] = [
  {
    id: "ai-replacement",
    title: "AI will replace most white-collar jobs within a decade",
    category: "Technology",
  },
  {
    id: "space-funding",
    title: "Space exploration funding should take priority over ocean research",
    category: "Science",
  },
  {
    id: "social-media",
    title: "Social media does more harm than good for society",
    category: "Society",
  },
  {
    id: "ubi",
    title: "Universal basic income is inevitable and necessary",
    category: "Economics",
  },
  {
    id: "education",
    title: "Traditional universities are obsolete in the age of information",
    category: "Education",
  },
  {
    id: "privacy",
    title: "Personal privacy should be sacrificed for public safety",
    category: "Ethics",
  },
  {
    id: "nuclear",
    title: "Nuclear energy is essential for a sustainable future",
    category: "Environment",
  },
  {
    id: "democracy",
    title: "Democracy is the best system of governance available",
    category: "Politics",
  },
];

export const categories = [...new Set(topics.map((t) => t.category))];
