"use client";

import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Brain, ShieldAlert, BarChart3, ArrowRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import DebatePreview from "@/components/landing/DebatePreview";

const features = [
  {
    icon: Brain,
    title: "Adaptive Personas",
    description:
      "Debate against unique AI personalities including Socrates, Prosecutor, Philosopher, and Devil's Advocate.",
    color: "text-purple-400",
    glow: "group-hover:shadow-[0_0_50px_12px_oklch(0.65_0.26_290_/_20%)]",
  },
  {
    icon: ShieldAlert,
    title: "Live Fallacy Detection",
    description:
      "Receive real-time feedback when your arguments contain logical fallacies.",
    color: "text-cyan-400",
    glow: "group-hover:shadow-[0_0_50px_12px_oklch(0.72_0.18_195_/_20%)]",
  },
  {
    icon: BarChart3,
    title: "Debate Analytics",
    description:
      "Get a post-debate scorecard measuring logic, evidence, consistency, and persuasiveness.",
    color: "text-purple-300",
    glow: "group-hover:shadow-[0_0_50px_12px_oklch(0.65_0.22_320_/_20%)]",
  },
];

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.15 } },
};

const item = {
  hidden: { opacity: 0, y: 24 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.5, ease: [0.25, 0.1, 0.25, 1] as const },
  },
};

export default function Home() {
  const router = useRouter();

  return (
    <div className="relative min-h-screen overflow-hidden bg-background">
      {/* Background layers */}
      <div className="pointer-events-none absolute inset-0" aria-hidden>
        {/* Grid pattern */}
        <div className="grid-pattern absolute inset-0" />

        {/* Floating gradient orbs */}
        <motion.div
          animate={{ y: [0, -18, 0] }}
          transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
          className="absolute -top-40 left-1/2 h-[600px] w-[600px] -translate-x-1/2 rounded-full bg-purple-600/20 blur-[120px]"
        />
        <motion.div
          animate={{ y: [0, -12, 0], x: [0, 8, 0] }}
          transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-1/3 -right-40 h-[400px] w-[400px] rounded-full bg-cyan-500/15 blur-[100px]"
        />
        <motion.div
          animate={{ y: [0, -14, 0] }}
          transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
          className="absolute bottom-0 left-1/4 h-[300px] w-[300px] rounded-full bg-purple-500/10 blur-[80px]"
        />

        {/* Aurora band */}
        <motion.div
          animate={{ opacity: [0.25, 0.5, 0.25], x: ["-5%", "5%", "-5%"], scaleX: [1, 1.05, 1] }}
          transition={{ duration: 15, repeat: Infinity, ease: "easeInOut" }}
          className="absolute top-[20%] left-0 h-[2px] w-full bg-gradient-to-r from-transparent via-purple-500/40 to-transparent blur-[1px]"
        />
      </div>

      {/* Hero */}
      <section className="relative flex min-h-screen flex-col items-center justify-center px-6 text-center">
        <motion.div
          initial={{ opacity: 0, y: 32 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.7, ease: "easeOut" }}
          className="flex flex-col items-center gap-8"
        >
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.1, duration: 0.5 }}
            className="inline-flex items-center gap-2 rounded-full border border-purple-500/20 bg-purple-500/10 px-4 py-1.5 text-sm text-purple-300"
          >
            <span className="size-1.5 rounded-full bg-purple-400 animate-pulse" />
            Powered by Adaptive AI
          </motion.div>

          <h1 className="font-heading text-7xl font-bold tracking-tighter sm:text-8xl lg:text-[120px] xl:text-[144px] leading-[0.88]">
            <span className="text-gradient-purple">DebateArena</span>
          </h1>

          <p className="max-w-2xl text-xl font-light leading-relaxed text-foreground/45 sm:text-2xl">
            Challenge adaptive AI opponents. Sharpen your reasoning.
            <br className="hidden sm:block" />{" "}
            Master the art of argument.
          </p>

          <motion.div
            initial={{ opacity: 0, y: 16 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3, duration: 0.5 }}
          >
            <Button
              size="lg"
              onClick={() => router.push("/setup")}
              className="group gap-2 px-10 py-7 text-lg font-bold tracking-wide rounded-xl bg-purple-600 text-white hover:bg-purple-500 transition-all duration-300 ring-2 ring-purple-400/20 hover:ring-purple-400/40 hover:scale-[1.02] active:scale-[0.98]"
              style={{ animation: "breathe-glow 3s ease-in-out infinite" }}
            >
              Start Debating
              <ArrowRight className="size-4 transition-transform duration-300 group-hover:translate-x-1.5" />
            </Button>
          </motion.div>
        </motion.div>

        {/* Scroll hint */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 1, duration: 0.6 }}
          className="absolute bottom-10"
        >
          <div className="size-5 rounded-full border-2 border-muted-foreground/30 p-1">
            <div className="size-full animate-bounce rounded-full bg-muted-foreground/30" />
          </div>
        </motion.div>
      </section>

      {/* Trust statement */}
      <section className="relative px-6 pb-20 pt-4">
        <motion.p
          initial={{ opacity: 0, y: 12 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.5 }}
          className="text-center text-sm text-muted-foreground/60"
        >
          Master logical reasoning with adaptive AI debate opponents.
        </motion.p>
      </section>

      {/* Debate Preview */}
      <section className="relative py-24">
        <DebatePreview />
      </section>

      {/* Features */}
      <section className="relative px-6 pt-24 pb-40">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.5 }}
          className="text-center mb-20"
        >
          <h2 className="font-heading text-4xl font-bold tracking-tight sm:text-5xl lg:text-6xl leading-tight">
            Built for{" "}
            <span className="text-gradient-purple">sharper thinkers</span>
          </h2>
          <p className="mt-5 text-xl font-light text-foreground/40 sm:text-2xl">
            Everything you need to elevate your argumentation skills.
          </p>
        </motion.div>

        <motion.div
          variants={container}
          initial="hidden"
          whileInView="show"
          viewport={{ once: true, margin: "-80px" }}
          className="mx-auto grid max-w-6xl gap-8 sm:grid-cols-2 lg:grid-cols-3"
        >
          {features.map((feature) => (
            <motion.div
              key={feature.title}
              variants={item}
              className={`group glass glass-hover rounded-2xl p-10 transition-all duration-300 shadow-lg shadow-black/20 hover:shadow-xl hover:-translate-y-1 ${feature.glow}`}
            >
              <div
                className={`mb-6 inline-flex size-14 items-center justify-center rounded-xl bg-white/5 transition-transform duration-300 group-hover:scale-110 ${feature.color}`}
              >
                <feature.icon className="size-7" />
              </div>
              <h3 className="mb-3 font-heading text-xl font-semibold tracking-wide text-foreground">
                {feature.title}
              </h3>
              <p className="text-base leading-relaxed text-foreground/45">
                {feature.description}
              </p>
            </motion.div>
          ))}
        </motion.div>
      </section>
    </div>
  );
}
