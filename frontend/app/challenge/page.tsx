"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Trophy, Shield, Download, Play, CheckCircle, AlertTriangle,
  Loader2, FileText, Database, Brain, Activity, ChevronRight,
  Clock, Award, Upload, X, Eye, Users, FileUp, Zap,
  Sparkles, Target, BookOpen, BarChart2
} from "lucide-react";
import { challengeApi } from "@/lib/api";

// ── Types ──────────────────────────────────────────────────────────────────────
type DatasetInfo = Awaited<ReturnType<typeof challengeApi.getInfo>>;
type RunStatus = Awaited<ReturnType<typeof challengeApi.getStatus>>;
type RankedItem = RunStatus["top_10_preview"][0];
type JDProfile = Awaited<ReturnType<typeof challengeApi.parseJd>>;
type HistoryRun = Awaited<ReturnType<typeof challengeApi.getHistory>>["runs"][0];

// ── History Tab ────────────────────────────────────────────────────────────────
function HistoryTab() {
  const [runs, setRuns] = useState<HistoryRun[]>([]);
  const [loading, setLoading] = useState(true);
  const [deleting, setDeleting] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const d = await challengeApi.getHistory();
      setRuns(d.runs);
    } catch {
      setRuns([]);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);

  async function handleDelete(runId: string) {
    if (!confirm("Delete this ranking run from history?")) return;
    setDeleting(runId);
    try {
      await challengeApi.deleteHistory(runId);
      setRuns(prev => prev.filter(r => r.run_id !== runId));
    } catch (e) {
      alert("Could not delete: " + (e instanceof Error ? e.message : "unknown error"));
    } finally {
      setDeleting(null);
    }
  }

  function fmtDate(iso: string | null) {
    if (!iso) return "—";
    const d = new Date(iso);
    return d.toLocaleDateString("en-IN", { day: "2-digit", month: "short", year: "numeric" }) +
      " " + d.toLocaleTimeString("en-IN", { hour: "2-digit", minute: "2-digit" });
  }

  if (loading) return (
    <div style={{ textAlign: "center", padding: "60px 0", color: "var(--text-muted)" }}>
      <Loader2 size={28} style={{ animation: "spin 0.8s linear infinite", marginBottom: 12 }} />
      <div style={{ fontSize: 13 }}>Loading history...</div>
    </div>
  );

  if (runs.length === 0) return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ textAlign: "center", padding: "60px 40px" }}>
      <Database size={44} color="rgba(100,116,139,0.4)" style={{ marginBottom: 14 }} />
      <div style={{ fontSize: 16, fontWeight: 700, color: "var(--text-secondary)", marginBottom: 8 }}>No ranking history yet</div>
      <p style={{ fontSize: 12, color: "var(--text-muted)", maxWidth: 300, margin: "0 auto" }}>
        Run your first ranking on the <strong style={{ color: "#f59e0b" }}>Rank</strong> tab.
        Completed runs will be saved here automatically.
      </p>
    </motion.div>
  );

  return (
    <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
      <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 16 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Clock size={14} color="#f59e0b" />
          <span style={{ fontSize: 13, fontWeight: 700 }}>{runs.length} Saved Ranking{runs.length !== 1 ? "s" : ""}</span>
        </div>
        <button onClick={load} style={{ padding: "5px 12px", borderRadius: 8, border: "1px solid var(--border-subtle)", background: "var(--bg-elevated)", color: "var(--text-muted)", fontSize: 11, cursor: "pointer", display: "flex", alignItems: "center", gap: 5 }}>
          <Activity size={11} /> Refresh
        </button>
      </div>

      <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
        {runs.map((run, idx) => {
          const isOk = run.status === "complete";
          const isFailed = run.status === "failed";
          const statusColor = isOk ? "#10b981" : isFailed ? "#f43f5e" : "#f59e0b";
          const statusBg = isOk ? "rgba(16,185,129,0.08)" : isFailed ? "rgba(244,63,94,0.08)" : "rgba(245,158,11,0.08)";
          const statusBorder = isOk ? "rgba(16,185,129,0.25)" : isFailed ? "rgba(244,63,94,0.25)" : "rgba(245,158,11,0.25)";

          return (
            <motion.div key={run.run_id} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: idx * 0.04 }}
              style={{ padding: "16px 18px", borderRadius: 12, background: statusBg, border: `1px solid ${statusBorder}` }}>

              {/* Top row */}
              <div style={{ display: "flex", alignItems: "flex-start", gap: 12, marginBottom: 10 }}>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap", marginBottom: 4 }}>
                    <span style={{ fontSize: 13, fontWeight: 700 }}>
                      {run.uploaded_filename || "Server dataset"}
                    </span>
                    <span style={{ fontSize: 9, padding: "2px 7px", borderRadius: 20, background: `${statusColor}20`, border: `1px solid ${statusColor}40`, color: statusColor, fontWeight: 700, textTransform: "uppercase" }}>
                      {run.status}
                    </span>
                    {run.is_sample && <span style={{ fontSize: 9, padding: "2px 7px", borderRadius: 20, background: "rgba(6,182,212,0.12)", border: "1px solid rgba(6,182,212,0.2)", color: "#06b6d4", fontWeight: 700 }}>SAMPLE</span>}
                    {run.jd_provided && <span style={{ fontSize: 9, padding: "2px 7px", borderRadius: 20, background: "rgba(139,92,246,0.12)", border: "1px solid rgba(139,92,246,0.2)", color: "#a78bfa", fontWeight: 700 }}>CUSTOM JD</span>}
                  </div>
                  {run.jd_title && (
                    <div style={{ fontSize: 10, color: "#a78bfa", marginBottom: 2 }}>JD: {run.jd_title}</div>
                  )}
                  <div style={{ fontSize: 10, color: "var(--text-muted)" }}>{fmtDate(run.completed_at || run.started_at)}</div>
                </div>

                {/* Stats */}
                <div style={{ display: "flex", gap: 8, flexShrink: 0 }}>
                  {[
                    { label: "Ranked", val: run.ranked_count, color: "#f59e0b" },
                    { label: "Analyzed", val: run.processed.toLocaleString(), color: "#a78bfa" },
                    { label: "Time", val: run.elapsed_seconds ? `${run.elapsed_seconds.toFixed(0)}s` : "—", color: "#06b6d4" },
                  ].map(s => (
                    <div key={s.label} style={{ textAlign: "center", padding: "6px 10px", borderRadius: 8, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.07)" }}>
                      <div style={{ fontSize: 13, fontWeight: 800, fontFamily: "'Space Grotesk',sans-serif", color: s.color }}>{s.val}</div>
                      <div style={{ fontSize: 9, color: "var(--text-muted)" }}>{s.label}</div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Top-5 mini table */}
              {run.top_5 && run.top_5.length > 0 && (
                <div style={{ marginBottom: 10 }}>
                  <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.05em" }}>Top {run.top_5.length} candidates</div>
                  <div style={{ display: "flex", flexDirection: "column", gap: 4 }}>
                    {run.top_5.map(c => (
                      <div key={c.candidate_id} style={{ display: "flex", alignItems: "center", gap: 10, padding: "6px 10px", borderRadius: 8, background: "rgba(255,255,255,0.03)", border: "1px solid rgba(255,255,255,0.06)" }}>
                        <div style={{ width: 20, height: 20, borderRadius: "50%", background: "rgba(245,158,11,0.15)", border: "1px solid rgba(245,158,11,0.3)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 9, fontWeight: 800, color: "#f59e0b", flexShrink: 0 }}>#{c.rank}</div>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontSize: 11, fontWeight: 600, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{c.name || c.candidate_id}</div>
                          <div style={{ fontSize: 10, color: "var(--text-muted)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{c.title}</div>
                        </div>
                        <div style={{ fontSize: 13, fontWeight: 800, fontFamily: "'Space Grotesk',sans-serif", color: c.score >= 0.7 ? "#10b981" : c.score >= 0.45 ? "#f59e0b" : "#f43f5e", flexShrink: 0 }}>
                          {(c.score * 100).toFixed(1)}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {run.error && (
                <div style={{ padding: "7px 10px", borderRadius: 7, background: "rgba(244,63,94,0.08)", border: "1px solid rgba(244,63,94,0.2)", fontSize: 11, color: "#f43f5e", marginBottom: 10 }}>
                  Error: {run.error}
                </div>
              )}

              {/* Actions */}
              <div style={{ display: "flex", gap: 8 }}>
                {isOk && (
                  <button onClick={() => challengeApi.downloadHistory(run.run_id)} style={{
                    flex: 1, display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
                    padding: "8px 12px", borderRadius: 8, cursor: "pointer",
                    background: "linear-gradient(135deg,#059669,#10b981)", border: "none",
                    color: "white", fontSize: 11, fontWeight: 700, boxShadow: "0 2px 10px rgba(16,185,129,0.25)",
                  }}>
                    <Download size={11} /> Download CSV
                  </button>
                )}
                <button onClick={() => handleDelete(run.run_id)} disabled={deleting === run.run_id} style={{
                  padding: "8px 12px", borderRadius: 8, cursor: "pointer",
                  background: "rgba(244,63,94,0.1)", border: "1px solid rgba(244,63,94,0.2)",
                  color: "#f43f5e", fontSize: 11, fontWeight: 600, display: "flex", alignItems: "center", gap: 5,
                }}>
                  {deleting === run.run_id ? <Loader2 size={11} style={{ animation: "spin 0.8s linear infinite" }} /> : <X size={11} />} Delete
                </button>
              </div>
            </motion.div>
          );
        })}
      </div>
    </motion.div>
  );
}

// ── Score Bar ──────────────────────────────────────────────────────────────────
function ScoreBar({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
        <span style={{ fontSize: 10, color: "var(--text-muted)", fontWeight: 500 }}>{label}</span>
        <span style={{ fontSize: 10, color, fontWeight: 700 }}>{value.toFixed(1)}/{max}</span>
      </div>
      <div style={{ height: 4, borderRadius: 4, background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
        <motion.div
          initial={{ width: 0 }} animate={{ width: `${Math.min(100, (value / max) * 100)}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          style={{ height: "100%", borderRadius: 4, background: color }}
        />
      </div>
    </div>
  );
}

function Medal({ rank }: { rank: number }) {
  const m: Record<number, { bg: string; border: string; emoji: string }> = {
    1: { bg: "rgba(251,191,36,0.15)", border: "rgba(251,191,36,0.4)", emoji: "🥇" },
    2: { bg: "rgba(148,163,184,0.15)", border: "rgba(148,163,184,0.4)", emoji: "🥈" },
    3: { bg: "rgba(180,120,80,0.15)", border: "rgba(180,120,80,0.4)", emoji: "🥉" },
  };
  const medal = m[rank];
  if (!medal) return (
    <div style={{
      width: 28, height: 28, borderRadius: "50%", flexShrink: 0,
      background: "rgba(124,58,237,0.1)", border: "1px solid rgba(124,58,237,0.2)",
      display: "flex", alignItems: "center", justifyContent: "center",
      fontSize: 11, fontWeight: 700, color: "#a78bfa",
    }}>{rank}</div>
  );
  return (
    <div style={{ width: 28, height: 28, borderRadius: "50%", flexShrink: 0, background: medal.bg, border: `1px solid ${medal.border}`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16 }}>
      {medal.emoji}
    </div>
  );
}

// ── Drag-Drop Zone ─────────────────────────────────────────────────────────────
function DropZone({ onFile, accept, label, sublabel, color = "#f59e0b", icon: Icon = FileUp, compact = false }:
  { onFile: (f: File) => void; accept: string; label: string; sublabel: string; color?: string; icon?: React.ElementType; compact?: boolean }) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);
  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault(); setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) onFile(f);
  }, [onFile]);
  return (
    <div
      onDragOver={e => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      style={{
        border: `2px dashed ${dragging ? color : color + "55"}`,
        borderRadius: 10, padding: compact ? "14px 16px" : "22px 16px",
        textAlign: "center", cursor: "pointer", transition: "all 0.2s",
        background: dragging ? `${color}12` : `${color}06`,
      }}
    >
      <input ref={inputRef} type="file" accept={accept} style={{ display: "none" }}
        onChange={e => { const f = e.target.files?.[0]; if (f) onFile(f); }} />
      <Icon size={compact ? 20 : 26} color={dragging ? color : `${color}88`} style={{ marginBottom: 6 }} />
      <div style={{ fontSize: compact ? 11 : 12, fontWeight: 700, color, marginBottom: 3 }}>{label}</div>
      <div style={{ fontSize: 10, color: "var(--text-muted)" }}>{sublabel}</div>
    </div>
  );
}

// ── File Chip ──────────────────────────────────────────────────────────────────
function FileChip({ file, color = "#10b981", onRemove }: { file: File; color?: string; onRemove: () => void }) {
  return (
    <div style={{
      padding: "9px 12px", borderRadius: 10, display: "flex", alignItems: "center", gap: 10,
      background: `${color}10`, border: `1px solid ${color}40`,
    }}>
      <FileText size={14} color={color} style={{ flexShrink: 0 }} />
      <div style={{ flex: 1, minWidth: 0 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{file.name}</div>
        <div style={{ fontSize: 10, color: "var(--text-muted)" }}>{(file.size / (1024 * 1024)).toFixed(1)} MB</div>
      </div>
      <button onClick={onRemove} style={{ width: 22, height: 22, borderRadius: 6, border: "none", background: "rgba(244,63,94,0.15)", color: "#f43f5e", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "center" }}>
        <X size={11} />
      </button>
    </div>
  );
}

// ── Candidate Row ──────────────────────────────────────────────────────────────
function CandidateRow({ item, index, expanded, onToggle }: { item: RankedItem; index: number; expanded: boolean; onToggle: () => void }) {
  const scoreColor = item.score >= 0.7 ? "#10b981" : item.score >= 0.45 ? "#f59e0b" : "#f43f5e";
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.03 }}>
      <div onClick={onToggle} style={{
        padding: "12px 16px", borderRadius: expanded ? "12px 12px 0 0" : 12,
        background: expanded ? "rgba(124,58,237,0.08)" : "var(--bg-elevated)",
        border: `1px solid ${expanded ? "rgba(124,58,237,0.3)" : "var(--border-subtle)"}`,
        cursor: "pointer", display: "flex", alignItems: "center", gap: 12,
        transition: "all 0.2s", marginBottom: expanded ? 0 : 6,
      }}>
        <Medal rank={item.rank} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            <span style={{ fontWeight: 700, fontSize: 13 }}>{item.name || item.candidate_id}</span>
            <span style={{ fontSize: 10, padding: "2px 7px", borderRadius: 6, background: "rgba(124,58,237,0.12)", border: "1px solid rgba(124,58,237,0.2)", color: "#a78bfa", fontWeight: 600 }}>{item.candidate_id}</span>
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{item.title}</div>
        </div>
        <div style={{ textAlign: "right", flexShrink: 0 }}>
          <div style={{ fontSize: 20, fontWeight: 800, fontFamily: "'Space Grotesk',sans-serif", color: scoreColor }}>{(item.score * 100).toFixed(1)}</div>
          <div style={{ fontSize: 9, color: "var(--text-muted)", fontWeight: 600 }}>/ 100</div>
        </div>
        <div style={{ transform: `rotate(${expanded ? 90 : 0}deg)`, transition: "transform 0.2s", color: "var(--text-muted)" }}>
          <ChevronRight size={14} />
        </div>
      </div>
      <AnimatePresence>
        {expanded && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }} transition={{ duration: 0.22 }} style={{ overflow: "hidden" }}>
            <div style={{ padding: "14px 16px 16px", borderRadius: "0 0 12px 12px", background: "rgba(124,58,237,0.05)", border: "1px solid rgba(124,58,237,0.2)", borderTop: "none", marginBottom: 6 }}>
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 12 }}>
                <div>
                  <ScoreBar label="Skills Depth" value={item.skills_score} max={40} color="#7c3aed" />
                  <ScoreBar label="Career Quality" value={item.career_score} max={30} color="#06b6d4" />
                </div>
                <div>
                  <ScoreBar label="Behavioral Signals" value={item.behavioral_score} max={20} color="#10b981" />
                  <ScoreBar label="Platform Engagement" value={item.engagement_score} max={10} color="#f59e0b" />
                </div>
              </div>
              <div style={{ padding: "9px 12px", borderRadius: 8, background: "rgba(255,255,255,0.03)", border: "1px solid var(--border-subtle)" }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", marginBottom: 4, textTransform: "uppercase", letterSpacing: "0.06em" }}>Reasoning</div>
                <p style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.65, margin: 0 }}>{item.reasoning}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────────
export default function ChallengePage() {
  const [info, setInfo] = useState<DatasetInfo | null>(null);
  const [infoLoading, setInfoLoading] = useState(true);

  // JD state
  const [jdFile, setJdFile] = useState<File | null>(null);
  const [jdText, setJdText] = useState("");
  const [jdPaste, setJdPaste] = useState(false); // show paste area
  const [parsedJd, setParsedJd] = useState<JDProfile | null>(null);
  const [parsingJd, setParsingJd] = useState(false);
  const [jdError, setJdError] = useState<string | null>(null);

  // Candidates state
  const [candidatesFile, setCandidatesFile] = useState<File | null>(null);
  const [useSample, setUseSample] = useState(false);
  const [uploadPct, setUploadPct] = useState(0);

  // Run state
  const [runId, setRunId] = useState<string | null>(null);
  const [runStatus, setRunStatus] = useState<RunStatus | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [allResults, setAllResults] = useState<RankedItem[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [showAll, setShowAll] = useState(false);
  const [activeTab, setActiveTab] = useState<"rank" | "history">("rank");

  useEffect(() => {
    challengeApi.getInfo().then(d => { setInfo(d); setInfoLoading(false); }).catch(() => setInfoLoading(false));
  }, []);

  const hasLocalFull = !!info?.full_dataset?.available;
  const hasLocalSample = !!info?.sample_dataset?.available;

  // Parse JD whenever file or text changes
  async function handleParseJd(source: File | string) {
    if (!source || (typeof source === "string" && source.trim().length < 30)) return;
    setParsingJd(true);
    setJdError(null);
    try {
      const result = await challengeApi.parseJd(source);
      setParsedJd(result);
      if (typeof source === "string") setJdText(result.jd_text); // store parsed text
    } catch (e: unknown) {
      setJdError(e instanceof Error ? e.message : "Failed to parse JD");
    } finally {
      setParsingJd(false);
    }
  }

  const effectiveJdText = parsedJd?.jd_text || jdText;
  const useUpload = !!candidatesFile;
  const useLocalSample = !candidatesFile && useSample && hasLocalSample;
  const useLocalFull = !candidatesFile && !useSample && hasLocalFull;
  const canRun = useUpload || useLocalSample || useLocalFull;

  async function handleRun() {
    if (running || !canRun) return;
    setRunning(true);
    setError(null);
    setRunStatus(null);
    setAllResults([]);
    setUploadPct(0);

    try {
      let id: string;
      if (useUpload && candidatesFile) {
        const r = await challengeApi.uploadAndRun(
          candidatesFile, jdFile || null, effectiveJdText || undefined, 0, setUploadPct
        );
        id = r.run_id;
      } else {
        const r = await challengeApi.run(useLocalSample, 0, effectiveJdText || undefined);
        id = r.run_id;
      }
      setRunId(id);

      const final = await challengeApi.pollStatus(id, (processed, total, honeypots, status) => {
        setRunStatus(prev => ({ ...(prev || {} as RunStatus), processed, total_candidates: total, honeypots_detected: honeypots, status }));
      });
      setRunStatus(final);

      const full = await challengeApi.getResults(id);
      setAllResults(full.results);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Ranking failed");
    } finally {
      setRunning(false);
    }
  }

  const progress = runStatus && runStatus.total_candidates > 0
    ? Math.min(100, (runStatus.processed / runStatus.total_candidates) * 100) : 0;
  const isComplete = runStatus?.status === "complete";
  const displayResults = showAll ? allResults : allResults.slice(0, 10);

  return (
    <div style={{ maxWidth: 1100 }}>
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 20 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
          <div style={{ width: 44, height: 44, borderRadius: 12, flexShrink: 0, background: "linear-gradient(135deg,rgba(245,158,11,0.2),rgba(251,191,36,0.1))", border: "1px solid rgba(245,158,11,0.4)", display: "flex", alignItems: "center", justifyContent: "center", boxShadow: "0 0 20px rgba(245,158,11,0.2)" }}>
            <Trophy size={22} color="#f59e0b" />
          </div>
          <div>
            <h1 style={{ fontSize: 24, fontWeight: 800, fontFamily: "'Space Grotesk',sans-serif", marginBottom: 2 }}>Challenge Ranker</h1>
            <p style={{ fontSize: 12, color: "var(--text-muted)" }}>Upload any JD + candidates · Genuine multi-dimensional ranking · No keyword stuffing</p>
          </div>
        </div>

        {/* Tab switcher */}
        <div style={{ display: "flex", gap: 4, background: "rgba(255,255,255,0.04)", borderRadius: 10, padding: 4, width: "fit-content", border: "1px solid var(--border-subtle)" }}>
          {([
            { id: "rank", label: "⚡ Rank", hint: "Run ranking" },
            { id: "history", label: "📋 History", hint: "Past runs" },
          ] as const).map(tab => (
            <button key={tab.id} onClick={() => setActiveTab(tab.id)} style={{
              padding: "7px 18px", borderRadius: 7, border: "none", cursor: "pointer",
              background: activeTab === tab.id ? "linear-gradient(135deg,#d97706,#f59e0b)" : "transparent",
              color: activeTab === tab.id ? "white" : "var(--text-muted)",
              fontSize: 12, fontWeight: 700, transition: "all 0.2s",
              boxShadow: activeTab === tab.id ? "0 2px 10px rgba(245,158,11,0.3)" : "none",
            }}>{tab.label}</button>
          ))}
        </div>
      </motion.div>

      {/* Main content — Rank tab or History tab */}
      {activeTab === "history" ? (
        <HistoryTab />
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "300px 1fr", gap: 18, alignItems: "start" }}>

        {/* ── LEFT PANEL ─────────────────────────────────────── */}
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>

          {/* ❶ JD Upload */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card" style={{ padding: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
              <div style={{ width: 22, height: 22, borderRadius: 6, background: "rgba(139,92,246,0.2)", border: "1px solid rgba(139,92,246,0.4)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 800, color: "#a78bfa" }}>1</div>
              <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Job Description</span>
              <span style={{ fontSize: 9, padding: "2px 7px", borderRadius: 20, background: "rgba(139,92,246,0.12)", border: "1px solid rgba(139,92,246,0.25)", color: "#a78bfa", fontWeight: 600 }}>Optional</span>
            </div>

            {jdFile ? (
              <div style={{ marginBottom: 8 }}>
                <FileChip file={jdFile} color="#a78bfa" onRemove={() => { setJdFile(null); setParsedJd(null); }} />
              </div>
            ) : !jdPaste ? (
              <DropZone
                onFile={f => { setJdFile(f); handleParseJd(f); }}
                accept=".docx,.txt,.md,.pdf"
                label="Drop JD file here"
                sublabel=".docx · .txt · .md · .pdf · or click"
                color="#a78bfa"
                icon={BookOpen}
                compact
              />
            ) : null}

            {/* Paste toggle */}
            {!jdFile && (
              <button onClick={() => setJdPaste(!jdPaste)} style={{
                width: "100%", marginTop: 8, padding: "7px 12px", borderRadius: 8,
                background: "rgba(255,255,255,0.04)", border: "1px solid var(--border-subtle)",
                color: "var(--text-muted)", fontSize: 11, cursor: "pointer", textAlign: "center",
              }}>
                {jdPaste ? "↑ Hide paste area" : "Paste JD text instead"}
              </button>
            )}

            {jdPaste && !jdFile && (
              <div style={{ marginTop: 8 }}>
                <textarea
                  value={jdText}
                  onChange={e => setJdText(e.target.value)}
                  placeholder="Paste your job description here..."
                  style={{
                    width: "100%", minHeight: 100, padding: "10px 12px",
                    borderRadius: 8, background: "rgba(255,255,255,0.04)",
                    border: "1px solid var(--border-subtle)", color: "var(--text-primary)",
                    fontSize: 11, resize: "vertical", outline: "none",
                  }}
                />
                <button
                  onClick={() => handleParseJd(jdText)}
                  disabled={jdText.trim().length < 30 || parsingJd}
                  style={{
                    width: "100%", marginTop: 6, padding: "8px", borderRadius: 8,
                    background: jdText.trim().length >= 30 ? "rgba(139,92,246,0.2)" : "rgba(100,116,139,0.15)",
                    border: `1px solid ${jdText.trim().length >= 30 ? "rgba(139,92,246,0.4)" : "var(--border-subtle)"}`,
                    color: "#a78bfa", fontSize: 11, fontWeight: 600, cursor: "pointer",
                    display: "flex", alignItems: "center", justifyContent: "center", gap: 6,
                  }}>
                  {parsingJd ? <><Loader2 size={12} style={{ animation: "spin 0.8s linear infinite" }} /> Parsing...</> : <><Sparkles size={12} /> Extract JD Profile</>}
                </button>
              </div>
            )}

            {/* Parsing state */}
            {parsingJd && !parsedJd && (
              <div style={{ marginTop: 8, display: "flex", alignItems: "center", gap: 6, color: "#a78bfa", fontSize: 11 }}>
                <Loader2 size={12} style={{ animation: "spin 0.8s linear infinite" }} /> Extracting skills & requirements...
              </div>
            )}

            {/* JD Parsed Profile */}
            {parsedJd && !parsingJd && (
              <motion.div initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} style={{
                marginTop: 10, padding: "10px 12px", borderRadius: 8,
                background: "rgba(139,92,246,0.08)", border: "1px solid rgba(139,92,246,0.25)",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                  <Sparkles size={11} color="#a78bfa" />
                  <span style={{ fontSize: 10, fontWeight: 700, color: "#a78bfa", textTransform: "uppercase" }}>JD Parsed ✓</span>
                </div>
                <p style={{ fontSize: 10, color: "var(--text-muted)", margin: "0 0 8px", lineHeight: 1.6 }}>{parsedJd.parsed_summary}</p>

                <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", marginBottom: 4, textTransform: "uppercase" }}>
                  {parsedJd.core_skills_count} Core Skills Detected
                </div>
                <div style={{ display: "flex", flexWrap: "wrap", gap: 4, marginBottom: 8 }}>
                  {parsedJd.required_skills_preview.slice(0, 8).map(s => (
                    <span key={s} style={{ fontSize: 10, padding: "2px 7px", borderRadius: 20, background: "rgba(139,92,246,0.15)", border: "1px solid rgba(139,92,246,0.25)", color: "#c4b5fd" }}>{s}</span>
                  ))}
                  {parsedJd.core_skills_count > 8 && (
                    <span style={{ fontSize: 10, padding: "2px 7px", borderRadius: 20, background: "rgba(100,116,139,0.15)", color: "var(--text-muted)" }}>+{parsedJd.core_skills_count - 8} more</span>
                  )}
                </div>

                <div style={{ display: "flex", gap: 8 }}>
                  <div style={{ flex: 1, padding: "6px 8px", borderRadius: 6, background: "rgba(6,182,212,0.1)", border: "1px solid rgba(6,182,212,0.2)", textAlign: "center" }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: "#06b6d4" }}>{parsedJd.experience_range.ideal_min}–{parsedJd.experience_range.ideal_max}yr</div>
                    <div style={{ fontSize: 9, color: "var(--text-muted)" }}>Ideal exp</div>
                  </div>
                  <div style={{ flex: 1, padding: "6px 8px", borderRadius: 6, background: "rgba(16,185,129,0.1)", border: "1px solid rgba(16,185,129,0.2)", textAlign: "center" }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: "#10b981" }}>{parsedJd.core_skills_count}</div>
                    <div style={{ fontSize: 9, color: "var(--text-muted)" }}>Core skills</div>
                  </div>
                  <div style={{ flex: 1, padding: "6px 8px", borderRadius: 6, background: "rgba(245,158,11,0.1)", border: "1px solid rgba(245,158,11,0.2)", textAlign: "center" }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: "#f59e0b" }}>{parsedJd.secondary_skills_count}</div>
                    <div style={{ fontSize: 9, color: "var(--text-muted)" }}>Nice skills</div>
                  </div>
                </div>

                {parsedJd.locations.length > 0 && (
                  <div style={{ marginTop: 6, fontSize: 10, color: "var(--text-muted)" }}>
                    📍 {parsedJd.locations.join(", ")}
                  </div>
                )}
              </motion.div>
            )}

            {jdError && (
              <div style={{ marginTop: 8, fontSize: 11, color: "#f43f5e" }}>{jdError}</div>
            )}

            {/* No JD hint */}
            {!parsedJd && !parsingJd && !jdPaste && !jdFile && (
              <p style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 8, textAlign: "center", lineHeight: 1.6 }}>
                Without a JD, ranking uses the built-in <strong style={{ color: "#f59e0b" }}>Redrob AI Engineer</strong> profile
              </p>
            )}
          </motion.div>

          {/* ❷ Candidates Upload */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.04 }} className="glass-card" style={{ padding: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
              <div style={{ width: 22, height: 22, borderRadius: 6, background: "rgba(245,158,11,0.2)", border: "1px solid rgba(245,158,11,0.4)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 800, color: "#f59e0b" }}>2</div>
              <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Candidates</span>
              <span style={{ fontSize: 9, padding: "2px 7px", borderRadius: 20, background: "rgba(16,185,129,0.12)", border: "1px solid rgba(16,185,129,0.2)", color: "#10b981", fontWeight: 700 }}>Required</span>
            </div>

            {candidatesFile ? (
              <FileChip file={candidatesFile} color="#10b981" onRemove={() => setCandidatesFile(null)} />
            ) : (
              <DropZone
                onFile={setCandidatesFile}
                accept=".json,.jsonl"
                label="Drop candidates file here"
                sublabel="candidates.jsonl or sample_candidates.json"
                color="#f59e0b"
                compact
              />
            )}

            {/* Dataset info */}
            {!infoLoading && !candidatesFile && (
              <div style={{ display: "flex", flexDirection: "column", gap: 6, marginTop: 10 }}>
                {[
                  { label: "candidates.jsonl", ok: hasLocalFull, desc: hasLocalFull ? `${info?.full_dataset?.size_mb} MB · 100k candidates` : "Not on server", val: false },
                  { label: "sample_candidates.json", ok: hasLocalSample, desc: hasLocalSample ? `${info?.sample_dataset?.candidate_count} candidates · embedded` : "Not found", val: true },
                ].map(opt => (
                  <button key={opt.label} disabled={!opt.ok} onClick={() => opt.ok && setUseSample(opt.val)}
                    style={{
                      padding: "8px 12px", borderRadius: 8, cursor: opt.ok ? "pointer" : "default", textAlign: "left",
                      background: opt.ok && useSample === opt.val ? "rgba(16,185,129,0.12)" : "rgba(255,255,255,0.03)",
                      border: `1px solid ${opt.ok ? (useSample === opt.val ? "rgba(16,185,129,0.3)" : "rgba(255,255,255,0.08)") : "rgba(100,116,139,0.12)"}`,
                      opacity: opt.ok ? 1 : 0.4,
                    }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                      {opt.ok ? <CheckCircle size={10} color="#10b981" /> : <AlertTriangle size={10} color="#64748b" />}
                      <span style={{ fontSize: 11, fontWeight: 600, color: opt.ok ? "var(--text-primary)" : "var(--text-muted)" }}>{opt.label}</span>
                    </div>
                    <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 2, paddingLeft: 16 }}>{opt.desc}</div>
                  </button>
                ))}
              </div>
            )}
          </motion.div>

          {/* Scoring breakdown */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.08 }} className="glass-card" style={{ padding: 16 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
              <Brain size={13} color="#a78bfa" />
              <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                Scoring · {parsedJd ? "Custom JD" : "Default JD"}
              </span>
              {parsedJd && <span style={{ fontSize: 9, padding: "2px 6px", borderRadius: 20, background: "rgba(139,92,246,0.15)", color: "#a78bfa", fontWeight: 700, border: "1px solid rgba(139,92,246,0.25)" }}>✓ JD Applied</span>}
            </div>
            {[
              { label: "Skills Depth", pct: 40, color: "#7c3aed", desc: parsedJd ? `${parsedJd.core_skills_count} JD-specific core skills` : "Level + duration + endorsements + assessments" },
              { label: "Career Quality", pct: 30, color: "#06b6d4", desc: parsedJd ? `Exp: ${parsedJd.experience_range.ideal_min}–${parsedJd.experience_range.ideal_max}yr ideal` : "Product co. ratio, consulting penalty, trajectory" },
              { label: "Behavioral Signals", pct: 20, color: "#10b981", desc: "Activity, response rate, notice, open-to-work" },
              { label: "Platform Engagement", pct: 10, color: "#f59e0b", desc: "GitHub, recruiter saves, profile completeness" },
            ].map(({ label, pct, color, desc }) => (
              <div key={label} style={{ marginBottom: 9 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
                  <span style={{ fontSize: 11, fontWeight: 600 }}>{label}</span>
                  <span style={{ fontSize: 11, fontWeight: 700, color }}>{pct}%</span>
                </div>
                <div style={{ height: 4, borderRadius: 4, background: "rgba(255,255,255,0.06)", overflow: "hidden", marginBottom: 3 }}>
                  <div style={{ height: "100%", width: `${pct}%`, borderRadius: 4, background: color }} />
                </div>
                <p style={{ fontSize: 10, color: "var(--text-muted)", margin: 0 }}>{desc}</p>
              </div>
            ))}
            <div style={{ marginTop: 10, padding: "8px 10px", borderRadius: 8, background: "rgba(244,63,94,0.06)", border: "1px solid rgba(244,63,94,0.15)" }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: "#f43f5e", marginBottom: 4, textTransform: "uppercase" }}>🛡️ Anti-Gaming</div>
              <ul style={{ margin: 0, paddingLeft: 14, fontSize: 10, color: "var(--text-muted)", lineHeight: 1.7 }}>
                <li>Honeypots excluded (impossible profiles)</li>
                <li>Consulting-only career −15 pts</li>
                <li>Wrong-domain title −18 pts</li>
                <li>Title-chaser pattern −5 pts</li>
              </ul>
            </div>
          </motion.div>

          {/* ❸ Run Button */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.12 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 10 }}>
              <div style={{ width: 22, height: 22, borderRadius: 6, background: "rgba(16,185,129,0.2)", border: "1px solid rgba(16,185,129,0.4)", display: "flex", alignItems: "center", justifyContent: "center", fontSize: 11, fontWeight: 800, color: "#10b981" }}>3</div>
              <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Run Ranking</span>
            </div>

            <button id="run-challenge-btn" onClick={handleRun} disabled={running || !canRun} style={{
              width: "100%", padding: "13px 20px", borderRadius: 12, cursor: running || !canRun ? "not-allowed" : "pointer",
              background: running ? "rgba(245,158,11,0.2)" : !canRun ? "rgba(100,116,139,0.2)" : "linear-gradient(135deg,#d97706,#f59e0b)",
              border: "none", color: "white", fontSize: 13, fontWeight: 700,
              display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
              boxShadow: running || !canRun ? "none" : "0 4px 22px rgba(245,158,11,0.4)",
              transition: "all 0.2s",
            }}>
              {running
                ? <><Loader2 size={15} style={{ animation: "spin 0.8s linear infinite" }} /> Ranking...</>
                : !canRun
                ? <><Upload size={14} /> Upload candidates first</>
                : parsedJd
                ? <><Sparkles size={14} /> Run with Custom JD</>
                : <><Play size={14} fill="white" /> Run Challenge Ranking</>
              }
            </button>

            {running && uploadPct > 0 && uploadPct < 100 && (
              <div style={{ marginTop: 8 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4, fontSize: 11, color: "var(--text-muted)" }}>
                  <span>Uploading...</span><span>{uploadPct}%</span>
                </div>
                <div style={{ height: 4, borderRadius: 4, background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
                  <motion.div animate={{ width: `${uploadPct}%` }} style={{ height: "100%", borderRadius: 4, background: "#f59e0b" }} />
                </div>
              </div>
            )}
          </motion.div>
        </div>

        {/* ── RIGHT PANEL ───────────────────────────────────── */}
        <div>
          {/* Progress */}
          <AnimatePresence>
            {running && runStatus && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                className="glass-card" style={{ padding: 20, marginBottom: 14 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 14 }}>
                  <Activity size={15} color="#f59e0b" style={{ animation: "pulse 1s ease-in-out infinite alternate" }} />
                  <span style={{ fontSize: 13, fontWeight: 700, color: "#f59e0b" }}>
                    Ranking {parsedJd ? `against "${parsedJd.parsed_title.slice(0, 30)}..."` : "— Redrob AI Engineer profile"}
                  </span>
                </div>
                <div style={{ marginBottom: 12 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 5 }}>
                    <span style={{ fontSize: 11, color: "var(--text-muted)" }}>
                      {runStatus.processed.toLocaleString()} / {runStatus.total_candidates.toLocaleString()}
                    </span>
                    <span style={{ fontSize: 11, fontWeight: 700, color: "#f59e0b" }}>{progress.toFixed(1)}%</span>
                  </div>
                  <div style={{ height: 8, borderRadius: 8, background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
                    <motion.div animate={{ width: `${progress}%` }} transition={{ duration: 0.5 }} style={{
                      height: "100%", borderRadius: 8,
                      background: "linear-gradient(90deg,#d97706,#f59e0b,#fbbf24)",
                      boxShadow: "0 0 12px rgba(245,158,11,0.4)",
                    }} />
                  </div>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3,1fr)", gap: 10 }}>
                  {[
                    { icon: Users, label: "Processed", val: runStatus.processed.toLocaleString(), color: "#a78bfa" },
                    { icon: Shield, label: "Honeypots", val: String(runStatus.honeypots_detected), color: "#f43f5e" },
                    { icon: Zap, label: "Rate", val: runStatus.elapsed_seconds && runStatus.processed > 0 ? `${Math.round(runStatus.processed / runStatus.elapsed_seconds)}/s` : "—", color: "#10b981" },
                  ].map(({ icon: Icon, label, val, color }) => (
                    <div key={label} style={{ padding: "9px 12px", borderRadius: 10, background: "var(--bg-elevated)", border: "1px solid var(--border-subtle)", textAlign: "center" }}>
                      <Icon size={12} color={color} style={{ marginBottom: 3 }} />
                      <div style={{ fontSize: 15, fontWeight: 800, fontFamily: "'Space Grotesk',sans-serif", color }}>{val}</div>
                      <div style={{ fontSize: 10, color: "var(--text-muted)" }}>{label}</div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Error */}
          {error && (
            <div style={{ padding: "11px 14px", borderRadius: 10, marginBottom: 12, background: "rgba(244,63,94,0.08)", border: "1px solid rgba(244,63,94,0.25)", display: "flex", alignItems: "center", gap: 10 }}>
              <AlertTriangle size={14} color="#f43f5e" />
              <span style={{ fontSize: 12, color: "#f43f5e" }}>{error}</span>
            </div>
          )}

          {/* Complete banner */}
          <AnimatePresence>
            {isComplete && runStatus && (
              <motion.div initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }}
                className="glass-card" style={{ padding: 18, marginBottom: 14, background: "linear-gradient(135deg,rgba(245,158,11,0.12),rgba(16,185,129,0.08))", border: "1px solid rgba(245,158,11,0.3)" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                    <CheckCircle size={17} color="#10b981" />
                    <span style={{ fontSize: 14, fontWeight: 700, color: "#10b981" }}>
                      Ranking Complete · {runStatus.jd_provided ? "Custom JD" : "Default JD"}
                    </span>
                  </div>
                  <button onClick={() => challengeApi.download(runId!)} style={{
                    display: "flex", alignItems: "center", gap: 7,
                    padding: "8px 16px", borderRadius: 10, cursor: "pointer",
                    background: "linear-gradient(135deg,#059669,#10b981)", border: "none",
                    color: "white", fontSize: 12, fontWeight: 700, boxShadow: "0 4px 14px rgba(16,185,129,0.3)",
                  }}>
                    <Download size={13} /> Download submission.csv
                  </button>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 8 }}>
                  {[
                    { label: "Ranked", val: String(allResults.length), color: "#f59e0b", icon: Trophy },
                    { label: "Analyzed", val: runStatus.processed.toLocaleString(), color: "#a78bfa", icon: Users },
                    { label: "Honeypots", val: String(runStatus.honeypots_detected), color: "#f43f5e", icon: Shield },
                    { label: "Time", val: `${runStatus.elapsed_seconds?.toFixed(1)}s`, color: "#06b6d4", icon: Clock },
                  ].map(({ label, val, color, icon: Icon }) => (
                    <div key={label} style={{ padding: "9px 10px", borderRadius: 10, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", textAlign: "center" }}>
                      <Icon size={12} color={color} style={{ marginBottom: 3 }} />
                      <div style={{ fontSize: 16, fontWeight: 800, fontFamily: "'Space Grotesk',sans-serif", color }}>{val}</div>
                      <div style={{ fontSize: 10, color: "var(--text-muted)" }}>{label}</div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Results table */}
          {displayResults.length > 0 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 10 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <Award size={14} color="#f59e0b" />
                  <span style={{ fontSize: 13, fontWeight: 700 }}>Top {allResults.length} Ranked Candidates</span>
                  <span style={{ fontSize: 11, color: "var(--text-muted)" }}>· click for breakdown</span>
                </div>
                {allResults.length > 10 && (
                  <button onClick={() => setShowAll(!showAll)} style={{ display: "flex", alignItems: "center", gap: 5, padding: "5px 10px", borderRadius: 8, cursor: "pointer", background: "var(--bg-elevated)", border: "1px solid var(--border-subtle)", color: "var(--text-secondary)", fontSize: 11, fontWeight: 600 }}>
                    <Eye size={11} /> {showAll ? "Top 10" : `All ${allResults.length}`}
                  </button>
                )}
              </div>
              <div style={{ display: "flex", flexDirection: "column" }}>
                {displayResults.map((item, i) => (
                  <CandidateRow key={item.candidate_id} item={item} index={i}
                    expanded={expandedId === item.candidate_id}
                    onToggle={() => setExpandedId(expandedId === item.candidate_id ? null : item.candidate_id)} />
                ))}
              </div>
            </motion.div>
          )}

          {/* Empty state */}
          {!running && !isComplete && allResults.length === 0 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ textAlign: "center", padding: "60px 40px" }}>
              <Trophy size={44} color="rgba(245,158,11,0.3)" style={{ marginBottom: 14 }} />
              <div style={{ fontSize: 17, fontWeight: 700, marginBottom: 8, color: "var(--text-secondary)" }}>3 Steps to Rank</div>
              <div style={{ display: "flex", gap: 8, justifyContent: "center", flexWrap: "wrap", marginBottom: 16 }}>
                {[
                  { step: "1", text: "Upload JD file (optional)", color: "#a78bfa" },
                  { step: "2", text: "Upload candidates file", color: "#f59e0b" },
                  { step: "3", text: "Hit Run Ranking", color: "#10b981" },
                ].map(s => (
                  <div key={s.step} style={{ display: "flex", alignItems: "center", gap: 6, padding: "7px 12px", borderRadius: 20, background: `${s.color}12`, border: `1px solid ${s.color}40` }}>
                    <div style={{ width: 18, height: 18, borderRadius: "50%", background: `${s.color}20`, border: `1px solid ${s.color}50`, display: "flex", alignItems: "center", justifyContent: "center", fontSize: 10, fontWeight: 800, color: s.color }}>{s.step}</div>
                    <span style={{ fontSize: 11, fontWeight: 600, color: s.color }}>{s.text}</span>
                  </div>
                ))}
              </div>
              <p style={{ fontSize: 12, color: "var(--text-muted)", maxWidth: 360, margin: "0 auto", lineHeight: 1.7 }}>
                Upload any JD file (.docx, .txt, .md, .pdf) and the ranker auto-extracts skills, experience range, and seniority to build a custom scoring profile — no keyword gaming.
              </p>
            </motion.div>
          )}
        </div>
        </div>
      )}

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes pulse { from { opacity: 0.6; } to { opacity: 1; } }
        textarea:focus { border-color: rgba(139,92,246,0.4) !important; }
      `}</style>
    </div>
  );
}
