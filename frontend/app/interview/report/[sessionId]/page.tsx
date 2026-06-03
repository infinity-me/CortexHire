"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { motion } from "framer-motion";
import {
  Trophy, TrendingUp, AlertTriangle, CheckCircle,
  BarChart2, Eye, Activity, Shield, MessageSquare,
  Printer, Video, ChevronDown, ChevronUp
} from "lucide-react";
import Link from "next/link";
import { interviewApi } from "@/lib/api";
import type { InterviewReport } from "@/lib/types";

// ─── Score Ring ───────────────────────────────────────────────

function ScoreRing({ score, size = 120 }: { score: number; size?: number }) {
  const radius = (size - 16) / 2;
  const circ = 2 * Math.PI * radius;
  const filled = (score / 100) * circ;
  const color = score >= 70 ? "#10b981" : score >= 50 ? "#f59e0b" : "#f43f5e";

  return (
    <div style={{ position: "relative", width: size, height: size }}>
      <svg width={size} height={size} style={{ transform: "rotate(-90deg)" }}>
        <circle cx={size / 2} cy={size / 2} r={radius} fill="none" stroke="var(--bg-elevated)" strokeWidth={8} />
        <motion.circle
          cx={size / 2} cy={size / 2} r={radius}
          fill="none" stroke={color} strokeWidth={8}
          strokeLinecap="round"
          strokeDasharray={circ}
          initial={{ strokeDashoffset: circ }}
          animate={{ strokeDashoffset: circ - filled }}
          transition={{ duration: 1.5, ease: "easeOut" }}
        />
      </svg>
      <div style={{
        position: "absolute", inset: 0, display: "flex", flexDirection: "column",
        alignItems: "center", justifyContent: "center",
      }}>
        <motion.div
          initial={{ opacity: 0, scale: 0.5 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 0.5 }}
          style={{ fontSize: size * 0.28, fontWeight: 900, color, fontFamily: "'Space Grotesk', sans-serif", lineHeight: 1 }}
        >
          {score.toFixed(0)}
        </motion.div>
        <div style={{ fontSize: size * 0.11, color: "var(--text-muted)", fontWeight: 600 }}>/100</div>
      </div>
    </div>
  );
}

// ─── Dimension Bar ────────────────────────────────────────────

function DimensionBar({ label, value, weight, color, icon: Icon }: {
  label: string; value: number; weight: number; color: string; icon: React.ElementType;
}) {
  const scoreColor = value >= 70 ? "#10b981" : value >= 50 ? "#f59e0b" : "#f43f5e";
  return (
    <div style={{ marginBottom: 16 }}>
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 6 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Icon size={14} color={color} />
          <span style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>{label}</span>
          <span style={{ fontSize: 10, color: "var(--text-muted)", background: "var(--bg-elevated)", padding: "1px 6px", borderRadius: 10 }}>
            {weight}% weight
          </span>
        </div>
        <span style={{ fontSize: 18, fontWeight: 800, color: scoreColor, fontFamily: "'Space Grotesk', sans-serif" }}>
          {value.toFixed(0)}
        </span>
      </div>
      <div style={{ height: 8, borderRadius: 4, background: "var(--bg-elevated)", overflow: "hidden" }}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          style={{ height: "100%", borderRadius: 4, background: `linear-gradient(90deg, ${color}, ${scoreColor})` }}
        />
      </div>
    </div>
  );
}

// ─── Verdict Badge ────────────────────────────────────────────

const VERDICT_CONFIG: Record<string, { label: string; color: string; bg: string; icon: string }> = {
  strong_hire: { label: "Strong Hire", color: "#10b981", bg: "rgba(16,185,129,0.15)", icon: "🏆" },
  hire: { label: "Hire", color: "#06b6d4", bg: "rgba(6,182,212,0.15)", icon: "✅" },
  maybe: { label: "Maybe", color: "#f59e0b", bg: "rgba(245,158,11,0.15)", icon: "🤔" },
  no_hire: { label: "No Hire", color: "#f43f5e", bg: "rgba(244,63,94,0.15)", icon: "❌" },
  strong_no_hire: { label: "Strong No Hire", color: "#f43f5e", bg: "rgba(244,63,94,0.2)", icon: "🚫" },
};

