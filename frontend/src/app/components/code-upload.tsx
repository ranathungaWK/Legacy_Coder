import { motion } from "motion/react";
import { ClipboardPaste, Check, Sparkles, X } from "lucide-react";
import { useState } from "react";

const placeholders: Record<string, string> = {
  cobol: `       IDENTIFICATION DIVISION.
       PROGRAM-ID. LEGACY-CALC.
       DATA DIVISION.
       WORKING-STORAGE SECTION.
       01 WS-NUM1 PIC 9(5) VALUE 0.
       01 WS-NUM2 PIC 9(5) VALUE 0.
       01 WS-RESULT PIC 9(10) VALUE 0.
       PROCEDURE DIVISION.
           MOVE 12345 TO WS-NUM1
           MOVE 67890 TO WS-NUM2
           MULTIPLY WS-NUM1 BY WS-NUM2 GIVING WS-RESULT
           DISPLAY WS-RESULT
           STOP RUN.`,
  fortran: `      PROGRAM LEGACY
      INTEGER I, N, SUM
      N = 100
      SUM = 0
      DO 10 I = 1, N
        SUM = SUM + I
   10 CONTINUE
      WRITE(*,*) 'Sum =', SUM
      END`,
  java: `public class LegacyProcessor {
    public static void main(String[] args) {
        int[] data = {5, 3, 8, 1, 9, 2};
        for (int i = 0; i < data.length - 1; i++) {
            for (int j = 0; j < data.length - i - 1; j++) {
                if (data[j] > data[j + 1]) {
                    int temp = data[j];
                    data[j] = data[j + 1];
                    data[j + 1] = temp;
                }
            }
        }
    }
}`,
  cpp: `#include <iostream>
#include <vector>
using namespace std;

int fibonacci(int n) {
    if (n <= 1) return n;
    int a = 0, b = 1, c;
    for (int i = 2; i <= n; i++) {
        c = a + b;
        a = b;
        b = c;
    }
    return b;
}

int main() {
    for (int i = 0; i < 10; i++)
        cout << fibonacci(i) << " ";
    return 0;
}`,
  c: `#include <stdio.h>

int main() {
    int n = 10, i;
    long long fact = 1;
    for (i = 1; i <= n; ++i) {
        fact *= i;
    }
    printf("Factorial of %d = %lld\\n", n, fact);
    return 0;
}`,
};

interface CodeUploadProps {
  code: string;
  setCode: (code: string) => void;
  selectedLanguage: string;
  setSelectedLanguage: (lang: string) => void;
  isProcessing: boolean;
  submitted: boolean;
  setSubmitted: (sub: boolean) => void;
  onSubmit: () => void;
  onReset: () => void;
}

