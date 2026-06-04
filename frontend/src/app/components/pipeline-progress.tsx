import { motion } from "motion/react";
import { Progress } from "@radix-ui/react-progress";

import { PipelineStage } from "../App";

interface PipelineProgressProps {
  stages: PipelineStage[];
  progress: number;
  isProcessing: boolean;
  error: string | null;
  onReset: () => void;
}

export function PipelineProgress({
  stages,
  progress,
  isProcessing,
  error,
  onReset,
}: PipelineProgressProps) {
  return (
    <div className="py-12 px-6">
      <div className="max-w-4xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl p-8"
        >
          <div className="flex items-center justify-between mb-8">
            <div>
              <h3 className="mb-1">Pipeline Status</h3>
              <p className="text-sm text-[var(--muted-foreground)]">
                {isProcessing
                  ? "Multi-agent orchestration active..."
                  : error
                  ? "Pipeline execution failed"
                  : "Modernization completed successfully!"}
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl text-[var(--neon-blue)]">{progress}%</div>
              <div className="text-xs text-[var(--muted-foreground)]">Overall Progress</div>
            </div>
          </div>

          <div className="mb-6">
            <Progress value={progress} className="h-2 w-full bg-[var(--input-background)] rounded-full overflow-hidden">
              <motion.div
                className="h-full bg-gradient-to-r from-[var(--neon-blue)] via-[var(--neon-purple)] to-[var(--neon-emerald)]"
                initial={{ width: 0 }}
                animate={{ width: `${progress}%` }}
                transition={{ duration: 0.5, ease: "easeOut" }}
              />
            </Progress>
          </div>

          {error && (
            <div className="mb-6 p-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-400 text-xs font-mono">
              <strong>Error:</strong> {error}
            </div>
          )}

          <div className="space-y-4">
            {stages.map((stage, index) => (
              <motion.div
                key={stage.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
                className="flex items-center gap-4 p-4 rounded-xl bg-[var(--input-background)]"
              >
                <div className="flex-shrink-0">
                  {stage.status === "complete" ? (
                    <div className="w-10 h-10 rounded-full bg-[var(--neon-emerald)]/20 flex items-center justify-center">
                      <div className="w-5 h-5 rounded-full bg-[var(--neon-emerald)]"></div>
                    </div>
                  ) : stage.status === "running" ? (
                    <div className="w-10 h-10 rounded-full bg-[var(--neon-blue)]/20 flex items-center justify-center">
                      <motion.div
                        className="w-5 h-5 rounded-full bg-[var(--neon-blue)]"
                        animate={{ scale: [1, 1.2, 1] }}
                        transition={{ duration: 1, repeat: Infinity }}
                      />
                    </div>
                  ) : stage.status === "error" ? (
                    <div className="w-10 h-10 rounded-full bg-red-500/20 flex items-center justify-center">
                      <div className="w-5 h-5 rounded-full bg-red-500"></div>
                    </div>
                  ) : (
                    <div className="w-10 h-10 rounded-full bg-[var(--muted)] flex items-center justify-center">
                      <div className="w-5 h-5 rounded-full border-2 border-[var(--muted-foreground)]"></div>
                    </div>
                  )}
                </div>

                <div className="flex-grow">
                  <div className="flex items-center justify-between mb-1">
                    <span className="text-sm">{stage.name}</span>
                    <span className="text-xs text-[var(--muted-foreground)]">
                      {stage.progress}%
                    </span>
                  </div>
                  <p className="text-xs text-[var(--muted-foreground)]">{stage.details}</p>
                  {stage.progress > 0 && stage.progress < 100 && (
                    <div className="mt-2 h-1 w-full bg-[var(--muted)] rounded-full overflow-hidden">
                      <motion.div
                        className="h-full bg-[var(--neon-blue)]"
                        initial={{ width: 0 }}
                        animate={{ width: `${stage.progress}%` }}
                        transition={{ duration: 0.5 }}
                      />
                    </div>
                  )}
                </div>
              </motion.div>
            ))}
          </div>

          <div className="mt-6 flex gap-3">
            <motion.button
              onClick={onReset}
              className="flex-1 px-4 py-3 rounded-xl glass text-sm"
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
            >
              Clear & Start Over
            </motion.button>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
