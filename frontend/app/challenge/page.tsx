"use client";

import { useEffect, useState, useRef, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Trophy, Target, Zap, Shield, Download, Play,
  CheckCircle, AlertTriangle, Loader2, FileText,
  Database, Brain, Activity, ChevronRight, Clock,
  Award, Upload, X, Eye, Users, FileUp
} from "lucide-react";
import { challengeApi } from "@/lib/api";

// ── Types ──────────────────────────────────────────────────────────────────────
type DatasetInfo = Awaited<ReturnType<typeof challengeApi.getInfo>>;
type RunStatus = Awaited<ReturnType<typeof challengeApi.getStatus>>;
type RankedItem = RunStatus["top_10_preview"][0];

// ── Score Bar ──────────────────────────────────────────────────────────────────
function ScoreBar({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  const pct = Math.min(100, (value / max) * 100);
  return (
    <div style={{ marginBottom: 8 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
        <span style={{ fontSize: 10, color: "var(--text-muted)", fontWeight: 500 }}>{label}</span>
        <span style={{ fontSize: 10, color, fontWeight: 700 }}>{value.toFixed(1)}/{max}</span>
      </div>
      <div style={{ height: 4, borderRadius: 4, background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
        <motion.div
          initial={{ width: 0 }} animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          style={{ height: "100%", borderRadius: 4, background: color }}
        />
      </div>
    </div>
  );
}

// ── Medal ──────────────────────────────────────────────────────────────────────
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
    <div style={{
      width: 28, height: 28, borderRadius: "50%", flexShrink: 0,
      background: medal.bg, border: `1px solid ${medal.border}`,
      display: "flex", alignItems: "center", justifyContent: "center", fontSize: 16,
    }}>{medal.emoji}</div>
  );
}

// ── Candidate Row ──────────────────────────────────────────────────────────────
function CandidateRow({ item, index, expanded, onToggle }: {
  item: RankedItem; index: number; expanded: boolean; onToggle: () => void;
}) {
  const scoreColor = item.score >= 0.7 ? "#10b981" : item.score >= 0.45 ? "#f59e0b" : "#f43f5e";
  return (
    <motion.div initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: index * 0.03 }}>
      <div onClick={onToggle} style={{
        padding: "13px 16px", borderRadius: expanded ? "12px 12px 0 0" : 12,
        background: expanded ? "rgba(124,58,237,0.08)" : "var(--bg-elevated)",
        border: `1px solid ${expanded ? "rgba(124,58,237,0.3)" : "var(--border-subtle)"}`,
        cursor: "pointer", display: "flex", alignItems: "center", gap: 12,
        transition: "all 0.2s", marginBottom: expanded ? 0 : 6,
      }}>
        <Medal rank={item.rank} />
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            <span style={{ fontWeight: 700, fontSize: 13 }}>{item.name || item.candidate_id}</span>
            <span style={{
              fontSize: 10, padding: "2px 7px", borderRadius: 6,
              background: "rgba(124,58,237,0.12)", border: "1px solid rgba(124,58,237,0.2)",
              color: "#a78bfa", fontWeight: 600,
            }}>{item.candidate_id}</span>
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {item.title}
          </div>
        </div>
        <div style={{ textAlign: "right", flexShrink: 0 }}>
          <div style={{ fontSize: 20, fontWeight: 800, fontFamily: "'Space Grotesk',sans-serif", color: scoreColor }}>
            {(item.score * 100).toFixed(1)}
          </div>
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
            <div style={{
              padding: "14px 16px 16px", borderRadius: "0 0 12px 12px",
              background: "rgba(124,58,237,0.05)", border: "1px solid rgba(124,58,237,0.2)",
              borderTop: "none", marginBottom: 6,
            }}>
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
              <div style={{ padding: "10px 12px", borderRadius: 8, background: "rgba(255,255,255,0.03)", border: "1px solid var(--border-subtle)" }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", marginBottom: 5, textTransform: "uppercase", letterSpacing: "0.06em" }}>Reasoning</div>
                <p style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.65, margin: 0 }}>{item.reasoning}</p>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
}

// ── Upload Zone ────────────────────────────────────────────────────────────────
function UploadZone({ onFile }: { onFile: (f: File) => void }) {
  const [dragging, setDragging] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setDragging(false);
    const f = e.dataTransfer.files[0];
    if (f) onFile(f);
  }, [onFile]);

  return (
    <div
      onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
      onDragLeave={() => setDragging(false)}
      onDrop={handleDrop}
      onClick={() => inputRef.current?.click()}
      style={{
        border: `2px dashed ${dragging ? "#f59e0b" : "rgba(245,158,11,0.35)"}`,
        borderRadius: 12, padding: "28px 20px", textAlign: "center",
        cursor: "pointer", transition: "all 0.2s",
        background: dragging ? "rgba(245,158,11,0.08)" : "rgba(245,158,11,0.03)",
      }}
    >
      <input ref={inputRef} type="file" accept=".json,.jsonl" style={{ display: "none" }}
        onChange={(e) => { const f = e.target.files?.[0]; if (f) onFile(f); }} />
      <FileUp size={28} color={dragging ? "#f59e0b" : "rgba(245,158,11,0.5)"} style={{ marginBottom: 10 }} />
      <div style={{ fontSize: 13, fontWeight: 700, color: "#fbbf24", marginBottom: 4 }}>
        Drop candidates file here
      </div>
      <div style={{ fontSize: 11, color: "var(--text-muted)", lineHeight: 1.6 }}>
        .json or .jsonl · candidates.jsonl, sample_candidates.json<br />
        <span style={{ color: "rgba(245,158,11,0.7)" }}>or click to browse</span>
      </div>
    </div>
  );
}

