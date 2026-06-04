import { motion } from "motion/react";
import { useState } from "react";
import {
  FileText,
  AlertCircle,
  CheckCircle2,
  FlaskConical,
  Activity,
  Copy,
} from "lucide-react";

interface AIInsightsProps {
  explanation: {
    purpose: string;
    inputs: { name?: string; source?: string; description: string; type: string }[];
    outputs: { name?: string; destination?: string; description: string; type: string }[];
    assumptions: string[];
    side_effects: string[];
    edge_cases: string[];
    confidence_level: string;
  };
  rewrite: {
    design_notes: string[];
    assumptions_made: string[];
    compatibility_notes: string[];
  };
  syntaxValid: boolean;
  syntaxError: string | null;
  testOutcome: {
    test_code: string;
    execution_result: {
      success: boolean;
      exit_code: number;
      stdout: string;
      stderr: string;
      timed_out: boolean;
    };
  } | null;
}

export function AIInsights({
  explanation,
  rewrite,
  syntaxValid,
  syntaxError,
  testOutcome,
}: AIInsightsProps) {
  const [copiedId, setCopiedId] = useState<string | null>(null);

  const handleCopy = (id: string, text: string) => {
    navigator.clipboard.writeText(text);
    setCopiedId(id);
    setTimeout(() => setCopiedId(null), 2000);
  };
  const formatExplanation = (exp: any) => {
    if (!exp) return "";
    const inputsStr = (exp.inputs || [])
      .map((i: any) => `• ${i.name || i.source || "Input"}: ${i.description} (${i.type})`)
      .join("\n");
    const outputsStr = (exp.outputs || [])
      .map((o: any) => `• ${o.name || o.destination || "Output"}: ${o.description} (${o.type})`)
      .join("\n");
    const assumptionsStr = (exp.assumptions || []).map((a: any) => `• ${a}`).join("\n");
    const sideEffectsStr = (exp.side_effects || []).map((s: any) => `• ${s}`).join("\n");
    const edgeCasesStr = (exp.edge_cases || []).map((e: any) => `• ${e}`).join("\n");

    return `Purpose:\n${exp.purpose}\n\nInputs:\n${inputsStr || "None"}\n\nOutputs:\n${outputsStr || "None"}\n\nAssumptions:\n${assumptionsStr || "None"}\n\nSide Effects:\n${sideEffectsStr || "None"}\n\nEdge Cases:\n${edgeCasesStr || "None"}\n\nConfidence Level: ${exp.confidence_level ? exp.confidence_level.toUpperCase() : "MEDIUM"}`;
  };

  const formatModernizationDetails = (rew: any) => {
    if (!rew) return "";
    const designNotesStr = (rew.design_notes || []).map((n: any) => `• ${n}`).join("\n");
    const assumptionsMadeStr = (rew.assumptions_made || []).map((a: any) => `• ${a}`).join("\n");
    const compatibilityNotesStr = (rew.compatibility_notes || []).map((c: any) => `• ${c}`).join("\n");

    return `Design Notes:\n${designNotesStr || "None"}\n\nAssumptions Made:\n${assumptionsMadeStr || "None"}\n\nCompatibility Notes:\n${compatibilityNotesStr || "None"}`;
  };

  const formatTests = (outcome: any) => {
    if (!outcome) return "No tests generated. (Either skipped due to syntax errors or pipeline failure.)";
    return outcome.test_code;
  };

  const formatVerification = (outcome: any, valid: boolean, error: string | null) => {
    if (!valid) {
      return `✗ Syntax validation failed!\n${error || "Code contains syntax errors. Skipped tests."}`;
    }
    if (!outcome || !outcome.execution_result) {
      return "Pending verification run...";
    }
    const res = outcome.execution_result;
    return `Status: ${res.success ? "✓ Passed" : "✗ Failed"}\nExit Code: ${res.exit_code}\nTimed Out: ${res.timed_out}\n\nStdout:\n${res.stdout || "(none)"}\n\nStderr:\n${res.stderr || "(none)"}`;
  };

  const insights = [
    {
      id: "explanation",
      title: "AI Code Explanation",
      icon: <FileText className="w-5 h-5" />,
      color: "var(--neon-blue)",
      content: formatExplanation(explanation),
    },
    {
      id: "assumptions",
      title: "Modernization Details",
      icon: <AlertCircle className="w-5 h-5" />,
      color: "var(--neon-purple)",
      content: formatModernizationDetails(rewrite),
    },
    {
      id: "tests",
      title: "Generated Test Suite",
      icon: <FlaskConical className="w-5 h-5" />,
      color: "var(--neon-emerald)",
      content: formatTests(testOutcome),
    },
    {
      id: "verification",
      title: "Docker Verification Results",
      icon: <CheckCircle2 className="w-5 h-5" />,
      color: "#10b981",
      content: formatVerification(testOutcome, syntaxValid, syntaxError),
    },
  ];

  return (
    <div className="py-12 px-6">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-12"
        >
          <h2 className="mb-4">AI-Generated Insights</h2>
          <p className="text-[var(--muted-foreground)] max-w-2xl mx-auto">
            Comprehensive analysis, testing, and validation powered by multi-agent AI pipeline
          </p>
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {insights.map((insight, index) => (
            <motion.div
              key={insight.id}
              initial={{ opacity: 0, y: 30 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="glass rounded-2xl p-6 hover:scale-[1.02] transition-transform relative group"
            >
              <div className="absolute top-4 right-4 opacity-0 group-hover:opacity-100 transition-opacity">
                <button
                  onClick={() => handleCopy(insight.id, insight.content)}
                  className="p-2 bg-[var(--input-background)] hover:bg-[var(--border)] rounded-lg transition-colors"
                  title="Copy to clipboard"
                >
                  {copiedId === insight.id ? (
                    <CheckCircle2 className="w-4 h-4 text-green-500" />
                  ) : (
                    <Copy className="w-4 h-4 text-[var(--muted-foreground)]" />
                  )}
                </button>
              </div>

              <div className="flex items-center gap-3 mb-4">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center"
                  style={{
                    background: `${insight.color}20`,
                    color: insight.color,
                  }}
                >
                  {insight.icon}
                </div>
                <h3 className="text-sm">{insight.title}</h3>
              </div>

              <div className="bg-[var(--input-background)] rounded-xl p-4">
                <pre className="text-xs font-mono whitespace-pre-wrap text-[var(--muted-foreground)] leading-relaxed">
                  {insight.content}
                </pre>
              </div>

              <div className="mt-4 flex items-center gap-2">
                <Activity className="w-3 h-3" style={{ color: insight.color }} />
                <span className="text-xs text-[var(--muted-foreground)]">
                  Generated by {insight.title.split(" ")[0]} Agent
                </span>
              </div>
            </motion.div>
          ))}
        </div>
      </div>
    </div>
  );
}