// ─── Q&A Detail Row ───────────────────────────────────────────

function QARow({ qa, index }: { qa: InterviewReport["per_question"][0]; index: number }) {
  const [open, setOpen] = useState(false);
  const score = qa.answer_quality ?? 0;
  const scoreColor = score >= 70 ? "#10b981" : score >= 50 ? "#f59e0b" : "#f43f5e";

  return (
    <div style={{ borderBottom: "1px solid var(--border-subtle)", paddingBottom: 12, marginBottom: 12 }}>
      <div
        style={{ display: "flex", gap: 12, alignItems: "flex-start", cursor: "pointer" }}
        onClick={() => setOpen(o => !o)}
      >
        <div style={{
          width: 28, height: 28, borderRadius: "50%", flexShrink: 0,
          background: `${scoreColor}20`, border: `2px solid ${scoreColor}`,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontSize: 11, fontWeight: 800, color: scoreColor,
        }}>
          {index + 1}
        </div>
        <div style={{ flex: 1 }}>
          <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)", lineHeight: 1.4, marginBottom: 4 }}>
            {qa.question_text}
          </div>
          <div style={{ display: "flex", gap: 10, fontSize: 11, color: "var(--text-muted)" }}>
            <span>Quality: <strong style={{ color: scoreColor }}>{(qa.answer_quality ?? 0).toFixed(0)}</strong></span>
            <span>Comm: <strong style={{ color: "var(--text-secondary)" }}>{(qa.communication ?? 0).toFixed(0)}</strong></span>
            <span>Posture: <strong style={{ color: "var(--text-secondary)" }}>{(qa.posture ?? 0).toFixed(0)}</strong></span>
          </div>
        </div>
        <div style={{ color: "var(--text-muted)" }}>
          {open ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
        </div>
      </div>

      {open && (
        <motion.div
          initial={{ opacity: 0, height: 0 }}
          animate={{ opacity: 1, height: "auto" }}
          style={{ marginTop: 12, marginLeft: 40 }}
        >
          {qa.transcript && (
            <div style={{
              padding: "10px 14px", borderRadius: 10, marginBottom: 10,
              background: "var(--bg-elevated)", border: "1px solid var(--border-subtle)",
              fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.6,
              fontStyle: "italic",
            }}>
              &ldquo;{qa.transcript}&rdquo;
            </div>
          )}
          {qa.feedback?.strength && (
            <div style={{ display: "flex", gap: 6, marginBottom: 6, fontSize: 12 }}>
              <CheckCircle size={13} color="#10b981" style={{ flexShrink: 0, marginTop: 1 }} />
              <span style={{ color: "var(--text-secondary)" }}>{qa.feedback.strength}</span>
            </div>
          )}
          {qa.feedback?.weakness && (
            <div style={{ display: "flex", gap: 6, marginBottom: 6, fontSize: 12 }}>
              <AlertTriangle size={13} color="#f59e0b" style={{ flexShrink: 0, marginTop: 1 }} />
              <span style={{ color: "var(--text-secondary)" }}>{qa.feedback.weakness}</span>
            </div>
          )}
          {qa.feedback?.overall_comment && (
            <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 8, lineHeight: 1.5 }}>
              {qa.feedback.overall_comment}
            </div>
          )}
        </motion.div>
      )}
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────

