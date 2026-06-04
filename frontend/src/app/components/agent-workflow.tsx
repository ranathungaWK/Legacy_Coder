import { motion } from "motion/react";
import { Brain, Code, FlaskConical, CheckCircle2, ArrowRight } from "lucide-react";
import { PipelineStage } from "../App";

interface Agent {
  id: string;
  name: string;
  icon: React.ReactNode;
  color: string;
  status: "idle" | "active" | "complete" | "error";
  description: string;
}

interface AgentWorkflowProps {
  stages: PipelineStage[];
}

export function AgentWorkflow({ stages }: AgentWorkflowProps) {
  const getAgentStatus = (id: string): "idle" | "active" | "complete" | "error" => {
    const stage = stages.find(s => s.id === id);
    if (!stage) return "idle";
    if (stage.status === "running") return "active";
    if (stage.status === "complete") return "complete";
    if (stage.status === "error") return "error";
    return "idle";
  };

  const agents: Agent[] = [
    {
      id: "comprehension",
      name: "Comprehension Agent",
      icon: <Brain className="w-6 h-6" />,
      color: "var(--neon-blue)",
      status: getAgentStatus("comprehension"),
      description: "Analyzes legacy code structure and logic",
    },
    {
      id: "modernization",
      name: "Modernization Agent",
      icon: <Code className="w-6 h-6" />,
      color: "var(--neon-purple)",
      status: getAgentStatus("modernization"),
      description: "Transforms code to modern Python patterns",
    },
    {
      id: "testing",
      name: "Testing Agent",
      icon: <FlaskConical className="w-6 h-6" />,
      color: "var(--neon-emerald)",
      status: getAgentStatus("testing"),
      description: "Generates comprehensive pytest test suites",
    },
    {
      id: "verification",
      name: "Verification Agent",
      icon: <CheckCircle2 className="w-6 h-6" />,
      color: "#f59e0b",
      status: getAgentStatus("verification"),
      description: "Docker-based validation and compatibility checks",
    },
  ];

  return (
    <div className="py-20 px-6">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="text-center mb-16"
        >
          <h2 className="mb-4">Intelligent Multi-Agent Pipeline</h2>
          <p className="text-[var(--muted-foreground)] max-w-2xl mx-auto">
            Four specialized AI agents work in orchestrated sequence to ensure accurate, tested, and production-ready code transformation
          </p>
        </motion.div>

        <div className="relative">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {agents.map((agent, index) => (
              <motion.div
                key={agent.id}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: index * 0.2 }}
                className="relative"
              >
                <div
                  className={`glass rounded-2xl p-6 h-full transition-all duration-500 ${
                    agent.status === "active" ? "scale-105" : ""
                  }`}
                  style={{
                    boxShadow:
                      agent.status === "active"
                        ? `0 0 30px ${agent.color}40, 0 0 60px ${agent.color}20`
                        : undefined,
                    borderColor: agent.status === "active" ? agent.color : undefined,
                  }}
                >
                  <motion.div
                    className="flex items-center justify-center w-14 h-14 rounded-xl mb-4"
                    style={{
                      background: `${agent.color}20`,
                      color: agent.color,
                    }}
                    animate={
                      agent.status === "active"
                        ? {
                            scale: [1, 1.1, 1],
                            rotate: [0, 5, -5, 0],
                          }
                        : {}
                    }
                    transition={{
                      duration: 2,
                      repeat: agent.status === "active" ? Infinity : 0,
                    }}
                  >
                    {agent.icon}
                  </motion.div>

                  <h3 className="mb-2">{agent.name}</h3>
                  <p className="text-sm text-[var(--muted-foreground)]">{agent.description}</p>

                  <div className="mt-4 flex items-center gap-2">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        agent.status === "active"
                          ? "animate-pulse"
                          : agent.status === "complete"
                          ? ""
                          : "opacity-30"
                      }`}
                      style={{
                        backgroundColor:
                          agent.status === "complete"
                            ? "var(--neon-emerald)"
                            : agent.status === "active"
                            ? agent.color
                            : "var(--muted-foreground)",
                      }}
                    />
                    <span className="text-xs text-[var(--muted-foreground)]">
                      {agent.status === "active"
                        ? "Processing..."
                        : agent.status === "complete"
                        ? "Complete"
                        : "Pending"}
                    </span>
                  </div>

                  {agent.status === "active" && (
                    <motion.div
                      className="absolute inset-0 rounded-2xl pointer-events-none"
                      style={{
                        border: `1px solid ${agent.color}`,
                      }}
                      animate={{
                        opacity: [0.5, 1, 0.5],
                      }}
                      transition={{
                        duration: 2,
                        repeat: Infinity,
                      }}
                    />
                  )}
                </div>

                {index < agents.length - 1 && (
                  <div className="hidden lg:block absolute top-1/2 -right-3 transform -translate-y-1/2 z-10">
                    <motion.div
                      animate={{
                        x: [0, 5, 0],
                      }}
                      transition={{
                        duration: 1.5,
                        repeat: Infinity,
                      }}
                    >
                      <ArrowRight className="w-6 h-6 text-[var(--neon-blue)]" />
                    </motion.div>
                  </div>
                )}
              </motion.div>
            ))}
          </div>

          <svg className="absolute inset-0 w-full h-full pointer-events-none hidden lg:block" style={{ zIndex: -1 }}>
            <motion.path
              d="M 200 150 Q 400 100 600 150"
              stroke="var(--neon-blue)"
              strokeWidth="1"
              fill="none"
              strokeDasharray="5,5"
              initial={{ pathLength: 0, opacity: 0 }}
              animate={{ pathLength: 1, opacity: 0.3 }}
              transition={{ duration: 2, delay: 0.5 }}
            />
          </svg>
        </div>
      </div>
    </div>
  );
}
