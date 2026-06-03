"use client";

import { useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import {
  Video, User, Mail, Briefcase, ChevronRight, Clock,
  AlertCircle, CheckCircle, PenLine, FileText, Upload, X, Loader2
} from "lucide-react";
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

  // Resume upload state
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [resumeText, setResumeText] = useState<string>("");
  const [resumeParsing, setResumeParsing] = useState(false);
  const [resumeError, setResumeError] = useState("");
  const [resumeWordCount, setResumeWordCount] = useState(0);
  const [dragOver, setDragOver] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

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

  async function handleResumeFile(file: File) {
    const validTypes = [".pdf", ".docx", ".txt", ".md"];
    const ext = "." + file.name.split(".").pop()?.toLowerCase();
    if (!validTypes.includes(ext)) {
      setResumeError("Unsupported file type. Upload PDF, DOCX, or TXT.");
      return;
    }
    if (file.size > 10 * 1024 * 1024) {
      setResumeError("File too large (max 10 MB).");
      return;
    }
    setResumeFile(file);
    setResumeError("");
    setResumeText("");
    setResumeParsing(true);
    try {
      const result = await interviewApi.parseResume(file);
      setResumeText(result.text);
      setResumeWordCount(result.word_count);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Could not parse resume";
      setResumeError(msg);
      setResumeFile(null);
    } finally {
      setResumeParsing(false);
    }
  }

  function handleFileDrop(e: React.DragEvent) {
    e.preventDefault();
    setDragOver(false);
    const file = e.dataTransfer.files[0];
    if (file) handleResumeFile(file);
  }

  function clearResume() {
    setResumeFile(null);
    setResumeText("");
    setResumeError("");
    setResumeWordCount(0);
    if (fileInputRef.current) fileInputRef.current.value = "";
  }

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
            resumeText || undefined,
          )
        : await interviewApi.start(
            selectedJobId,
            candidateName.trim(),
            candidateEmail || undefined,
            numQuestions,
            undefined, undefined, undefined,
            resumeText || undefined,
          );
      sessionStorage.setItem(`interview_${session.session_id}`, JSON.stringify(session));
      router.push(`/interview/session/${session.session_id}`);
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Failed to start interview";
      setError(msg);
      setStarting(false);
    }
  }

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
              AI-generated questions · Resume-aware · Real-time posture analysis · Honest scoring
            </p>
          </div>
        </div>
      </motion.div>

      <div style={{ display: "grid", gridTemplateColumns: "minmax(0, 1fr) minmax(0, 360px)", gap: 24, flexWrap: "wrap" }} className="interview-layout">
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

          {/* Resume Upload */}
          <div style={{ marginBottom: 20 }}>
            <label style={{ display: "block", fontSize: 13, fontWeight: 600, marginBottom: 8, color: "var(--text-secondary)" }}>
              <FileText size={14} style={{ display: "inline", marginRight: 6, verticalAlign: "middle" }} />
              Candidate Resume <span style={{ color: "var(--text-muted)", fontWeight: 400 }}>(optional — AI personalizes questions)</span>
            </label>

            <AnimatePresence mode="wait">
              {resumeFile && resumeText ? (
                /* Parsed successfully */
                <motion.div
                  key="parsed"
                  initial={{ opacity: 0, scale: 0.97 }}
                  animate={{ opacity: 1, scale: 1 }}
                  exit={{ opacity: 0, scale: 0.97 }}
                  style={{
                    padding: "12px 14px", borderRadius: 10,
                    background: "rgba(16,185,129,0.08)", border: "1px solid rgba(16,185,129,0.25)",
                    display: "flex", alignItems: "center", justifyContent: "space-between",
                  }}
                >
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <div style={{
                      width: 32, height: 32, borderRadius: 8,
                      background: "rgba(16,185,129,0.15)", display: "flex", alignItems: "center", justifyContent: "center",
                    }}>
                      <CheckCircle size={16} color="#10b981" />
                    </div>
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 600, color: "var(--text-primary)" }}>
                        {resumeFile.name}
                      </div>
                      <div style={{ fontSize: 11, color: "#10b981" }}>
                        ✓ Parsed — {resumeWordCount} words · AI will personalize questions from this resume
                      </div>
                    </div>
                  </div>
                  <button
                    type="button"
                    onClick={clearResume}
                    style={{
                      background: "none", border: "none", cursor: "pointer",
                      color: "var(--text-muted)", padding: 4, borderRadius: 6,
                      display: "flex", alignItems: "center",
                    }}
                  >
                    <X size={16} />
                  </button>
                </motion.div>
              ) : resumeParsing ? (
                /* Parsing in progress */
                <motion.div
                  key="parsing"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  style={{
                    padding: "12px 14px", borderRadius: 10,
                    background: "rgba(124,58,237,0.08)", border: "1px solid rgba(124,58,237,0.2)",
                    display: "flex", alignItems: "center", gap: 10,
                  }}
                >
                  <Loader2 size={16} color="#a78bfa" style={{ animation: "spin 0.8s linear infinite" }} />
                  <span style={{ fontSize: 13, color: "#a78bfa" }}>Parsing resume...</span>
                </motion.div>
              ) : (
                /* Drop zone */
                <motion.div
                  key="dropzone"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  onDragOver={e => { e.preventDefault(); setDragOver(true); }}
                  onDragLeave={() => setDragOver(false)}
                  onDrop={handleFileDrop}
                  onClick={() => fileInputRef.current?.click()}
                  style={{
                    padding: "20px 16px", borderRadius: 10, cursor: "pointer",
                    border: `2px dashed ${dragOver ? "rgba(124,58,237,0.6)" : "var(--border-default)"}`,
                    background: dragOver ? "rgba(124,58,237,0.06)" : "var(--bg-elevated)",
                    display: "flex", flexDirection: "column", alignItems: "center", gap: 8,
                    transition: "all 0.2s ease",
                  }}
                >
                  <div style={{
                    width: 36, height: 36, borderRadius: 10,
                    background: dragOver ? "rgba(124,58,237,0.15)" : "rgba(255,255,255,0.05)",
                    display: "flex", alignItems: "center", justifyContent: "center",
                    transition: "all 0.2s ease",
                  }}>
                    <Upload size={16} color={dragOver ? "#a78bfa" : "var(--text-muted)"} />
                  </div>
                  <div style={{ fontSize: 13, fontWeight: 600, color: dragOver ? "#a78bfa" : "var(--text-secondary)" }}>
                    Drop resume here or click to browse
                  </div>
                  <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                    PDF, DOCX, TXT · Max 10 MB
                  </div>
                </motion.div>
              )}
            </AnimatePresence>

            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.docx,.txt,.md"
              style={{ display: "none" }}
              onChange={e => {
                const f = e.target.files?.[0];
                if (f) handleResumeFile(f);
              }}
            />

            {resumeError && (
              <div style={{
                marginTop: 8, padding: "8px 12px", borderRadius: 8, fontSize: 12,
                background: "rgba(244,63,94,0.08)", border: "1px solid rgba(244,63,94,0.2)",
                color: "#f43f5e", display: "flex", alignItems: "center", gap: 6,
              }}>
                <AlertCircle size={12} />
                {resumeError}
              </div>
            )}
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
                {resumeText ? "Building personalized questions..." : "Generating Questions..."}
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

        {/* Right panel */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* What the AI Scores */}
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

          {/* Resume tip card */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.25 }}
            className="glass-card"
            style={{ padding: 20, background: "rgba(124,58,237,0.06)", borderColor: "rgba(124,58,237,0.2)" }}
          >
            <div style={{ fontSize: 12, fontWeight: 700, color: "#a78bfa", letterSpacing: "0.06em", textTransform: "uppercase", marginBottom: 12 }}>
              ✦ Resume-Aware AI
            </div>
            {[
              "References actual companies & projects from the resume",
              "Probes claimed skills with concrete examples",
              "Asks about career transitions and gaps",
              "Makes every interview feel personal, not generic",
            ].map((tip, i) => (
              <div key={i} style={{ display: "flex", gap: 8, marginBottom: 8, fontSize: 12 }}>
                <span style={{ color: "#a78bfa", marginTop: 1, flexShrink: 0 }}>→</span>
                <span style={{ color: "var(--text-secondary)" }}>{tip}</span>
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
        textarea:focus { border-color: rgba(124,58,237,0.5) !important; outline: none; }
      `}</style>
    </div>
  );
}
