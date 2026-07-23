"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Swords, Zap } from "lucide-react";
import { Button } from "@/components/ui/button";

export default function Home() {
  const [healthResponse, setHealthResponse] = useState<Record<string, string> | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const checkBackend = async () => {
    setLoading(true);
    setError(null);
    setHealthResponse(null);
    try {
      const res = await fetch("http://localhost:8000/health");
      const data = await res.json();
      setHealthResponse(data);
    } catch {
      setError("Could not reach backend. Is it running on port 8000?");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center min-h-screen bg-background px-4">
      <motion.main
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6, ease: "easeOut" }}
        className="flex flex-col items-center gap-8 text-center max-w-xl"
      >
        <motion.div
          initial={{ scale: 0.8, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: 0.15, duration: 0.5 }}
          className="flex items-center gap-3"
        >
          <Swords className="size-10 text-primary" />
          <h1 className="text-5xl font-bold tracking-tight text-foreground">
            DebateArena
          </h1>
        </motion.div>

        <motion.p
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.35, duration: 0.5 }}
          className="text-lg text-muted-foreground leading-relaxed"
        >
          Where ideas clash and knowledge wins.
          <br />
          AI-powered structured debates for sharper thinking.
        </motion.p>

        <motion.div
          initial={{ opacity: 0, y: 12 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.5, duration: 0.4 }}
        >
          <Button
            onClick={checkBackend}
            disabled={loading}
            size="lg"
            className="gap-2 px-6 text-base"
          >
            <Zap className="size-4" />
            {loading ? "Checking..." : "Check Backend"}
          </Button>
        </motion.div>

        {healthResponse && (
          <motion.div
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.3 }}
            className="mt-2 w-full rounded-lg border border-border bg-card p-5 text-left shadow-lg"
          >
            <p className="text-xs font-medium uppercase tracking-wider text-muted-foreground mb-2">
              Backend Response
            </p>
            <pre className="text-sm text-card-foreground font-mono whitespace-pre-wrap">
              {JSON.stringify(healthResponse, null, 2)}
            </pre>
          </motion.div>
        )}

        {error && (
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            className="mt-2 text-sm text-destructive"
          >
            {error}
          </motion.p>
        )}
      </motion.main>
    </div>
  );
}