export function CodeUpload({
  code,
  setCode,
  selectedLanguage,
  setSelectedLanguage,
  isProcessing,
  submitted,
  setSubmitted,
  onSubmit,
  onReset,
}: CodeUploadProps) {
  const languages = [
    { id: "cobol", name: "COBOL", color: "var(--neon-blue)" },
    { id: "fortran", name: "Fortran", color: "var(--neon-purple)" },
    { id: "c", name: "C", color: "#38bdf8" },
    { id: "cpp", name: "C++", color: "#f59e0b" },
    { id: "java", name: "Java", color: "var(--neon-emerald)" },
  ];

  const handlePaste = async () => {
    try {
      const text = await navigator.clipboard.readText();
      setCode(text);
    } catch {
      // clipboard access denied — user can type manually
    }
  };

  const handleSubmit = () => {
    if (code.trim()) {
      onSubmit();
    }
  };

  const handleReset = () => {
    onReset();
  };

  const activeLang = languages.find((l) => l.id === selectedLanguage)!;

  return (
    <div className="py-20 px-6">
      <div className="max-w-5xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="mb-4">Paste Your Legacy Code</h2>
          <p className="text-[var(--muted-foreground)] max-w-2xl mx-auto">
            Copy your legacy code and paste it below to begin the AI-powered modernization process
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Language selector */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="glass rounded-2xl p-6"
          >
            <h3 className="mb-4 text-sm">Select Source Language</h3>
            <div className="space-y-3">
              {languages.map((lang) => (
                <motion.button
                  key={lang.id}
                  onClick={() => {
                    setSelectedLanguage(lang.id);
                    setSubmitted(false);
                    setCode("");
                  }}
                  className={`w-full px-4 py-3 rounded-xl transition-all flex items-center justify-between ${
                    selectedLanguage === lang.id
                      ? "glass"
                      : "bg-[var(--input-background)] hover:bg-[var(--muted)]"
                  }`}
                  style={{
                    borderColor: selectedLanguage === lang.id ? lang.color : "transparent",
                    borderWidth: "1px",
                  }}
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                >
                  <span>{lang.name}</span>
                  {selectedLanguage === lang.id && (
                    <Check className="w-4 h-4" style={{ color: lang.color }} />
                  )}
                </motion.button>
              ))}
            </div>

            <div className="mt-6 p-4 rounded-xl bg-[var(--input-background)]">
              <div className="text-xs text-[var(--muted-foreground)] mb-2">Target Language</div>
              <div className="flex items-center gap-2">
                <div className="w-2 h-2 rounded-full bg-[var(--neon-emerald)]"></div>
                <span className="text-sm">Python 3.12+</span>
              </div>
            </div>
          </motion.div>

          {/* Code paste area */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            whileInView={{ opacity: 1, y: 0 }}
            viewport={{ once: true }}
            transition={{ delay: 0.2 }}
            className="lg:col-span-2 flex flex-col gap-4"
          >
            {!submitted ? (
              <div className="glass rounded-2xl overflow-hidden flex flex-col" style={{ minHeight: 400 }}>
                {/* Editor toolbar */}
                <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--border)]">
                  <div className="flex items-center gap-2">
                    <div className="w-3 h-3 rounded-full bg-red-500/70"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-500/70"></div>
                    <div className="w-3 h-3 rounded-full bg-green-500/70"></div>
                    <span
                      className="ml-3 text-xs px-2 py-0.5 rounded-full"
                      style={{
                        color: activeLang.color,
                        background: `${activeLang.color}18`,
                        border: `1px solid ${activeLang.color}40`,
                      }}
                    >
                      {activeLang.name}
                    </span>
                  </div>

                  <motion.button
                    onClick={handlePaste}
                    className="flex items-center gap-2 px-3 py-1.5 rounded-lg text-xs bg-[var(--input-background)] hover:bg-[var(--muted)] transition-colors"
                    whileHover={{ scale: 1.04 }}
                    whileTap={{ scale: 0.96 }}
                    style={{ color: "var(--neon-blue)" }}
                  >
                    <ClipboardPaste className="w-3.5 h-3.5" />
                    Paste from clipboard
                  </motion.button>
                </div>

                {/* Textarea */}
                <textarea
                  className="flex-1 w-full bg-transparent resize-none outline-none font-mono text-sm p-4 text-[var(--foreground)] placeholder:text-[var(--muted-foreground)]"
                  style={{ minHeight: 300 }}
                  placeholder={placeholders[selectedLanguage]}
                  value={code}
                  onChange={(e) => setCode(e.target.value)}
                  spellCheck={false}
                />

                {/* Footer */}
                <div className="flex items-center justify-between px-4 py-3 border-t border-[var(--border)]">
                  <span className="text-xs text-[var(--muted-foreground)]">
                    {code.trim() ? `${code.split("\n").length} lines` : "Paste or type your code above"}
                  </span>
                  <motion.button
                    onClick={handleSubmit}
                    disabled={!code.trim()}
                    className="flex items-center gap-2 px-5 py-2 rounded-xl text-sm font-medium transition-all disabled:opacity-30 disabled:cursor-not-allowed"
                    style={{
                      background: code.trim()
                        ? "linear-gradient(135deg, var(--neon-blue), var(--neon-purple))"
                        : "var(--input-background)",
                    }}
                    whileHover={code.trim() ? { scale: 1.04 } : {}}
                    whileTap={code.trim() ? { scale: 0.96 } : {}}
                  >
                    <Sparkles className="w-4 h-4" />
                    Start Modernization
                  </motion.button>
                </div>
              </div>
            ) : (
              <motion.div
                initial={{ scale: 0.95, opacity: 0 }}
                animate={{ scale: 1, opacity: 1 }}
                className="glass rounded-2xl p-8 flex flex-col items-center justify-center text-center"
                style={{ minHeight: 400 }}
              >
                <div
                  className="w-20 h-20 mx-auto mb-6 rounded-2xl glass flex items-center justify-center"
                  style={{ boxShadow: "0 0 24px var(--neon-emerald)40" }}
                >
                  <Check className="w-10 h-10" style={{ color: "var(--neon-emerald)" }} />
                </div>
                <h3 className="mb-2">Code submitted successfully</h3>
                <p className="text-[var(--muted-foreground)] mb-2">
                  {code.split("\n").length} lines of {activeLang.name} queued for modernization
                </p>
                <p className="text-xs text-[var(--muted-foreground)] mb-8">
                  The multi-agent pipeline is now analyzing your code
                </p>
                <motion.button
                  onClick={handleReset}
                  className="flex items-center gap-2 text-sm text-[var(--muted-foreground)] hover:text-[var(--foreground)] transition-colors"
                  whileHover={{ scale: 1.04 }}
                >
                  <X className="w-4 h-4" />
                  Clear and start over
                </motion.button>
              </motion.div>
            )}
          </motion.div>
        </div>
      </div>
    </div>
  );
}
