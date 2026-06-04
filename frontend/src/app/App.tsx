import { useState, useRef, useEffect } from "react";
import { HeroSection } from "./components/hero-section";
import { AgentWorkflow } from "./components/agent-workflow";
import { CodeUpload } from "./components/code-upload";
import { PipelineProgress } from "./components/pipeline-progress";
import { CodeComparison } from "./components/code-comparison";
import { AIInsights } from "./components/ai-insights";
import { BackgroundEffects } from "./components/background-effects";

export interface PipelineStage {
  id: string;
  name: string;
  progress: number;
  status: "pending" | "running" | "complete" | "error";
  details: string;
}

const initialStages: PipelineStage[] = [
  {
    id: "comprehension",
    name: "Code Comprehension",
    progress: 0,
    status: "pending",
    details: "Queued",
  },
  {
    id: "modernization",
    name: "Code Transformation",
    progress: 0,
    status: "pending",
    details: "Waiting for comprehension",
  },
  {
    id: "testing",
    name: "Test Generation",
    progress: 0,
    status: "pending",
    details: "Waiting for transformation",
  },
  {
    id: "verification",
    name: "Verification",
    progress: 0,
    status: "pending",
    details: "Waiting for tests",
  },
];

export default function App() {
  const [selectedLanguage, setSelectedLanguage] = useState("cobol");
  const [code, setCode] = useState("");
  const [submitted, setSubmitted] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [overallProgress, setOverallProgress] = useState(0);
  const [stages, setStages] = useState<PipelineStage[]>(initialStages);
  const [result, setResult] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);
  const intervalRef = useRef<number | null>(null);

  useEffect(() => {
    return () => {
      if (intervalRef.current) window.clearInterval(intervalRef.current);
    };
  }, []);

  const handleStartModernization = async () => {
    if (!code.trim() || isProcessing) return;
    setIsProcessing(true);
    setSubmitted(true);
    setResult(null);
    setError(null);
    setOverallProgress(5);
    
    // Reset stages
    setStages([
      { id: "comprehension", name: "Code Comprehension", progress: 20, status: "running", details: "Analyzing code semantics..." },
      { id: "modernization", name: "Code Transformation", progress: 0, status: "pending", details: "Waiting for comprehension" },
      { id: "testing", name: "Test Generation", progress: 0, status: "pending", details: "Waiting for transformation" },
      { id: "verification", name: "Verification", progress: 0, status: "pending", details: "Waiting for tests" }
    ]);

    // Timers to simulate progress during execution
    const startTime = Date.now();
    if (intervalRef.current) window.clearInterval(intervalRef.current);
    intervalRef.current = window.setInterval(() => {
      const elapsed = (Date.now() - startTime) / 1000;
      
      setStages(prev => {
        const next = [...prev];
        
        // Comprehension: 0 - 3s
        if (elapsed < 3) {
          next[0].progress = Math.min(90, Math.floor(20 + elapsed * 20));
          setOverallProgress(Math.floor(5 + elapsed * 5)); // 5% -> 20%
        } 
        // Modernization: 3 - 7s
        else if (elapsed >= 3 && elapsed < 7) {
          if (next[0].status !== "complete") {
            next[0].status = "complete";
            next[0].progress = 100;
            next[0].details = "Comprehended logic successfully";
            next[1].status = "running";
            next[1].details = "Generating clean Python rewrite...";
          }
          next[1].progress = Math.min(90, Math.floor(10 + (elapsed - 3) * 20));
          setOverallProgress(Math.floor(20 + (elapsed - 3) * 8)); // 20% -> 52%
        }
        // Testing: 7 - 17s (Ollama is slow)
        else if (elapsed >= 7 && elapsed < 17) {
          if (next[1].status !== "complete") {
            next[1].status = "complete";
            next[1].progress = 100;
            next[1].details = "Transformed code structure successfully";
            next[2].status = "running";
            next[2].details = "Retrieving RAG patterns & generating pytest...";
          }
          next[2].progress = Math.min(90, Math.floor(10 + (elapsed - 7) * 8));
          setOverallProgress(Math.floor(52 + (elapsed - 7) * 3)); // 52% -> 82%
        }
        // Verification: 17s+
        else if (elapsed >= 17) {
          if (next[2].status !== "complete") {
            next[2].status = "complete";
            next[2].progress = 100;
            next[2].details = "Generated pytest suite successfully";
            next[3].status = "running";
            next[3].details = "Running tests in isolated Docker sandbox...";
          }
          next[3].progress = Math.min(90, Math.floor(10 + (elapsed - 17) * 4));
          setOverallProgress(Math.min(95, Math.floor(82 + (elapsed - 17) * 1))); // 82% -> 95%
        }
        
        return next;
      });
    }, 500);

    try {
      const mappedLang = selectedLanguage === "cpp" ? "c++" : selectedLanguage;
      const response = await fetch("http://localhost:8000/api/v1/modernize/", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        body: JSON.stringify({
          code: code,
          language: mappedLang
        })
      });

      if (!response.ok) {
        throw new Error(`Server returned status ${response.status}`);
      }

      const data = await response.json();
      if (intervalRef.current) window.clearInterval(intervalRef.current);

      // Successfully finished pipeline!
      setStages(prev => {
        const next = prev.map(stage => ({
          ...stage,
          status: "complete" as const,
          progress: 100
        }));
        next[0].details = "Comprehended logic successfully";
        next[1].details = "Transformed code structure successfully";
        next[2].details = "Generated pytest suite successfully";
        next[3].details = data.test_outcome?.execution_result?.success 
          ? "Tests verified successfully in Docker" 
          : "Verification complete (some tests failed or sandbox connection failed)";
        
        // Handle if syntax validation failed
        if (!data.syntax_valid) {
          next[2].status = "pending" as const;
          next[2].progress = 0;
          next[2].details = "Skipped due to syntax errors";
          next[3].status = "pending" as const;
          next[3].progress = 0;
          next[3].details = "Skipped due to syntax errors";
        }
        return next;
      });
      
      setOverallProgress(100);
      setResult(data);
      setIsProcessing(false);

    } catch (err: any) {
      if (intervalRef.current) window.clearInterval(intervalRef.current);
      setError(err.message || "An unexpected error occurred");
      
      // Update currently running stage to error
      setStages(prev => {
        return prev.map(stage => {
          if (stage.status === "running") {
            return {
              ...stage,
              status: "error" as const,
              details: `Failed: ${err.message || "Endpoint error"}`
            };
          }
          return stage;
        });
      });
      
      setIsProcessing(false);
    }
  };

  const handleReset = () => {
    if (intervalRef.current) window.clearInterval(intervalRef.current);
    setCode("");
    setSubmitted(false);
    setIsProcessing(false);
    setOverallProgress(0);
    setStages(initialStages);
    setResult(null);
    setError(null);
  };

  return (
    <div className="min-h-screen relative overflow-x-hidden dark">
      <BackgroundEffects />

      <div className="relative z-10">
        <HeroSection />
        <AgentWorkflow stages={stages} />
        <CodeUpload
          code={code}
          setCode={setCode}
          selectedLanguage={selectedLanguage}
          setSelectedLanguage={setSelectedLanguage}
          isProcessing={isProcessing}
          submitted={submitted}
          setSubmitted={setSubmitted}
          onSubmit={handleStartModernization}
          onReset={handleReset}
        />
        
        {submitted && (
          <PipelineProgress
            stages={stages}
            progress={overallProgress}
            isProcessing={isProcessing}
            error={error}
            onReset={handleReset}
          />
        )}

        {result && (
          <>
            <CodeComparison
              legacyCode={code}
              modernCode={result.rewrite.python_code}
              selectedLanguage={selectedLanguage}
            />
            <AIInsights
              explanation={result.explanation}
              rewrite={result.rewrite}
              syntaxValid={result.syntax_valid}
              syntaxError={result.syntax_error}
              testOutcome={result.test_outcome}
            />
          </>
        )}

        <footer className="py-12 px-6 border-t border-[var(--border)]">
          <div className="max-w-7xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full glass mb-4">
              <div className="w-2 h-2 rounded-full bg-[var(--neon-emerald)] animate-pulse"></div>
              <span className="text-sm text-[var(--muted-foreground)]">
                Production-grade AI modernization pipeline
              </span>
            </div>
            <p className="text-xs text-[var(--muted-foreground)]">
              LegacyCoder &copy; 2026 - Powered by multi-agent AI orchestration and RAG knowledge retrieval
            </p>
          </div>
        </footer>
      </div>
    </div>
  );
}