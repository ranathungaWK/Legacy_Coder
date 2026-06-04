import { motion } from "motion/react";
import { Terminal, ChevronRight, CheckCircle2, XCircle, Info } from "lucide-react";
import { useState, useEffect } from "react";

interface LogEntry {
  id: string;
  timestamp: string;
  type: "info" | "success" | "error" | "command";
  message: string;
}

export function TerminalConsole() {
  const [logs, setLogs] = useState<LogEntry[]>([
    {
      id: "1",
      timestamp: "14:23:45",
      type: "command",
      message: "$ legacycoder modernize customer_account.cbl --target python",
    },
    {
      id: "2",
      timestamp: "14:23:46",
      type: "info",
      message: "🔍 Comprehension Agent: Analyzing COBOL source structure...",
    },
    {
      id: "3",
      timestamp: "14:23:48",
      type: "success",
      message: "✓ AST generation complete: 2,453 lines, 47 procedures identified",
    },
    {
      id: "4",
      timestamp: "14:23:49",
      type: "info",
      message: "🔧 Modernization Agent: Transforming to Python dataclasses...",
    },
    {
      id: "5",
      timestamp: "14:23:51",
      type: "info",
      message: "🧪 Testing Agent: Generating pytest test suite...",
    },
    {
      id: "6",
      timestamp: "14:23:53",
      type: "success",
      message: "✓ Generated 14 test cases with 96.2% coverage",
    },
    {
      id: "7",
      timestamp: "14:23:54",
      type: "info",
      message: "🐳 Verification Agent: Building Docker container...",
    },
    {
      id: "8",
      timestamp: "14:23:58",
      type: "success",
      message: "✓ All verification checks passed",
    },
  ]);

  const [autoScroll, setAutoScroll] = useState(true);

  useEffect(() => {
    const interval = setInterval(() => {
      const newLog: LogEntry = {
        id: Date.now().toString(),
        timestamp: new Date().toLocaleTimeString("en-US", { hour12: false }),
        type: "info",
        message: "⚡ Pipeline status: Running (68% complete)",
      };
      setLogs((prev) => [...prev, newLog]);
    }, 5000);

    return () => clearInterval(interval);
  }, []);

  const getIcon = (type: LogEntry["type"]) => {
    switch (type) {
      case "success":
        return <CheckCircle2 className="w-4 h-4 text-[var(--neon-emerald)]" />;
      case "error":
        return <XCircle className="w-4 h-4 text-[var(--destructive)]" />;
      case "command":
        return <ChevronRight className="w-4 h-4 text-[var(--neon-blue)]" />;
      default:
        return <Info className="w-4 h-4 text-[var(--muted-foreground)]" />;
    }
  };

  const getTextColor = (type: LogEntry["type"]) => {
    switch (type) {
      case "success":
        return "text-[var(--neon-emerald)]";
      case "error":
        return "text-[var(--destructive)]";
      case "command":
        return "text-[var(--neon-blue)]";
      default:
        return "text-[var(--foreground)]";
    }
  };

  return (
    <div className="py-12 px-6">
      <div className="max-w-6xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl overflow-hidden"
        >
          <div className="flex items-center justify-between p-4 border-b border-[var(--border)] bg-[var(--input-background)]">
            <div className="flex items-center gap-3">
              <Terminal className="w-5 h-5 text-[var(--neon-blue)]" />
              <h3 className="text-sm">Verification Console</h3>
              <motion.div
                className="w-2 h-2 rounded-full bg-[var(--neon-emerald)]"
                animate={{ opacity: [1, 0.5, 1] }}
                transition={{ duration: 2, repeat: Infinity }}
              />
            </div>

            <div className="flex items-center gap-2">
              <button
                onClick={() => setAutoScroll(!autoScroll)}
                className={`text-xs px-3 py-1 rounded-lg transition-all ${
                  autoScroll
                    ? "bg-[var(--neon-blue)]/20 text-[var(--neon-blue)]"
                    : "bg-[var(--muted)] text-[var(--muted-foreground)]"
                }`}
              >
                Auto-scroll
              </button>
              <button className="text-xs px-3 py-1 rounded-lg bg-[var(--muted)] text-[var(--muted-foreground)] hover:bg-[var(--muted)]/80 transition-all">
                Clear
              </button>
            </div>
          </div>

          <div className="p-6 h-[400px] overflow-y-auto font-mono bg-[var(--background)]">
            <div className="space-y-2">
              {logs.map((log, index) => (
                <motion.div
                  key={log.id}
                  initial={{ opacity: 0, x: -10 }}
                  animate={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.05 }}
                  className="flex items-start gap-3 group hover:bg-[var(--input-background)] p-2 rounded transition-colors"
                >
                  <span className="text-xs text-[var(--muted-foreground)] flex-shrink-0 font-mono">
                    {log.timestamp}
                  </span>
                  <div className="flex-shrink-0 mt-0.5">{getIcon(log.type)}</div>
                  <span className={`text-xs flex-grow ${getTextColor(log.type)}`}>
                    {log.message}
                  </span>
                </motion.div>
              ))}
            </div>

            <motion.div
              className="flex items-center gap-2 mt-4"
              animate={{ opacity: [1, 0.5, 1] }}
              transition={{ duration: 1.5, repeat: Infinity }}
            >
              <ChevronRight className="w-4 h-4 text-[var(--neon-blue)]" />
              <span className="text-xs text-[var(--muted-foreground)]">_</span>
            </motion.div>
          </div>

          <div className="p-4 border-t border-[var(--border)] bg-[var(--input-background)] flex items-center justify-between">
            <div className="flex items-center gap-4 text-xs text-[var(--muted-foreground)]">
              <span>Docker: python:3.12-slim</span>
              <span>•</span>
              <span>Memory: 124 MB / 2 GB</span>
              <span>•</span>
              <span>CPU: 23%</span>
            </div>
            <div className="text-xs text-[var(--neon-emerald)]">
              Container ID: a7f3c92e
            </div>
          </div>
        </motion.div>
      </div>
    </div>
  );
}