export default function InterviewReportPage() {
  const { sessionId } = useParams<{ sessionId: string }>();
  const [report, setReport] = useState<InterviewReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    // Try fetching the report; it may already exist from the session page
    const fetchReport = async () => {
      try {
        const data = await interviewApi.getReport(sessionId);
        setReport(data);
      } catch (e) {
        setError("Could not load report. The interview may not have completed yet.");
      } finally {
        setLoading(false);
      }
    };
    fetchReport();
  }, [sessionId]);

  if (loading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: "60vh", flexDirection: "column", gap: 16 }}>
        <div style={{ width: 52, height: 52, border: "3px solid rgba(124,58,237,0.3)", borderTopColor: "#7c3aed", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
        <div style={{ color: "var(--text-muted)" }}>Generating AI interview report...</div>
        <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
      </div>
    );
  }

  if (error || !report) {
    return (
      <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: "50vh", gap: 12 }}>
        <AlertTriangle size={40} color="#f59e0b" />
        <div style={{ color: "var(--text-secondary)", textAlign: "center" }}>{error || "Report not found"}</div>
        <Link href="/interview" style={{ color: "#a78bfa", fontSize: 13 }}>← Back to Interview Setup</Link>
      </div>
    );
  }

  const verdict = VERDICT_CONFIG[report.ai_summary?.verdict] || VERDICT_CONFIG.maybe;

  return (
    <div style={{ maxWidth: 900 }}>
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 28 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
              <div style={{
                width: 40, height: 40, borderRadius: 12,
                background: "linear-gradient(135deg, #f43f5e, #f59e0b)",
                display: "flex", alignItems: "center", justifyContent: "center",
              }}>
                <Video size={18} color="white" />
              </div>
              <div>
                <h1 style={{ fontSize: 22, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif" }}>
                  Interview Report
                </h1>
                <div style={{ fontSize: 13, color: "var(--text-muted)" }}>
                  {report.candidate_name} · {report.job_title} at {report.company}
                </div>
              </div>
            </div>
          </div>
          <div style={{ display: "flex", gap: 8 }}>
            <button
              onClick={() => window.print()}
              style={{
                padding: "8px 14px", borderRadius: 8,
                background: "var(--bg-elevated)", border: "1px solid var(--border-default)",
                cursor: "pointer", color: "var(--text-secondary)", fontSize: 13,
                display: "flex", alignItems: "center", gap: 6,
              }}
            >
              <Printer size={13} /> Export PDF
            </button>
            <Link href="/interview" style={{ textDecoration: "none" }}>
              <div style={{
                padding: "8px 14px", borderRadius: 8,
                background: "rgba(124,58,237,0.15)", border: "1px solid rgba(124,58,237,0.25)",
                cursor: "pointer", color: "#a78bfa", fontSize: 13,
                display: "flex", alignItems: "center", gap: 6,
              }}>
                <Video size={13} /> New Interview
              </div>
            </Link>
          </div>
        </div>
      </motion.div>

      {/* Hero: Score + Verdict */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
        className="glass-card"
        style={{
          padding: 28, marginBottom: 20,
          background: "linear-gradient(135deg, rgba(26,32,53,0.9), rgba(22,27,39,0.95))",
          display: "flex", gap: 28, alignItems: "center",
        }}
      >
        <ScoreRing score={report.total_score} size={130} />

        <div style={{ flex: 1 }}>
          {/* Verdict */}
          <div style={{
            display: "inline-flex", alignItems: "center", gap: 8, padding: "6px 14px",
            borderRadius: 20, marginBottom: 12,
            background: verdict.bg, border: `1px solid ${verdict.color}40`,
          }}>
            <span style={{ fontSize: 16 }}>{verdict.icon}</span>
            <span style={{ fontSize: 14, fontWeight: 800, color: verdict.color }}>{verdict.label}</span>
          </div>

          <div style={{ fontSize: 18, fontWeight: 700, marginBottom: 8, lineHeight: 1.4 }}>
            {report.ai_summary?.headline || "Interview completed"}
          </div>
          <div style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.6 }}>
            {report.ai_summary?.recommendation}
          </div>
        </div>
      </motion.div>

      <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(200px, 1fr))", gap: 20, marginBottom: 20 }}>
        {/* Score Breakdown */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.2 }}
          className="glass-card"
          style={{ padding: 24 }}
        >
          <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-muted)", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 18 }}>
            Score Breakdown
          </div>
          <DimensionBar label="Answer Quality" value={report.scores.answer_quality} weight={40} color="#7c3aed" icon={MessageSquare} />
          <DimensionBar label="Communication" value={report.scores.communication} weight={15} color="#06b6d4" icon={BarChart2} />
          <DimensionBar label="Posture" value={report.scores.posture} weight={20} color="#10b981" icon={Activity} />
          <DimensionBar label="Engagement" value={report.scores.engagement} weight={15} color="#f59e0b" icon={Eye} />
          <DimensionBar label="Confidence" value={report.scores.confidence} weight={10} color="#f43f5e" icon={Shield} />
        </motion.div>

        {/* AI Summary */}
        <motion.div
          initial={{ opacity: 0, x: 20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.3 }}
          style={{ display: "flex", flexDirection: "column", gap: 16 }}
        >
          {/* Strengths */}
          {report.ai_summary?.strengths?.length > 0 && (
            <div className="glass-card" style={{ padding: 20, background: "rgba(16,185,129,0.07)", border: "1px solid rgba(16,185,129,0.2)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                <TrendingUp size={14} color="#10b981" />
                <span style={{ fontSize: 12, fontWeight: 700, color: "#10b981", letterSpacing: "0.06em", textTransform: "uppercase" }}>Strengths</span>
              </div>
              {report.ai_summary.strengths.map((s, i) => (
                <div key={i} style={{ display: "flex", gap: 8, marginBottom: 6, fontSize: 13, color: "var(--text-secondary)" }}>
                  <CheckCircle size={13} color="#10b981" style={{ flexShrink: 0, marginTop: 2 }} />
                  {s}
                </div>
              ))}
            </div>
          )}

          {/* Concerns */}
          {report.ai_summary?.concerns?.length > 0 && (
            <div className="glass-card" style={{ padding: 20, background: "rgba(244,63,94,0.07)", border: "1px solid rgba(244,63,94,0.2)" }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                <AlertTriangle size={14} color="#f43f5e" />
                <span style={{ fontSize: 12, fontWeight: 700, color: "#f43f5e", letterSpacing: "0.06em", textTransform: "uppercase" }}>Concerns</span>
              </div>
              {report.ai_summary.concerns.map((c, i) => (
                <div key={i} style={{ display: "flex", gap: 8, marginBottom: 6, fontSize: 13, color: "var(--text-secondary)" }}>
                  <AlertTriangle size={13} color="#f43f5e" style={{ flexShrink: 0, marginTop: 2 }} />
                  {c}
                </div>
              ))}
            </div>
          )}

          {/* Body Language */}
          {report.ai_summary?.body_language_summary && (
            <div className="glass-card" style={{ padding: 20 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
                <Eye size={14} color="#06b6d4" />
                <span style={{ fontSize: 12, fontWeight: 700, color: "#06b6d4", letterSpacing: "0.06em", textTransform: "uppercase" }}>Body Language</span>
              </div>
              <div style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.6 }}>
                {report.ai_summary.body_language_summary}
              </div>
            </div>
          )}
        </motion.div>
      </div>

      {/* Per-Question Breakdown */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4 }}
        className="glass-card"
        style={{ padding: 24 }}
      >
        <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-muted)", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 20 }}>
          Question-by-Question Analysis
        </div>
        {report.per_question.map((qa, i) => (
          <QARow key={i} qa={qa} index={i} />
        ))}
      </motion.div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @media print {
          nav, aside { display: none !important; }
          .glass-card { break-inside: avoid; }
        }
      `}</style>
    </div>
  );
}
