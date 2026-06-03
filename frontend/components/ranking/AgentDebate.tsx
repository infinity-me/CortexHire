"use client";

import { motion } from "framer-motion";
import type { AgentResult } from "@/lib/types";

interface Props {
  agentResults: AgentResult[];
}

const AGENT_CONFIG: Record<string, { emoji: string; color: string; bg: string; border: string }> = {
  "Technical Recruiter": {
    emoji: "⚙️", color: "#a78bfa",
    bg: "rgba(124,58,237,0.08)", border: "rgba(124,58,237,0.25)"
  },
  "Hiring Manager": {
    emoji: "📋", color: "#06b6d4",
    bg: "rgba(6,182,212,0.08)", border: "rgba(6,182,212,0.25)"
  },
  "Organizational Psychologist": {
    emoji: "🧠", color: "#10b981",
    bg: "rgba(16,185,129,0.08)", border: "rgba(16,185,129,0.25)"
  },
  "Diversity & Bias Corrector": {
    emoji: "⚖️", color: "#f59e0b",
    bg: "rgba(245,158,11,0.08)", border: "rgba(245,158,11,0.25)"
  },
  "Future Potential Predictor": {
    emoji: "🚀", color: "#f43f5e",
    bg: "rgba(244,63,94,0.08)", border: "rgba(244,63,94,0.25)"
  },
};

function AgentCard({ agent, index }: { agent: AgentResult; index: number }) {
  const config = AGENT_CONFIG[agent.agent] || {
    emoji: "🤖", color: "#94a3b8",
    bg: "rgba(148,163,184,0.08)", border: "rgba(148,163,184,0.25)"
  };

  const score = agent.score || 0;
  const confidence = agent.confidence || 0;

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.1 }}
      style={{
        padding: 18, borderRadius: 14,
        background: config.bg,
        border: `1px solid ${config.border}`,
        marginBottom: 12,
      }}
    >
      {/* Header */}
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 12 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <span style={{ fontSize: 20 }}>{config.emoji}</span>
          <div>
            <div style={{ fontWeight: 700, fontSize: 13, color: config.color }}>{agent.agent}</div>
            <div style={{ fontSize: 10, color: "var(--text-muted)" }}>
              Confidence: {(confidence * 100).toFixed(0)}%
            </div>
          </div>
        </div>
        {/* Score ring */}
        <div style={{
          width: 56, height: 56, borderRadius: "50%",
          background: `conic-gradient(${config.color} ${score * 3.6}deg, rgba(255,255,255,0.05) 0deg)`,
          display: "flex", alignItems: "center", justifyContent: "center",
          position: "relative"
        }}>
          <div style={{
            width: 44, height: 44, borderRadius: "50%",
            background: "var(--bg-card)",
            display: "flex", alignItems: "center", justifyContent: "center",
            fontFamily: "'Space Grotesk', sans-serif",
            fontWeight: 800, fontSize: 14, color: config.color
          }}>
            {score.toFixed(0)}
          </div>
        </div>
      </div>

      {/* Reasoning */}
      <p style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.6, marginBottom: 12 }}>
        {agent.reasoning}
      </p>

      {/* Key signals */}
      {agent.key_signals?.length > 0 && (
        <div style={{ marginBottom: 8 }}>
          <div style={{ fontSize: 9, fontWeight: 700, color: config.color, marginBottom: 6, letterSpacing: "0.06em" }}>
            KEY SIGNALS
          </div>
          {agent.key_signals.map((s, i) => (
            <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 6, marginBottom: 4 }}>
              <div style={{ width: 4, height: 4, borderRadius: "50%", background: config.color, marginTop: 5, flexShrink: 0 }} />
              <span style={{ fontSize: 11, color: "var(--text-secondary)" }}>{s}</span>
            </div>
          ))}
        </div>
      )}

      {/* Risks */}
      {agent.risks?.length > 0 && (
        <div>
          <div style={{ fontSize: 9, fontWeight: 700, color: "#f43f5e", marginBottom: 6, letterSpacing: "0.06em" }}>RISKS</div>
          {agent.risks.map((r, i) => (
            <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 6, marginBottom: 4 }}>
              <div style={{ width: 4, height: 4, borderRadius: "50%", background: "#f43f5e", marginTop: 5, flexShrink: 0 }} />
              <span style={{ fontSize: 11, color: "#f87171" }}>{r}</span>
            </div>
          ))}
        </div>
      )}

      {/* Future predictor extras */}
      {agent.predicted_role_in_2_years && (
        <div style={{
          marginTop: 10, padding: "8px 12px", borderRadius: 8,
          background: "rgba(244,63,94,0.08)", border: "1px solid rgba(244,63,94,0.2)"
        }}>
          <div style={{ fontSize: 9, color: "#f43f5e", fontWeight: 700, marginBottom: 3 }}>2-YEAR PREDICTION</div>
          <div style={{ fontSize: 12, color: "var(--text-primary)" }}>{agent.predicted_role_in_2_years}</div>
        </div>
      )}
    </motion.div>
  );
}

export default function AgentDebate({ agentResults }: Props) {
  return (
    <div>
      <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-muted)", marginBottom: 16, letterSpacing: "0.08em" }}>
        5-AGENT RECRUITER DEBATE
      </div>
      {agentResults.map((agent, i) => (
        <AgentCard key={agent.agent} agent={agent} index={i} />
      ))}
    </div>
  );
}
