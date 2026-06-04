import { motion } from "motion/react";
import {
  TrendingUp,
  Clock,
  FileCode,
  Zap,
  BarChart3,
  Activity,
} from "lucide-react";
import { AreaChart, Area, XAxis, YAxis, ResponsiveContainer, Tooltip } from "recharts";

export function AnalyticsDashboard() {
  const stats = [
    {
      id: "processed",
      label: "Files Processed",
      value: "1,247",
      change: "+23%",
      icon: <FileCode className="w-5 h-5" />,
      color: "var(--neon-blue)",
    },
    {
      id: "time",
      label: "Avg Processing Time",
      value: "2.4s",
      change: "-45%",
      icon: <Clock className="w-5 h-5" />,
      color: "var(--neon-purple)",
    },
    {
      id: "success",
      label: "Success Rate",
      value: "98.7%",
      change: "+2.1%",
      icon: <TrendingUp className="w-5 h-5" />,
      color: "var(--neon-emerald)",
    },
    {
      id: "efficiency",
      label: "Performance Gain",
      value: "12.5x",
      change: "+8.2x",
      icon: <Zap className="w-5 h-5" />,
      color: "#f59e0b",
    },
  ];

  const chartData = [
    { id: "t1", time: "00:00", value: 45 },
    { id: "t2", time: "04:00", value: 52 },
    { id: "t3", time: "08:00", value: 89 },
    { id: "t4", time: "12:00", value: 124 },
    { id: "t5", time: "16:00", value: 98 },
    { id: "t6", time: "20:00", value: 71 },
  ];

  return (
    <div className="py-12 px-6">
      <div className="max-w-7xl mx-auto">
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="mb-8"
        >
          <h2 className="mb-2">Analytics Dashboard</h2>
          <p className="text-[var(--muted-foreground)]">
            Real-time pipeline metrics and performance tracking
          </p>
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          {stats.map((stat, index) => (
            <motion.div
              key={stat.id}
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              viewport={{ once: true }}
              transition={{ delay: index * 0.1 }}
              className="glass rounded-2xl p-6"
            >
              <div className="flex items-start justify-between mb-4">
                <div
                  className="w-10 h-10 rounded-xl flex items-center justify-center"
                  style={{
                    background: `${stat.color}20`,
                    color: stat.color,
                  }}
                >
                  {stat.icon}
                </div>
                <div
                  className="text-xs px-2 py-1 rounded-full"
                  style={{
                    background: `${stat.color}20`,
                    color: stat.color,
                  }}
                >
                  {stat.change}
                </div>
              </div>
              <div className="text-3xl mb-1" style={{ color: stat.color }}>
                {stat.value}
              </div>
              <div className="text-sm text-[var(--muted-foreground)]">{stat.label}</div>
            </motion.div>
          ))}
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="lg:col-span-2 glass rounded-2xl p-6"
          >
            <div className="flex items-center justify-between mb-6">
              <div className="flex items-center gap-2">
                <BarChart3 className="w-5 h-5 text-[var(--neon-blue)]" />
                <h3 className="text-sm">Processing Activity (24h)</h3>
              </div>
              <div className="text-xs text-[var(--muted-foreground)]">Live</div>
            </div>

            <ResponsiveContainer width="100%" height={200}>
              <AreaChart data={chartData}>
                <defs>
                  <linearGradient id="colorValue" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--neon-blue)" stopOpacity={0.3} />
                    <stop offset="95%" stopColor="var(--neon-blue)" stopOpacity={0} />
                  </linearGradient>
                </defs>
                <XAxis
                  dataKey="time"
                  stroke="var(--muted-foreground)"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <YAxis
                  stroke="var(--muted-foreground)"
                  fontSize={12}
                  tickLine={false}
                  axisLine={false}
                />
                <Tooltip
                  contentStyle={{
                    background: "var(--glass-bg)",
                    border: "1px solid var(--glass-border)",
                    borderRadius: "8px",
                    backdropFilter: "blur(12px)",
                  }}
                />
                <Area
                  type="monotone"
                  dataKey="value"
                  stroke="var(--neon-blue)"
                  strokeWidth={2}
                  fillOpacity={1}
                  fill="url(#colorValue)"
                  isAnimationActive={true}
                />
              </AreaChart>
            </ResponsiveContainer>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, x: 20 }}
            whileInView={{ opacity: 1, x: 0 }}
            viewport={{ once: true }}
            className="glass rounded-2xl p-6"
          >
            <div className="flex items-center gap-2 mb-6">
              <Activity className="w-5 h-5 text-[var(--neon-purple)]" />
              <h3 className="text-sm">Agent Activity</h3>
            </div>

            <div className="space-y-4">
              {[
                { name: "Comprehension", load: 78, color: "var(--neon-blue)" },
                { name: "Modernization", load: 92, color: "var(--neon-purple)" },
                { name: "Testing", load: 65, color: "var(--neon-emerald)" },
                { name: "Verification", load: 41, color: "#f59e0b" },
              ].map((agent, index) => (
                <div key={agent.name}>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-xs text-[var(--muted-foreground)]">
                      {agent.name}
                    </span>
                    <span className="text-xs" style={{ color: agent.color }}>
                      {agent.load}%
                    </span>
                  </div>
                  <div className="h-2 rounded-full bg-[var(--input-background)] overflow-hidden">
                    <motion.div
                      className="h-full"
                      style={{ background: agent.color }}
                      initial={{ width: 0 }}
                      whileInView={{ width: `${agent.load}%` }}
                      viewport={{ once: true }}
                      transition={{ duration: 1, delay: index * 0.1 }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  );
}
