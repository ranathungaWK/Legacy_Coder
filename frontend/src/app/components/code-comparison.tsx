import { motion } from "motion/react";
import { ChevronLeft, ChevronRight, Copy, Download } from "lucide-react";
import { useState } from "react";

interface CodeComparisonProps {
  legacyCode: string;
  modernCode: string;
  selectedLanguage: string;
}

export function CodeComparison({
  legacyCode,
  modernCode,
  selectedLanguage,
}: CodeComparisonProps) {
  const [view, setView] = useState<"split" | "legacy" | "modern">("split");

  return (
    <div className="py-12 px-6">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          className="glass rounded-2xl overflow-hidden"
        >
          <div className="p-6 border-b border-[var(--border)] flex items-center justify-between">
            <h3>Code Comparison</h3>
            <div className="flex items-center gap-2">
              <div className="flex bg-[var(--input-background)] rounded-lg p-1">
                <button
                  onClick={() => setView("legacy")}
                  className={`px-3 py-1 rounded text-xs transition-all ${
                    view === "legacy"
                      ? "bg-[var(--neon-blue)] text-[var(--background)]"
                      : "text-[var(--muted-foreground)]"
                  }`}
                >
                  Legacy
                </button>
                <button
                  onClick={() => setView("split")}
                  className={`px-3 py-1 rounded text-xs transition-all ${
                    view === "split"
                      ? "bg-[var(--neon-blue)] text-[var(--background)]"
                      : "text-[var(--muted-foreground)]"
                  }`}
                >
                  Split
                </button>
                <button
                  onClick={() => setView("modern")}
                  className={`px-3 py-1 rounded text-xs transition-all ${
                    view === "modern"
                      ? "bg-[var(--neon-blue)] text-[var(--background)]"
                      : "text-[var(--muted-foreground)]"
                  }`}
                >
                  Modern
                </button>
              </div>
              <motion.button
                className="p-2 glass rounded-lg hover:glow-blue transition-all"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  const textToCopy = view === "legacy" ? legacyCode : modernCode;
                  navigator.clipboard.writeText(textToCopy);
                }}
                title="Copy code"
              >
                <Copy className="w-4 h-4" />
              </motion.button>
              <motion.button
                className="p-2 glass rounded-lg hover:glow-blue transition-all"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => {
                  const textToDownload = view === "legacy" ? legacyCode : modernCode;
                  const blob = new Blob([textToDownload], { type: "text/plain" });
                  const url = URL.createObjectURL(blob);
                  const a = document.createElement("a");
                  a.href = url;
                  a.download = view === "legacy" ? "legacy_code.txt" : "modern_code.py";
                  document.body.appendChild(a);
                  a.click();
                  document.body.removeChild(a);
                  URL.revokeObjectURL(url);
                }}
                title="Download code"
              >
                <Download className="w-4 h-4" />
              </motion.button>
            </div>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 divide-x divide-[var(--border)]">
            {(view === "split" || view === "legacy") && (
              <div className="p-6 bg-[var(--input-background)]/30">
                <div className="flex items-center gap-2 mb-4">
                  <ChevronLeft className="w-4 h-4 text-[var(--destructive)]" />
                  <span className="text-sm text-[var(--muted-foreground)]">
                    Legacy {selectedLanguage.toUpperCase()}
                  </span>
                </div>
                <pre className="text-xs overflow-auto h-[500px] font-mono text-[var(--destructive)]/80 whitespace-pre">
                  {legacyCode}
                </pre>
              </div>
            )}

            {(view === "split" || view === "modern") && (
              <div className="p-6">
                <div className="flex items-center gap-2 mb-4">
                  <ChevronRight className="w-4 h-4 text-[var(--neon-emerald)]" />
                  <span className="text-sm text-[var(--muted-foreground)]">
                    Modernized Python 3.12
                  </span>
                </div>
                <pre className="text-xs overflow-auto h-[500px] font-mono text-[var(--neon-emerald)]/80 whitespace-pre">
                  {modernCode}
                </pre>
              </div>
            )}
          </div>
        </motion.div>
      </div>
    </div>
  );
}
