"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import { Video, User, Mail, Briefcase, ChevronRight, Clock, AlertCircle, CheckCircle, PenLine } from "lucide-react";
import { jobsApi, interviewApi } from "@/lib/api";
import type { Job, InterviewSessionSummary } from "@/lib/types";

export default function InterviewSetupPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [sessions, setSessions] = useState<InterviewSessionSummary[]>([]);
  const [loading, setLoading] = useState(true);
  const [starting, setStarting] = useState(false);

  // Form state
  const [selectedJobId, setSelectedJobId] = useState("");
  const [candidateName, setCandidateName] = useState("");
  const [candidateEmail, setCandidateEmail] = useState("");
  const [numQuestions, setNumQuestions] = useState(6);
  const [error, setError] = useState("");

  // Custom role state
  const [useCustomRole, setUseCustomRole] = useState(false);
  const [customTitle, setCustomTitle] = useState("");
  const [customCompany, setCustomCompany] = useState("");
  const [customDescription, setCustomDescription] = useState("");

  useEffect(() => {
    Promise.all([
      jobsApi.list().catch(() => []),
      interviewApi.listSessions().catch(() => []),
    ]).then(([j, s]) => {
      setJobs(j);
      setSessions(s.slice(0, 5));
      if (j.length > 0) setSelectedJobId(j[0].id);
      setLoading(false);
    });
  }, []);

  const selectedJob = jobs.find(j => j.id === selectedJobId);

  async function handleStart() {
    if (useCustomRole) {
      if (!customTitle.trim()) { setError("Please enter a job role title"); return; }
    } else {
      if (!selectedJobId) { setError("Please select a job"); return; }
    }
    if (!candidateName.trim()) { setError("Please enter the candidate name"); return; }
    setError("");
    setStarting(true);
    try {
      const session = useCustomRole
        ? await interviewApi.start(
            "__custom__",
            candidateName.trim(),
            candidateEmail || undefined,
            numQuestions,
            customTitle.trim(),
            customCompany.trim() || undefined,
            customDescription.trim() || undefined,
          )
        : await interviewApi.start(selectedJobId, candidateName.trim(), candidateEmail || undefined, numQuestions);
      sessionStorage.setItem(`interview_${session.session_id}`, JSON.stringify(session));
      router.push(`/interview/session/${session.session_id}`);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Failed to start interview";
      setError(msg);
      setStarting(false);
    }
  }

  const verdictColor = (verdict: string) => {
    if (verdict === "strong_hire" || verdict === "hire") return "#10b981";
    if (verdict === "maybe") return "#f59e0b";
    return "#f43f5e";
  };

  return (
    <div style={{ maxWidth: 900 }}>
      {/* Header */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        style={{ marginBottom: 36 }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
          <div style={{
            width: 48, height: 48, borderRadius: 14,
            background: "linear-gradient(135deg, #f43f5e, #f59e0b)",
            display: "flex", alignItems: "center", justifyContent: "center",
            boxShadow: "0 0 24px rgba(244,63,94,0.4)",
          }}>
            <Video size={22} color="white" />
          </div>
          <div>
            <h1 style={{ fontSize: 28, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif" }}>
              Live Interview Panel
            </h1>
            <p style={{ fontSize: 14, color: "var(--text-muted)", marginTop: 2 }}>
              AI-generated questions · Real-time posture analysis · Honest scoring
            </p>
          </div>
        </div>
      </motion.div>

      <div style={{ display: "grid", gridTemplateColumns: "1fr 360px", gap: 24 }}>
        {/* Setup Form */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          transition={{ delay: 0.1 }}
          className="glass-card"
          style={{ padding: 28 }}
        >
          <div style={{ fontSize: 13, fontWeight: 700, color: "var(--text-muted)", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 20 }}>
            Interview Setup
          </div>

          {/* Job Selector */}
          <div style={{ marginBottom: 20 }}>
            <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
              <label style={{ fontSize: 13, fontWeight: 600, color: "var(--text-secondary)" }}>
                <Briefcase size={14} style={{ display: "inline", marginRight: 6, verticalAlign: "middle" }} />
                Job Role
              </label>
              <button
                type="button"
                onClick={() => { setUseCustomRole(v => !v); setError(""); }}
                style={{
                  fontSize: 11, fontWeight: 600, padding: "3px 10px", borderRadius: 20,
                  background: useCustomRole ? "rgba(124,58,237,0.2)" : "var(--bg-elevated)",
                  border: `1px solid ${useCustomRole ? "rgba(124,58,237,0.5)" : "var(--border-default)"}`,
                  color: useCustomRole ? "#a78bfa" : "var(--text-muted)",
                  cursor: "pointer", display: "flex", alignItems: "center", gap: 5,
                  transition: "all 0.2s ease",
                }}
              >
                <PenLine size={11} />
                {useCustomRole ? "Using custom role" : "Use custom role"}
              </button>
            </div>

            {loading ? (
              <div className="skeleton" style={{ height: 44, borderRadius: 10 }} />
            ) : useCustomRole ? (
              /* Custom role inputs */
              <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
                <input
                  id="custom-role-title"
                  type="text"
                  placeholder="e.g. Senior React Developer, Product Manager, Data Analyst..."
                  value={customTitle}
                  onChange={e => setCustomTitle(e.target.value)}
                  style={{
                    width: "100%", padding: "10px 14px",
                    background: "var(--bg-elevated)", border: "1px solid rgba(124,58,237,0.4)",
                    borderRadius: 10, color: "var(--text-primary)", fontSize: 14, outline: "none",
                    boxShadow: "0 0 0 3px rgba(124,58,237,0.08)",
                  }}
                />
                <input
                  id="custom-company"
                  type="text"
                  placeholder="Company name (optional)"
                  value={customCompany}
                  onChange={e => setCustomCompany(e.target.value)}
                  style={{
                    width: "100%", padding: "8px 14px",
                    background: "var(--bg-elevated)", border: "1px solid var(--border-default)",
                    borderRadius: 10, color: "var(--text-primary)", fontSize: 13, outline: "none",
                  }}
                />
                <textarea
                  id="custom-description"
                  placeholder="Job description / context (optional — helps AI generate better questions)"
                  value={customDescription}
                  onChange={e => setCustomDescription(e.target.value)}
                  rows={3}
                  style={{
                    width: "100%", padding: "8px 14px",
                    background: "var(--bg-elevated)", border: "1px solid var(--border-default)",
                    borderRadius: 10, color: "var(--text-primary)", fontSize: 12, outline: "none",
                    resize: "vertical", lineHeight: 1.5,
                  }}
                />
                <div style={{ fontSize: 11, color: "var(--text-muted)", display: "flex", alignItems: "center", gap: 5 }}>
                  <span style={{ color: "#a78bfa" }}>✦</span>
                  AI will generate questions tailored to your custom role
                </div>
              </div>
            ) : (
              /* Dropdown for seeded jobs */
              <select
                id="job-select"
                value={selectedJobId}
                onChange={e => setSelectedJobId(e.target.value)}
                style={{
                  width: "100%", padding: "10px 14px",
                  background: "var(--bg-elevated)", border: "1px solid var(--border-default)",
                  borderRadius: 10, color: "var(--text-primary)", fontSize: 14, outline: "none",
                  cursor: "pointer",
                }}
              >
                {jobs.map(j => (
                  <option key={j.id} value={j.id}>
                    {j.title} — {j.company}
                  </option>
                ))}
              </select>
            )}

            {!useCustomRole && selectedJob && (
              <div style={{ marginTop: 8, display: "flex", gap: 8 }}>
                <span style={{
                  fontSize: 11, fontWeight: 600, padding: "2px 8px", borderRadius: 20,
                  background: selectedJob.status === "ready" ? "rgba(16,185,129,0.15)" : "rgba(245,158,11,0.15)",
                  color: selectedJob.status === "ready" ? "#10b981" : "#f59e0b",
                  border: `1px solid ${selectedJob.status === "ready" ? "rgba(16,185,129,0.3)" : "rgba(245,158,11,0.3)"}`,
                }}>
                  {selectedJob.status === "ready" ? "✓ Role Genome Ready" : "Role Genome Pending"}
                </span>
              </div>
            )}
          </div>

          {/* Candidate Name */}
          <div style={{ marginBottom: 20 }}>
            <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 8, color: "var(--text-secondary)" }}>
              <User size={14} style={{ display: "inline", marginRight: 6, verticalAlign: "middle" }} />
              Candidate Name *
            </label>
            <input
              id="candidate-name"
              type="text"
              placeholder="e.g. Sarah Chen"
              value={candidateName}
              onChange={e => setCandidateName(e.target.value)}
              style={{
                width: "100%", padding: "10px 14px",
                background: "var(--bg-elevated)", border: "1px solid var(--border-default)",
                borderRadius: 10, color: "var(--text-primary)", fontSize: 14, outline: "none",
              }}
            />
          </div>

          {/* Email (optional) */}
          <div style={{ marginBottom: 20 }}>
            <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 8, color: "var(--text-secondary)" }}>
              <Mail size={14} style={{ display: "inline", marginRight: 6, verticalAlign: "middle" }} />
              Candidate Email <span style={{ color: "var(--text-muted)", fontWeight: 400 }}>(optional)</span>
            </label>
            <input
              id="candidate-email"
              type="email"
              placeholder="candidate@email.com"
              value={candidateEmail}
              onChange={e => setCandidateEmail(e.target.value)}
              style={{
                width: "100%", padding: "10px 14px",
                background: "var(--bg-elevated)", border: "1px solid var(--border-default)",
                borderRadius: 10, color: "var(--text-primary)", fontSize: 14, outline: "none",
              }}
            />
          </div>

          {/* Questions Count */}
          <div style={{ marginBottom: 28 }}>
            <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 8, color: "var(--text-secondary)" }}>
              <Clock size={14} style={{ display: "inline", marginRight: 6, verticalAlign: "middle" }} />
              Number of Questions: <span style={{ color: "#a78bfa" }}>{numQuestions}</span>
            </label>
            <input
              id="num-questions"
              type="range" min={4} max={10} step={1}
              value={numQuestions}
              onChange={e => setNumQuestions(Number(e.target.value))}
              style={{ width: "100%", accentColor: "#7c3aed" }}
            />
            <div style={{ display: "flex", justifyContent: "space-between", fontSize: 11, color: "var(--text-muted)", marginTop: 4 }}>
              <span>4 questions (~8 min)</span>
              <span>10 questions (~20 min)</span>
            </div>
          </div>

          {error && (
            <div style={{
              padding: "10px 14px", borderRadius: 10, marginBottom: 16,
              background: "rgba(244,63,94,0.1)", border: "1px solid rgba(244,63,94,0.25)",
              color: "#f43f5e", fontSize: 13, display: "flex", alignItems: "center", gap: 8,
            }}>
              <AlertCircle size={14} />
              {error}
            </div>
          )}

          <button
            id="start-interview-btn"
            onClick={handleStart}
            disabled={starting || loading}
            style={{
              width: "100%", padding: "13px 20px",
              background: "linear-gradient(135deg, #f43f5e, #f59e0b)",
              border: "none", borderRadius: 12, cursor: starting ? "wait" : "pointer",
              color: "white", fontSize: 15, fontWeight: 700,
              display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
              opacity: starting ? 0.7 : 1,
              boxShadow: "0 4px 20px rgba(244,63,94,0.35)",
              transition: "all 0.2s ease",
            }}
          >
            {starting ? (
              <>
                <div style={{ width: 16, height: 16, border: "2px solid rgba(255,255,255,0.3)", borderTopColor: "white", borderRadius: "50%", animation: "spin 0.8s linear infinite" }} />
                Generating Questions...
              </>
            ) : (
              <>
                <Video size={16} />
                Start Live Interview
                <ChevronRight size={16} />
              </>
            )}
          </button>
        </motion.div>

        {/* Right panel: info + recent sessions */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* What to expect */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.2 }}
            className="glass-card"
            style={{ padding: 20 }}
          >
            <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-muted)", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 14 }}>
              What the AI Scores
            </div>
            {[
              { label: "Answer Quality", pct: 40, color: "#7c3aed" },
              { label: "Communication", pct: 15, color: "#06b6d4" },
              { label: "Posture (Vision AI)", pct: 20, color: "#10b981" },
              { label: "Engagement", pct: 15, color: "#f59e0b" },
              { label: "Confidence", pct: 10, color: "#f43f5e" },
            ].map(item => (
              <div key={item.label} style={{ marginBottom: 10 }}>
                <div style={{ display: "flex", justifyContent: "space-between", fontSize: 12, marginBottom: 4 }}>
                  <span style={{ color: "var(--text-secondary)" }}>{item.label}</span>
                  <span style={{ color: item.color, fontWeight: 700 }}>{item.pct}%</span>
                </div>
                <div className="progress-bar">
                  <div className="progress-fill" style={{ width: `${item.pct * 2.5}%`, background: item.color }} />
                </div>
              </div>
            ))}
          </motion.div>

          {/* Requirements */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="glass-card"
            style={{ padding: 20 }}
          >
            <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-muted)", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 14 }}>
              Requirements
            </div>
            {[
              { ok: true, text: "Browser with camera support" },
              { ok: true, text: "Microphone for speech recognition" },
              { ok: true, text: "Good lighting (for posture analysis)" },
              { ok: null, text: "Gemini API key (falls back to mock if absent)" },
            ].map((req, i) => (
              <div key={i} style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 8, fontSize: 12 }}>
                <CheckCircle size={13} color={req.ok === true ? "#10b981" : "#f59e0b"} />
                <span style={{ color: "var(--text-secondary)" }}>{req.text}</span>
              </div>
            ))}
          </motion.div>

          {/* Recent Sessions */}
          {sessions.length > 0 && (
            <motion.div
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.4 }}
              className="glass-card"
              style={{ padding: 20 }}
            >
              <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-muted)", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 14 }}>
                Recent Sessions
              </div>
              {sessions.map(s => (
                <a
                  key={s.id}
                  href={s.status === "complete" ? `/interview/report/${s.id}` : `/interview/session/${s.id}`}
                  style={{ textDecoration: "none" }}
                >
                  <div style={{
                    display: "flex", justifyContent: "space-between", alignItems: "center",
                    padding: "8px 12px", borderRadius: 8, marginBottom: 6,
                    background: "var(--bg-elevated)", border: "1px solid var(--border-subtle)",
                    cursor: "pointer", transition: "all 0.15s ease",
                  }}>
                    <div>
                      <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-primary)" }}>{s.candidate_name}</div>
                      <div style={{ fontSize: 10, color: "var(--text-muted)" }}>
                        {new Date(s.created_at).toLocaleDateString()}
                      </div>
                    </div>
                    {s.total_score !== null ? (
                      <div style={{ fontSize: 16, fontWeight: 800, color: s.total_score >= 70 ? "#10b981" : s.total_score >= 50 ? "#f59e0b" : "#f43f5e", fontFamily: "'Space Grotesk', sans-serif" }}>
                        {s.total_score.toFixed(0)}
                      </div>
                    ) : (
                      <span style={{ fontSize: 10, color: "#f59e0b" }}>{s.status}</span>
                    )}
                  </div>
                </a>
              ))}
            </motion.div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        select option { background: #1a2035; }
        input[type="text"]:focus, input[type="email"]:focus { border-color: rgba(124,58,237,0.5); }
      `}</style>
    </div>
  );
}
