import { motion } from "motion/react";
import { Code2, Sparkles, ArrowRight } from "lucide-react";

export function HeroSection() {
  const legacyCode = `// Legacy COBOL
IDENTIFICATION DIVISION.
PROGRAM-ID. CALC.
DATA DIVISION.
WORKING-STORAGE SECTION.
01 NUM1 PIC 9(4) VALUE 0.
01 NUM2 PIC 9(4) VALUE 0.
PROCEDURE DIVISION.
COMPUTE NUM1 = NUM1 + NUM2.`;

  const modernCode = `# Modern Python
from typing import List
import pytest

class Calculator:
    """AI-modernized calculator with type safety."""

    def __init__(self):
        self.history: List[float] = []

    def add(self, num1: float, num2: float) -> float:
        result = num1 + num2
        self.history.append(result)
        return result`;

  return (
    <div className="relative min-h-screen flex items-center justify-center px-6 overflow-hidden">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.8 }}
        className="max-w-7xl w-full z-10"
      >
        <div className="text-center mb-12">
          <motion.div
            initial={{ scale: 0.5, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass glow-blue mb-6"
          >
            <Sparkles className="w-4 h-4 text-[var(--neon-blue)]" />
            <span className="text-sm">AI-Powered Legacy Code Modernization</span>
          </motion.div>

          <h1 className="text-6xl mb-6 bg-gradient-to-r from-[var(--neon-blue)] via-[var(--neon-purple)] to-[var(--neon-emerald)] bg-clip-text text-transparent">
            LegacyCoder
          </h1>

          <p className="text-xl text-[var(--muted-foreground)] max-w-3xl mx-auto mb-8">
            Transform decades-old COBOL, Fortran, Java, and C++ into modern, tested, verified Python code
            with intelligent AI agents and comprehensive validation pipelines.
          </p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 items-center">
          <motion.div
            initial={{ x: -50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.4 }}
            className="glass rounded-2xl p-6 glow-purple"
          >
            <div className="flex items-center gap-2 mb-4">
              <Code2 className="w-5 h-5 text-[var(--destructive)]" />
              <span className="text-sm text-[var(--muted-foreground)]">Legacy Code</span>
            </div>
            <pre className="text-sm overflow-x-auto text-[var(--destructive)]/80 font-mono">
              {legacyCode}
            </pre>
          </motion.div>

          <motion.div
            initial={{ scale: 0.8, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            transition={{ delay: 0.6, repeat: Infinity, repeatDelay: 3, duration: 0.5 }}
            className="flex justify-center"
          >
            <div className="relative">
              <div className="absolute inset-0 bg-gradient-to-r from-[var(--neon-blue)] to-[var(--neon-purple)] rounded-full blur-xl opacity-50"></div>
              <ArrowRight className="w-12 h-12 text-[var(--neon-blue)] relative z-10" />
            </div>
          </motion.div>

          <motion.div
            initial={{ x: 50, opacity: 0 }}
            animate={{ x: 0, opacity: 1 }}
            transition={{ delay: 0.8 }}
            className="glass rounded-2xl p-6 glow-emerald lg:col-start-2"
          >
            <div className="flex items-center gap-2 mb-4">
              <Sparkles className="w-5 h-5 text-[var(--neon-emerald)]" />
              <span className="text-sm text-[var(--muted-foreground)]">Modern Python</span>
            </div>
            <pre className="text-sm overflow-x-auto text-[var(--neon-emerald)]/80 font-mono">
              {modernCode}
            </pre>
          </motion.div>
        </div>
      </motion.div>

      <div className="absolute inset-0 pointer-events-none">
        {[...Array(20)].map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-1 h-1 bg-[var(--neon-blue)] rounded-full"
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
            animate={{
              opacity: [0, 1, 0],
              scale: [0, 1.5, 0],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 5,
            }}
          />
        ))}
      </div>
    </div>
  );
}