// ── Main Page ──────────────────────────────────────────────────────────────────
export default function ChallengePage() {
  const [info, setInfo] = useState<DatasetInfo | null>(null);
  const [infoLoading, setInfoLoading] = useState(true);

  const [useSample, setUseSample] = useState(false);
  const [uploadedFile, setUploadedFile] = useState<File | null>(null);
  const [uploadPct, setUploadPct] = useState(0);

  const [runId, setRunId] = useState<string | null>(null);
  const [runStatus, setRunStatus] = useState<RunStatus | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [allResults, setAllResults] = useState<RankedItem[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [showAll, setShowAll] = useState(false);

  // Load info
  useEffect(() => {
    challengeApi.getInfo()
      .then(d => { setInfo(d); setInfoLoading(false); })
      .catch(() => setInfoLoading(false));
  }, []);

  const hasLocalFull = !!info?.full_dataset?.available;
  const hasLocalSample = !!info?.sample_dataset?.available;
  const hasAnyLocal = hasLocalFull || hasLocalSample;

  // Determine mode: "local_full" | "local_sample" | "upload"
  // uploadedFile overrides everything
  const mode: "local_full" | "local_sample" | "upload" =
    uploadedFile ? "upload" :
    useSample && hasLocalSample ? "local_sample" :
    !useSample && hasLocalFull ? "local_full" : "upload";

  const canRun = mode === "upload" ? !!uploadedFile : true;

  async function handleRun() {
    if (running || !canRun) return;
    setRunning(true);
    setError(null);
    setRunStatus(null);
    setAllResults([]);
    setExpandedId(null);
    setUploadPct(0);

    try {
      let id: string;

      if (mode === "upload" && uploadedFile) {
        // Upload file then run
        const r = await challengeApi.uploadAndRun(uploadedFile, 0, setUploadPct);
        id = r.run_id;
      } else {
        // Use server-side file
        const r = await challengeApi.run(mode === "local_sample", 0);
        id = r.run_id;
      }

      setRunId(id);

      const final = await challengeApi.pollStatus(
        id,
        (processed, total, honeypots, status) => {
          setRunStatus(prev => ({
            ...(prev || {} as RunStatus),
            processed, total_candidates: total,
            honeypots_detected: honeypots, status,
          }));
        }
      );
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
    ? Math.min(100, (runStatus.processed / runStatus.total_candidates) * 100)
    : 0;

  const isComplete = runStatus?.status === "complete";
  const displayResults = showAll ? allResults : allResults.slice(0, 10);

  // ── Render ──────────────────────────────────────────────────────────────────
  return (
    <div style={{ maxWidth: 1100 }}>
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 28 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 4 }}>
          <div style={{
            width: 44, height: 44, borderRadius: 12, flexShrink: 0,
            background: "linear-gradient(135deg,rgba(245,158,11,0.2),rgba(251,191,36,0.1))",
            border: "1px solid rgba(245,158,11,0.4)",
            display: "flex", alignItems: "center", justifyContent: "center",
            boxShadow: "0 0 20px rgba(245,158,11,0.2)",
          }}>
            <Trophy size={22} color="#f59e0b" />
          </div>
          <div>
            <h1 style={{ fontSize: 26, fontWeight: 800, fontFamily: "'Space Grotesk',sans-serif", marginBottom: 2 }}>
              India Runs Challenge Ranker
            </h1>
            <p style={{ fontSize: 12, color: "var(--text-muted)" }}>
              Genuine multi-dimensional ranking · No keyword stuffing · NDCG-optimised · Honeypot-proof
            </p>
          </div>
        </div>
      </motion.div>

      <div style={{ display: "grid", gridTemplateColumns: isComplete ? "320px 1fr" : "320px 1fr", gap: 20, alignItems: "start" }}>

        {/* ── LEFT PANEL ─────────────────────────────────────────── */}
        <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>

          {/* Dataset Card */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card" style={{ padding: 18 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
              <Database size={14} color="#06b6d4" />
              <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Dataset</span>
            </div>

            {infoLoading ? (
              <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--text-muted)", fontSize: 12 }}>
                <Loader2 size={13} style={{ animation: "spin 0.8s linear infinite" }} /> Detecting...
              </div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 7 }}>
                {/* Full dataset status */}
                <div style={{
                  padding: "9px 12px", borderRadius: 9,
                  background: hasLocalFull ? "rgba(16,185,129,0.07)" : "rgba(100,116,139,0.07)",
                  border: `1px solid ${hasLocalFull ? "rgba(16,185,129,0.2)" : "rgba(100,116,139,0.12)"}`,
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    {hasLocalFull ? <CheckCircle size={11} color="#10b981" /> : <AlertTriangle size={11} color="#64748b" />}
                    <span style={{ fontSize: 11, fontWeight: 700, color: hasLocalFull ? "#10b981" : "var(--text-muted)" }}>
                      candidates.jsonl
                    </span>
                  </div>
                  <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 3 }}>
                    {hasLocalFull
                      ? `${info?.full_dataset?.estimated_candidates?.toLocaleString()} candidates · ${info?.full_dataset?.size_mb} MB`
                      : "Not on server — upload below"}
                  </div>
                </div>

                {/* Sample status */}
                <div style={{
                  padding: "9px 12px", borderRadius: 9,
                  background: hasLocalSample ? "rgba(6,182,212,0.07)" : "rgba(100,116,139,0.07)",
                  border: `1px solid ${hasLocalSample ? "rgba(6,182,212,0.2)" : "rgba(100,116,139,0.12)"}`,
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
                    {hasLocalSample ? <CheckCircle size={11} color="#06b6d4" /> : <AlertTriangle size={11} color="#64748b" />}
                    <span style={{ fontSize: 11, fontWeight: 700, color: hasLocalSample ? "#06b6d4" : "var(--text-muted)" }}>
                      sample_candidates.json
                    </span>
                  </div>
                  <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 3 }}>
                    {hasLocalSample
                      ? `${info?.sample_dataset?.candidate_count} candidates · embedded`
                      : "Not found"}
                  </div>
                </div>
              </div>
            )}
          </motion.div>

          {/* Upload Zone / File Selected */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.04 }} className="glass-card" style={{ padding: 18 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
              <Upload size={14} color="#f59e0b" />
              <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Upload Your File</span>
              <span style={{
                fontSize: 9, padding: "2px 7px", borderRadius: 20,
                background: "rgba(16,185,129,0.12)", border: "1px solid rgba(16,185,129,0.2)",
                color: "#10b981", fontWeight: 700,
              }}>Works on Render</span>
            </div>

            {uploadedFile ? (
              <div style={{
                padding: "12px 14px", borderRadius: 10,
                background: "rgba(16,185,129,0.08)", border: "1px solid rgba(16,185,129,0.25)",
                display: "flex", alignItems: "center", gap: 10,
              }}>
                <FileText size={16} color="#10b981" style={{ flexShrink: 0 }} />
                <div style={{ flex: 1, minWidth: 0 }}>
                  <div style={{ fontSize: 12, fontWeight: 700, color: "#10b981", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                    {uploadedFile.name}
                  </div>
                  <div style={{ fontSize: 10, color: "var(--text-muted)" }}>
                    {(uploadedFile.size / (1024 * 1024)).toFixed(1)} MB
                  </div>
                </div>
                <button onClick={() => setUploadedFile(null)} style={{
                  width: 24, height: 24, borderRadius: 6, border: "none",
                  background: "rgba(244,63,94,0.15)", color: "#f43f5e", cursor: "pointer",
                  display: "flex", alignItems: "center", justifyContent: "center",
                }}>
                  <X size={12} />
                </button>
              </div>
            ) : (
              <UploadZone onFile={setUploadedFile} />
            )}

            {uploadedFile && (
              <p style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 8, textAlign: "center" }}>
                Will rank all candidates in this file · overrides server-side files
              </p>
            )}
          </motion.div>

          {/* Mode select — only shown when server files exist */}
          {hasAnyLocal && !uploadedFile && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.06 }} className="glass-card" style={{ padding: 18 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                <Target size={14} color="#a78bfa" />
                <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Server Files</span>
              </div>
              <div style={{ display: "flex", gap: 8 }}>
                {[
                  { val: false, label: "Full Dataset", sub: "100k candidates", color: "#10b981", ok: hasLocalFull },
                  { val: true, label: "Sample Mode", sub: `${info?.sample_dataset?.candidate_count || 50} candidates`, color: "#06b6d4", ok: hasLocalSample },
                ].map(opt => (
                  <button key={String(opt.val)} onClick={() => setUseSample(opt.val)} disabled={!opt.ok}
                    style={{
                      flex: 1, padding: "10px 8px", borderRadius: 10,
                      cursor: opt.ok ? "pointer" : "not-allowed",
                      background: useSample === opt.val ? `${opt.color}20` : "var(--bg-elevated)",
                      border: `1px solid ${useSample === opt.val ? opt.color + "60" : "var(--border-subtle)"}`,
                      opacity: opt.ok ? 1 : 0.35, transition: "all 0.2s",
                    }}>
                    <div style={{ fontSize: 12, fontWeight: 700, color: useSample === opt.val ? opt.color : "var(--text-secondary)", marginBottom: 2 }}>{opt.label}</div>
                    <div style={{ fontSize: 10, color: "var(--text-muted)" }}>{opt.sub}</div>
                  </button>
                ))}
              </div>
            </motion.div>
          )}

          {/* Scoring breakdown */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.08 }} className="glass-card" style={{ padding: 18 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
              <Brain size={14} color="#a78bfa" />
              <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Scoring Dimensions</span>
            </div>
            {[
              { label: "Skills Depth", pct: 40, color: "#7c3aed", desc: "Level + duration + endorsements + assessments" },
              { label: "Career Quality", pct: 30, color: "#06b6d4", desc: "Product co. ratio, consulting penalty, trajectory" },
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
            <div style={{ marginTop: 10, padding: "9px 12px", borderRadius: 8, background: "rgba(244,63,94,0.06)", border: "1px solid rgba(244,63,94,0.15)" }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: "#f43f5e", marginBottom: 4, textTransform: "uppercase" }}>🛡️ Anti-Gaming</div>
              <ul style={{ margin: 0, paddingLeft: 14, fontSize: 10, color: "var(--text-muted)", lineHeight: 1.7 }}>
                <li>Honeypots excluded (impossible profiles)</li>
                <li>Consulting-only career −15 pts</li>
                <li>Wrong-domain title penalty −18 pts</li>
                <li>Title-chaser pattern −5 pts</li>
              </ul>
            </div>
          </motion.div>

          {/* JD Summary */}
          {info?.job_description_summary && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card" style={{ padding: 18 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                <FileText size={14} color="#f59e0b" />
                <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Target Role</span>
              </div>
              <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 1 }}>{info.job_description_summary.title}</div>
              <div style={{ fontSize: 11, color: "#f59e0b", marginBottom: 10 }}>{info.job_description_summary.company}</div>
              <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", marginBottom: 5, textTransform: "uppercase" }}>Must-Have</div>
              {info.job_description_summary.must_have.map(s => (
                <div key={s} style={{ display: "flex", alignItems: "flex-start", gap: 6, marginBottom: 4 }}>
                  <CheckCircle size={10} color="#10b981" style={{ marginTop: 1, flexShrink: 0 }} />
                  <span style={{ fontSize: 10, color: "var(--text-secondary)", lineHeight: 1.5 }}>{s}</span>
                </div>
              ))}
              <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", margin: "9px 0 5px", textTransform: "uppercase" }}>Disqualifiers</div>
              {info.job_description_summary.disqualifiers.map(s => (
                <div key={s} style={{ display: "flex", alignItems: "flex-start", gap: 6, marginBottom: 4 }}>
                  <AlertTriangle size={10} color="#f43f5e" style={{ marginTop: 1, flexShrink: 0 }} />
                  <span style={{ fontSize: 10, color: "var(--text-secondary)", lineHeight: 1.5 }}>{s}</span>
                </div>
              ))}
            </motion.div>
          )}

          {/* Run Button */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.12 }}>
            <button
              id="run-challenge-btn"
              onClick={handleRun}
              disabled={running || !canRun}
              style={{
                width: "100%", padding: "14px 20px", borderRadius: 12,
                cursor: running || !canRun ? "not-allowed" : "pointer",
                background: running
                  ? "rgba(245,158,11,0.2)"
                  : !canRun
                  ? "rgba(100,116,139,0.2)"
                  : "linear-gradient(135deg,#d97706,#f59e0b)",
                border: "none", color: "white", fontSize: 14, fontWeight: 700,
                display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
                boxShadow: running || !canRun ? "none" : "0 4px 22px rgba(245,158,11,0.4)",
                transition: "all 0.2s",
              }}>
              {running
                ? <><Loader2 size={16} style={{ animation: "spin 0.8s linear infinite" }} /> Ranking...</>
                : !canRun
                ? <><Upload size={15} /> Upload a file to continue</>
                : <><Play size={15} fill="white" /> Run Challenge Ranking</>
              }
            </button>
            {running && uploadPct > 0 && uploadPct < 100 && (
              <div style={{ marginTop: 8 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4, fontSize: 11, color: "var(--text-muted)" }}>
                  <span>Uploading file...</span><span>{uploadPct}%</span>
                </div>
                <div style={{ height: 4, borderRadius: 4, background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
                  <motion.div animate={{ width: `${uploadPct}%` }} style={{ height: "100%", borderRadius: 4, background: "#f59e0b" }} />
                </div>
              </div>
            )}
          </motion.div>
        </div>

        {/* ── RIGHT PANEL ───────────────────────────────────────── */}
        <div>
          {/* Progress */}
          <AnimatePresence>
            {running && runStatus && (
              <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}
                className="glass-card" style={{ padding: 22, marginBottom: 16 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
                  <Activity size={16} color="#f59e0b" style={{ animation: "pulse 1s ease-in-out infinite alternate" }} />
                  <span style={{ fontSize: 14, fontWeight: 700, color: "#f59e0b" }}>Ranking in progress...</span>
                </div>
                <div style={{ marginBottom: 14 }}>
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
                    { icon: Zap, label: "Rate", val: runStatus.elapsed_seconds && runStatus.processed > 0
                        ? `${Math.round(runStatus.processed / runStatus.elapsed_seconds)}/s` : "—", color: "#10b981" },
                  ].map(({ icon: Icon, label, val, color }) => (
                    <div key={label} style={{ padding: "10px 12px", borderRadius: 10, background: "var(--bg-elevated)", border: "1px solid var(--border-subtle)", textAlign: "center" }}>
                      <Icon size={13} color={color} style={{ marginBottom: 4 }} />
                      <div style={{ fontSize: 16, fontWeight: 800, fontFamily: "'Space Grotesk',sans-serif", color }}>{val}</div>
                      <div style={{ fontSize: 10, color: "var(--text-muted)" }}>{label}</div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Error */}
          {error && (
            <div style={{ padding: "12px 16px", borderRadius: 10, marginBottom: 14, background: "rgba(244,63,94,0.08)", border: "1px solid rgba(244,63,94,0.25)", display: "flex", alignItems: "center", gap: 10 }}>
              <AlertTriangle size={15} color="#f43f5e" />
              <span style={{ fontSize: 12, color: "#f43f5e" }}>{error}</span>
            </div>
          )}

          {/* Complete banner */}
          <AnimatePresence>
            {isComplete && runStatus && (
              <motion.div initial={{ opacity: 0, scale: 0.97 }} animate={{ opacity: 1, scale: 1 }}
                className="glass-card" style={{ padding: 20, marginBottom: 16, background: "linear-gradient(135deg,rgba(245,158,11,0.12),rgba(16,185,129,0.08))", border: "1px solid rgba(245,158,11,0.3)" }}>
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <CheckCircle size={18} color="#10b981" />
                    <span style={{ fontSize: 15, fontWeight: 700, color: "#10b981" }}>Ranking Complete!</span>
                  </div>
                  <button onClick={() => challengeApi.download(runId!)} style={{
                    display: "flex", alignItems: "center", gap: 8,
                    padding: "9px 18px", borderRadius: 10, cursor: "pointer",
                    background: "linear-gradient(135deg,#059669,#10b981)",
                    border: "none", color: "white", fontSize: 12, fontWeight: 700,
                    boxShadow: "0 4px 14px rgba(16,185,129,0.3)",
                  }}>
                    <Download size={13} /> Download submission.csv
                  </button>
                </div>
                <div style={{ display: "grid", gridTemplateColumns: "repeat(4,1fr)", gap: 10 }}>
                  {[
                    { label: "Ranked", val: String(allResults.length), color: "#f59e0b", icon: Trophy },
                    { label: "Analyzed", val: runStatus.processed.toLocaleString(), color: "#a78bfa", icon: Users },
                    { label: "Honeypots", val: String(runStatus.honeypots_detected), color: "#f43f5e", icon: Shield },
                    { label: "Time", val: `${runStatus.elapsed_seconds?.toFixed(1)}s`, color: "#06b6d4", icon: Clock },
                  ].map(({ label, val, color, icon: Icon }) => (
                    <div key={label} style={{ padding: "10px 12px", borderRadius: 10, background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", textAlign: "center" }}>
                      <Icon size={13} color={color} style={{ marginBottom: 4 }} />
                      <div style={{ fontSize: 18, fontWeight: 800, fontFamily: "'Space Grotesk',sans-serif", color }}>{val}</div>
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
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 12 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <Award size={15} color="#f59e0b" />
                  <span style={{ fontSize: 13, fontWeight: 700 }}>Top {allResults.length} Ranked Candidates</span>
                  <span style={{ fontSize: 11, color: "var(--text-muted)" }}>· click row for score breakdown</span>
                </div>
                {allResults.length > 10 && (
                  <button onClick={() => setShowAll(!showAll)} style={{
                    display: "flex", alignItems: "center", gap: 5,
                    padding: "5px 11px", borderRadius: 8, cursor: "pointer",
                    background: "var(--bg-elevated)", border: "1px solid var(--border-subtle)",
                    color: "var(--text-secondary)", fontSize: 11, fontWeight: 600,
                  }}>
                    <Eye size={11} /> {showAll ? "Show Top 10" : `Show All ${allResults.length}`}
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
              <Trophy size={48} color="rgba(245,158,11,0.3)" style={{ marginBottom: 14 }} />
              <div style={{ fontSize: 17, fontWeight: 700, marginBottom: 8, color: "var(--text-secondary)" }}>Ready to Rank</div>
              <p style={{ fontSize: 12, lineHeight: 1.7, maxWidth: 340, margin: "0 auto 18px", color: "var(--text-muted)" }}>
                {!canRun
                  ? <>Upload your <strong style={{ color: "#f59e0b" }}>candidates.jsonl</strong> or <strong style={{ color: "#f59e0b" }}>sample_candidates.json</strong> using the upload zone on the left, then hit Run.</>
                  : <>Hit <strong style={{ color: "#f59e0b" }}>Run Challenge Ranking</strong> to score all candidates across 4 dimensions — no keyword gaming.</>
                }
              </p>
              <div style={{ display: "flex", gap: 10, justifyContent: "center", flexWrap: "wrap" }}>
                {["NDCG@10 optimised", "Drag & drop upload", "Honeypot-proof", "~1700 cands/sec"].map(t => (
                  <span key={t} style={{ fontSize: 10, padding: "4px 11px", borderRadius: 20, background: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.2)", color: "#fbbf24", fontWeight: 600 }}>{t}</span>
                ))}
              </div>
            </motion.div>
          )}
        </div>
      </div>

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
        @keyframes pulse { from { opacity: 0.6; } to { opacity: 1; } }
      `}</style>
    </div>
  );
}
