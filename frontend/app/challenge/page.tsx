"use client";

import { useEffect, useState, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Trophy, Target, Zap, Shield, TrendingUp, Users,
  Download, Play, CheckCircle, AlertTriangle, Loader2,
  FileText, Database, Brain, Activity, ChevronRight,
  BarChart2, Clock, Star, Award, Info, RefreshCw, Eye
} from "lucide-react";
import { challengeApi } from "@/lib/api";

// ── Types ──────────────────────────────────────────────────────────────────────

type DatasetInfo = Awaited<ReturnType<typeof challengeApi.getInfo>>;
type RunStatus = Awaited<ReturnType<typeof challengeApi.getStatus>>;
type RankedItem = RunStatus["top_10_preview"][0];

// ── Score Bar Component ────────────────────────────────────────────────────────

function ScoreBar({ label, value, max, color }: { label: string; value: number; max: number; color: string }) {
  const pct = Math.min(100, (value / max) * 100);
  return (
    <div style={{ marginBottom: 6 }}>
      <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 3 }}>
        <span style={{ fontSize: 10, color: "var(--text-muted)", fontWeight: 500 }}>{label}</span>
        <span style={{ fontSize: 10, color, fontWeight: 700 }}>{value.toFixed(1)}/{max}</span>
      </div>
      <div style={{
        height: 4, borderRadius: 4,
        background: "rgba(255,255,255,0.06)",
        overflow: "hidden",
      }}>
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${pct}%` }}
          transition={{ duration: 0.8, ease: "easeOut" }}
          style={{ height: "100%", borderRadius: 4, background: color }}
        />
      </div>
    </div>
  );
}

// ── Medal Badges ───────────────────────────────────────────────────────────────

function MedalBadge({ rank }: { rank: number }) {
  const medals: Record<number, { bg: string; border: string; emoji: string }> = {
    1: { bg: "rgba(251,191,36,0.15)", border: "rgba(251,191,36,0.4)", emoji: "🥇" },
    2: { bg: "rgba(148,163,184,0.15)", border: "rgba(148,163,184,0.4)", emoji: "🥈" },
    3: { bg: "rgba(180,120,80,0.15)", border: "rgba(180,120,80,0.4)", emoji: "🥉" },
  };
  const m = medals[rank];
  if (!m) {
    return (
      <div style={{
        width: 28, height: 28, borderRadius: "50%",
        background: "rgba(124,58,237,0.1)", border: "1px solid rgba(124,58,237,0.2)",
        display: "flex", alignItems: "center", justifyContent: "center",
        fontSize: 11, fontWeight: 700, color: "#a78bfa", flexShrink: 0,
      }}>
        {rank}
      </div>
    );
  }
  return (
    <div style={{
      width: 28, height: 28, borderRadius: "50%",
      background: m.bg, border: `1px solid ${m.border}`,
      display: "flex", alignItems: "center", justifyContent: "center",
      fontSize: 16, flexShrink: 0,
    }}>
      {m.emoji}
    </div>
  );
}

// ── Candidate Row ──────────────────────────────────────────────────────────────

function CandidateRow({ item, index, expanded, onToggle }: {
  item: RankedItem; index: number; expanded: boolean; onToggle: () => void;
}) {
  const scoreColor = item.score >= 0.7 ? "#10b981" : item.score >= 0.45 ? "#f59e0b" : "#f43f5e";

  return (
    <motion.div
      initial={{ opacity: 0, y: 8 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay: index * 0.04 }}
    >
      <div
        onClick={onToggle}
        style={{
          padding: "14px 18px",
          borderRadius: expanded ? "12px 12px 0 0" : 12,
          background: expanded
            ? "rgba(124,58,237,0.08)"
            : "var(--bg-elevated)",
          border: `1px solid ${expanded ? "rgba(124,58,237,0.3)" : "var(--border-subtle)"}`,
          cursor: "pointer",
          display: "flex",
          alignItems: "center",
          gap: 12,
          transition: "all 0.2s ease",
          marginBottom: expanded ? 0 : 6,
        }}
      >
        <MedalBadge rank={item.rank} />

        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, flexWrap: "wrap" }}>
            <span style={{ fontWeight: 700, fontSize: 13 }}>
              {item.name || item.candidate_id}
            </span>
            <span style={{
              fontSize: 10, padding: "2px 7px", borderRadius: 6,
              background: "rgba(124,58,237,0.12)", border: "1px solid rgba(124,58,237,0.2)",
              color: "#a78bfa", fontWeight: 600,
            }}>
              {item.candidate_id}
            </span>
          </div>
          <div style={{ fontSize: 11, color: "var(--text-muted)", marginTop: 2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {item.title}
          </div>
        </div>

        <div style={{ textAlign: "right", flexShrink: 0 }}>
          <div style={{ fontSize: 18, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif", color: scoreColor }}>
            {(item.score * 100).toFixed(1)}
          </div>
          <div style={{ fontSize: 9, color: "var(--text-muted)", fontWeight: 600 }}>/ 100</div>
        </div>

        <div style={{
          transform: `rotate(${expanded ? 90 : 0}deg)`,
          transition: "transform 0.2s ease",
          color: "var(--text-muted)",
        }}>
          <ChevronRight size={14} />
        </div>
      </div>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.25 }}
            style={{ overflow: "hidden" }}
          >
            <div style={{
              padding: "14px 18px 16px",
              borderRadius: "0 0 12px 12px",
              background: "rgba(124,58,237,0.05)",
              border: "1px solid rgba(124,58,237,0.2)",
              borderTop: "none",
              marginBottom: 6,
            }}>
              {/* Score breakdown */}
              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 14 }}>
                <div>
                  <ScoreBar label="Skills Depth" value={item.skills_score} max={40} color="#7c3aed" />
                  <ScoreBar label="Career Quality" value={item.career_score} max={30} color="#06b6d4" />
                </div>
                <div>
                  <ScoreBar label="Behavioral Signals" value={item.behavioral_score} max={20} color="#10b981" />
                  <ScoreBar label="Platform Engagement" value={item.engagement_score} max={10} color="#f59e0b" />
                </div>
              </div>

              {/* Reasoning */}
              <div style={{
                padding: "10px 14px",
                borderRadius: 8,
                background: "rgba(255,255,255,0.03)",
                border: "1px solid var(--border-subtle)",
              }}>
                <div style={{ fontSize: 10, fontWeight: 700, color: "var(--text-muted)", marginBottom: 6, textTransform: "uppercase", letterSpacing: "0.06em" }}>
                  AI Reasoning
                </div>
                <p style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.6, margin: 0 }}>
                  {item.reasoning}
                </p>
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
  const [infoError, setInfoError] = useState<string | null>(null);

  const [useSample, setUseSample] = useState(false);
  const [runId, setRunId] = useState<string | null>(null);
  const [runStatus, setRunStatus] = useState<RunStatus | null>(null);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [allResults, setAllResults] = useState<RankedItem[]>([]);
  const [expandedId, setExpandedId] = useState<string | null>(null);
  const [showAll, setShowAll] = useState(false);

  const pollRef = useRef<boolean>(false);
  const progressRef = useRef<{ processed: number; total: number }>({ processed: 0, total: 0 });

  // Load dataset info on mount
  useEffect(() => {
    challengeApi.getInfo()
      .then(d => { setInfo(d); setInfoLoading(false); })
      .catch(e => { setInfoError(e.message); setInfoLoading(false); });
  }, []);

  // Start ranking run
  async function handleRun() {
    if (running) return;
    setRunning(true);
    setError(null);
    setRunStatus(null);
    setAllResults([]);
    setExpandedId(null);
    pollRef.current = true;

    try {
      const { run_id } = await challengeApi.run(useSample, 0);
      setRunId(run_id);

      // Poll
      const finalStatus = await challengeApi.pollStatus(
        run_id,
        (processed, total, honeypots, status) => {
          progressRef.current = { processed, total };
          setRunStatus(prev => ({
            ...(prev || {} as RunStatus),
            processed, total_candidates: total,
            honeypots_detected: honeypots, status,
          }));
        }
      );
      setRunStatus(finalStatus);

      // Fetch full results
      const fullResults = await challengeApi.getResults(run_id);
      setAllResults(fullResults.results);
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Ranking failed");
    } finally {
      setRunning(false);
      pollRef.current = false;
    }
  }

  const progress = runStatus
    ? Math.min(100, runStatus.total_candidates > 0
        ? (runStatus.processed / runStatus.total_candidates) * 100
        : 0)
    : 0;

  const displayResults = showAll ? allResults : allResults.slice(0, 10);
  const isComplete = runStatus?.status === "complete";
  const hasDataset = info?.full_dataset?.available || info?.sample_dataset?.available;

  return (
    <div style={{ maxWidth: 1100 }}>
      {/* ── Page Header ──────────────────────────────────────────── */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 28 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 6 }}>
          <div style={{
            width: 44, height: 44, borderRadius: 12, flexShrink: 0,
            background: "linear-gradient(135deg, rgba(245,158,11,0.2), rgba(251,191,36,0.1))",
            border: "1px solid rgba(245,158,11,0.4)",
            display: "flex", alignItems: "center", justifyContent: "center",
            boxShadow: "0 0 20px rgba(245,158,11,0.2)",
          }}>
            <Trophy size={22} color="#f59e0b" />
          </div>
          <div>
            <h1 style={{ fontSize: 28, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif", marginBottom: 2 }}>
              India Runs Challenge Ranker
            </h1>
            <p style={{ fontSize: 13, color: "var(--text-muted)" }}>
              Genuine multi-dimensional ranking · 100k candidates · No keyword stuffing · NDCG-optimised
            </p>
          </div>
        </div>
      </motion.div>

      <div style={{ display: "grid", gridTemplateColumns: isComplete ? "340px 1fr" : "1fr", gap: 20, alignItems: "start" }}>

        {/* ── Left Panel ────────────────────────────────────────── */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>

          {/* Dataset Status Card */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} className="glass-card" style={{ padding: 20 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
              <Database size={15} color="#06b6d4" />
              <span style={{ fontSize: 12, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>Dataset Files</span>
            </div>

            {infoLoading ? (
              <div style={{ display: "flex", alignItems: "center", gap: 8, color: "var(--text-muted)", fontSize: 13 }}>
                <Loader2 size={14} style={{ animation: "spin 0.8s linear infinite" }} />
                Detecting files...
              </div>
            ) : infoError ? (
              <div style={{ color: "#f43f5e", fontSize: 12 }}>Backend offline — start the API server</div>
            ) : (
              <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
                {/* Full dataset */}
                <div style={{
                  padding: "10px 14px", borderRadius: 10,
                  background: info?.full_dataset?.available ? "rgba(16,185,129,0.07)" : "rgba(100,116,139,0.07)",
                  border: `1px solid ${info?.full_dataset?.available ? "rgba(16,185,129,0.2)" : "rgba(100,116,139,0.15)"}`,
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                    {info?.full_dataset?.available
                      ? <CheckCircle size={12} color="#10b981" />
                      : <AlertTriangle size={12} color="#64748b" />}
                    <span style={{ fontSize: 12, fontWeight: 700, color: info?.full_dataset?.available ? "#10b981" : "var(--text-muted)" }}>
                      candidates.jsonl
                    </span>
                  </div>
                  {info?.full_dataset?.available ? (
                    <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                      {info.full_dataset.estimated_candidates.toLocaleString()} candidates · {info.full_dataset.size_mb} MB
                    </div>
                  ) : (
                    <div style={{ fontSize: 11, color: "var(--text-muted)" }}>Not found — place in India_runs_data_and_ai_challenge/</div>
                  )}
                </div>

                {/* Sample dataset */}
                <div style={{
                  padding: "10px 14px", borderRadius: 10,
                  background: info?.sample_dataset?.available ? "rgba(6,182,212,0.07)" : "rgba(100,116,139,0.07)",
                  border: `1px solid ${info?.sample_dataset?.available ? "rgba(6,182,212,0.2)" : "rgba(100,116,139,0.15)"}`,
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 4 }}>
                    {info?.sample_dataset?.available
                      ? <CheckCircle size={12} color="#06b6d4" />
                      : <AlertTriangle size={12} color="#64748b" />}
                    <span style={{ fontSize: 12, fontWeight: 700, color: info?.sample_dataset?.available ? "#06b6d4" : "var(--text-muted)" }}>
                      sample_candidates.json
                    </span>
                  </div>
                  {info?.sample_dataset?.available && (
                    <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                      {info.sample_dataset.candidate_count} candidates · Quick test mode
                    </div>
                  )}
                </div>
              </div>
            )}
          </motion.div>

          {/* Scoring Methodology Card */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.05 }} className="glass-card" style={{ padding: 20 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
              <Brain size={15} color="#a78bfa" />
              <span style={{ fontSize: 12, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                Scoring Dimensions
              </span>
            </div>

            {[
              { label: "Skills Depth", pct: 40, color: "#7c3aed", desc: "Level + duration + endorsements + assessment scores" },
              { label: "Career Quality", pct: 30, color: "#06b6d4", desc: "Product co. ratio, consulting penalty, trajectory" },
              { label: "Behavioral Signals", pct: 20, color: "#10b981", desc: "Activity, response rate, notice period, open-to-work" },
              { label: "Platform Engagement", pct: 10, color: "#f59e0b", desc: "GitHub, saved by recruiters, profile completeness" },
            ].map(({ label, pct, color, desc }) => (
              <div key={label} style={{ marginBottom: 10 }}>
                <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                  <span style={{ fontSize: 12, fontWeight: 600, color: "var(--text-primary)" }}>{label}</span>
                  <span style={{ fontSize: 11, fontWeight: 700, color }}>{pct}%</span>
                </div>
                <div style={{ height: 4, borderRadius: 4, background: "rgba(255,255,255,0.06)", overflow: "hidden", marginBottom: 4 }}>
                  <div style={{ height: "100%", width: `${pct}%`, borderRadius: 4, background: color }} />
                </div>
                <p style={{ fontSize: 10, color: "var(--text-muted)", margin: 0 }}>{desc}</p>
              </div>
            ))}

            {/* Anti-gaming notice */}
            <div style={{
              marginTop: 12, padding: "10px 12px", borderRadius: 8,
              background: "rgba(244,63,94,0.06)", border: "1px solid rgba(244,63,94,0.15)",
            }}>
              <div style={{ fontSize: 10, fontWeight: 700, color: "#f43f5e", marginBottom: 4, textTransform: "uppercase" }}>
                🛡️ Anti-Gaming Measures
              </div>
              <ul style={{ margin: 0, paddingLeft: 14, fontSize: 11, color: "var(--text-muted)", lineHeight: 1.7 }}>
                <li>Honeypot detection (impossible profiles → excluded)</li>
                <li>Consulting-only career penalty (−10 pts)</li>
                <li>Title mismatch penalty (marketing manager + AI skills)</li>
                <li>Title-chaser pattern detection</li>
                <li>CV/speech-only domain penalty</li>
              </ul>
            </div>
          </motion.div>

          {/* JD Summary Card */}
          {info?.job_description_summary && (
            <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }} className="glass-card" style={{ padding: 20 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
                <FileText size={15} color="#f59e0b" />
                <span style={{ fontSize: 12, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                  Target Role
                </span>
              </div>
              <div style={{ fontSize: 13, fontWeight: 700, marginBottom: 2 }}>{info.job_description_summary.title}</div>
              <div style={{ fontSize: 11, color: "#f59e0b", marginBottom: 10 }}>{info.job_description_summary.company}</div>

              <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", marginBottom: 6, textTransform: "uppercase" }}>Must-Have Skills</div>
              {info.job_description_summary.must_have.map(s => (
                <div key={s} style={{ display: "flex", alignItems: "flex-start", gap: 6, marginBottom: 4 }}>
                  <CheckCircle size={11} color="#10b981" style={{ marginTop: 1, flexShrink: 0 }} />
                  <span style={{ fontSize: 11, color: "var(--text-secondary)", lineHeight: 1.5 }}>{s}</span>
                </div>
              ))}

              <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", margin: "10px 0 6px", textTransform: "uppercase" }}>Disqualifiers</div>
              {info.job_description_summary.disqualifiers.map(s => (
                <div key={s} style={{ display: "flex", alignItems: "flex-start", gap: 6, marginBottom: 4 }}>
                  <AlertTriangle size={11} color="#f43f5e" style={{ marginTop: 1, flexShrink: 0 }} />
                  <span style={{ fontSize: 11, color: "var(--text-secondary)", lineHeight: 1.5 }}>{s}</span>
                </div>
              ))}
            </motion.div>
          )}

          {/* Run Configuration */}
          <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }} className="glass-card" style={{ padding: 20 }}>
            <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
              <Target size={15} color="#a78bfa" />
              <span style={{ fontSize: 12, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
                Run Configuration
              </span>
            </div>

            {/* Mode toggle */}
            <div style={{ display: "flex", gap: 8, marginBottom: 16 }}>
              {[
                { val: false, label: "Full Dataset", sub: "100k candidates", color: "#10b981", available: !!info?.full_dataset?.available },
                { val: true, label: "Sample Mode", sub: `${info?.sample_dataset?.candidate_count || 100} candidates`, color: "#06b6d4", available: !!info?.sample_dataset?.available },
              ].map(opt => (
                <button
                  key={String(opt.val)}
                  onClick={() => setUseSample(opt.val)}
                  disabled={!opt.available}
                  style={{
                    flex: 1, padding: "10px 8px", borderRadius: 10, cursor: opt.available ? "pointer" : "not-allowed",
                    background: useSample === opt.val
                      ? `${opt.color}20`
                      : "var(--bg-elevated)",
                    border: `1px solid ${useSample === opt.val ? opt.color + "60" : "var(--border-subtle)"}`,
                    opacity: opt.available ? 1 : 0.4,
                    transition: "all 0.2s ease",
                  }}
                >
                  <div style={{ fontSize: 12, fontWeight: 700, color: useSample === opt.val ? opt.color : "var(--text-secondary)", marginBottom: 2 }}>
                    {opt.label}
                  </div>
                  <div style={{ fontSize: 10, color: "var(--text-muted)" }}>{opt.sub}</div>
                </button>
              ))}
            </div>

            {/* Run button */}
            <button
              id="run-challenge-btn"
              onClick={handleRun}
              disabled={running || !hasDataset}
              style={{
                width: "100%", padding: "13px 20px",
                borderRadius: 12, cursor: running || !hasDataset ? "not-allowed" : "pointer",
                background: running
                  ? "rgba(245,158,11,0.2)"
                  : !hasDataset
                  ? "rgba(100,116,139,0.2)"
                  : "linear-gradient(135deg, #d97706, #f59e0b)",
                border: "none", color: "white", fontSize: 14, fontWeight: 700,
                display: "flex", alignItems: "center", justifyContent: "center", gap: 10,
                boxShadow: running || !hasDataset ? "none" : "0 4px 20px rgba(245,158,11,0.35)",
                transition: "all 0.2s ease",
              }}
            >
              {running
                ? <><Loader2 size={16} style={{ animation: "spin 0.8s linear infinite" }} /> Ranking in progress...</>
                : !hasDataset
                ? <>⚠️ No Dataset Found</>
                : <><Play size={16} fill="white" /> Run Challenge Ranking</>
              }
            </button>

            {!hasDataset && (
              <p style={{ fontSize: 11, color: "#f59e0b", marginTop: 8, textAlign: "center" }}>
                Place candidates.jsonl in the India_runs_data_and_ai_challenge/ folder
              </p>
            )}
          </motion.div>
        </div>

        {/* ── Right Panel: Results ──────────────────────────────── */}
        <div>
          {/* Progress Panel (during run) */}
          <AnimatePresence>
            {running && runStatus && (
              <motion.div
                initial={{ opacity: 0, y: 10 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="glass-card"
                style={{ padding: 24, marginBottom: 16 }}
              >
                <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 16 }}>
                  <Activity size={16} color="#f59e0b" style={{ animation: "pulse 1s ease-in-out infinite alternate" }} />
                  <span style={{ fontSize: 14, fontWeight: 700, color: "#f59e0b" }}>Ranking in progress...</span>
                </div>

                {/* Progress bar */}
                <div style={{ marginBottom: 16 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 6 }}>
                    <span style={{ fontSize: 12, color: "var(--text-muted)" }}>
                      {runStatus.processed.toLocaleString()} / {runStatus.total_candidates.toLocaleString()} candidates
                    </span>
                    <span style={{ fontSize: 12, fontWeight: 700, color: "#f59e0b" }}>{progress.toFixed(1)}%</span>
                  </div>
                  <div style={{ height: 8, borderRadius: 8, background: "rgba(255,255,255,0.06)", overflow: "hidden" }}>
                    <motion.div
                      animate={{ width: `${progress}%` }}
                      transition={{ duration: 0.5 }}
                      style={{
                        height: "100%", borderRadius: 8,
                        background: "linear-gradient(90deg, #d97706, #f59e0b, #fbbf24)",
                        boxShadow: "0 0 12px rgba(245,158,11,0.4)",
                      }}
                    />
                  </div>
                </div>

                {/* Stats grid */}
                <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 10 }}>
                  {[
                    { icon: Users, label: "Processed", val: runStatus.processed.toLocaleString(), color: "#a78bfa" },
                    { icon: Shield, label: "Honeypots", val: runStatus.honeypots_detected.toString(), color: "#f43f5e" },
                    { icon: Zap, label: "Rate", val: runStatus.elapsed_seconds && runStatus.processed > 0
                        ? `${Math.round(runStatus.processed / (runStatus.elapsed_seconds || 1))}/s`
                        : "—", color: "#10b981" },
                  ].map(({ icon: Icon, label, val, color }) => (
                    <div key={label} style={{
                      padding: "10px 14px", borderRadius: 10,
                      background: "var(--bg-elevated)", border: "1px solid var(--border-subtle)", textAlign: "center",
                    }}>
                      <Icon size={14} color={color} style={{ marginBottom: 4 }} />
                      <div style={{ fontSize: 16, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif", color }}>{val}</div>
                      <div style={{ fontSize: 10, color: "var(--text-muted)" }}>{label}</div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Error */}
          {error && (
            <div style={{
              padding: "14px 18px", borderRadius: 12, marginBottom: 16,
              background: "rgba(244,63,94,0.08)", border: "1px solid rgba(244,63,94,0.25)",
              display: "flex", alignItems: "center", gap: 10,
            }}>
              <AlertTriangle size={16} color="#f43f5e" />
              <span style={{ fontSize: 13, color: "#f43f5e" }}>{error}</span>
            </div>
          )}

          {/* Complete — Stats Banner */}
          <AnimatePresence>
            {isComplete && runStatus && (
              <motion.div
                initial={{ opacity: 0, scale: 0.97 }}
                animate={{ opacity: 1, scale: 1 }}
                className="glass-card"
                style={{
                  padding: 20, marginBottom: 16,
                  background: "linear-gradient(135deg, rgba(245,158,11,0.12), rgba(16,185,129,0.08))",
                  border: "1px solid rgba(245,158,11,0.3)",
                }}
              >
                <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <CheckCircle size={18} color="#10b981" />
                    <span style={{ fontSize: 15, fontWeight: 700, color: "#10b981" }}>Ranking Complete!</span>
                  </div>
                  <button
                    onClick={() => challengeApi.download(runId!)}
                    style={{
                      display: "flex", alignItems: "center", gap: 8,
                      padding: "9px 18px", borderRadius: 10, cursor: "pointer",
                      background: "linear-gradient(135deg, #059669, #10b981)",
                      border: "none", color: "white", fontSize: 12, fontWeight: 700,
                      boxShadow: "0 4px 14px rgba(16,185,129,0.3)",
                    }}
                  >
                    <Download size={14} />
                    Download submission.csv
                  </button>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "repeat(4, 1fr)", gap: 10 }}>
                  {[
                    { label: "Total Ranked", val: "100", color: "#f59e0b", icon: Trophy },
                    { label: "Analyzed", val: runStatus.processed.toLocaleString(), color: "#a78bfa", icon: Users },
                    { label: "Honeypots", val: runStatus.honeypots_detected.toString(), color: "#f43f5e", icon: Shield },
                    { label: "Time", val: `${runStatus.elapsed_seconds?.toFixed(1)}s`, color: "#06b6d4", icon: Clock },
                  ].map(({ label, val, color, icon: Icon }) => (
                    <div key={label} style={{
                      padding: "10px 14px", borderRadius: 10,
                      background: "rgba(255,255,255,0.04)", border: "1px solid rgba(255,255,255,0.08)", textAlign: "center",
                    }}>
                      <Icon size={14} color={color} style={{ marginBottom: 4 }} />
                      <div style={{ fontSize: 18, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif", color }}>{val}</div>
                      <div style={{ fontSize: 10, color: "var(--text-muted)" }}>{label}</div>
                    </div>
                  ))}
                </div>
              </motion.div>
            )}
          </AnimatePresence>

          {/* Results Table */}
          {displayResults.length > 0 && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
              <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 14 }}>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <Award size={16} color="#f59e0b" />
                  <span style={{ fontSize: 14, fontWeight: 700 }}>
                    Top {allResults.length} Ranked Candidates
                  </span>
                  <span style={{ fontSize: 11, color: "var(--text-muted)" }}>
                    · Click any row for score breakdown
                  </span>
                </div>
                <button
                  onClick={() => setShowAll(!showAll)}
                  style={{
                    display: "flex", alignItems: "center", gap: 5,
                    padding: "6px 12px", borderRadius: 8, cursor: "pointer",
                    background: "var(--bg-elevated)", border: "1px solid var(--border-subtle)",
                    color: "var(--text-secondary)", fontSize: 11, fontWeight: 600,
                  }}
                >
                  <Eye size={11} />
                  {showAll ? "Show Top 10" : `Show All ${allResults.length}`}
                </button>
              </div>

              <div style={{ display: "flex", flexDirection: "column" }}>
                {displayResults.map((item, i) => (
                  <CandidateRow
                    key={item.candidate_id}
                    item={item}
                    index={i}
                    expanded={expandedId === item.candidate_id}
                    onToggle={() => setExpandedId(expandedId === item.candidate_id ? null : item.candidate_id)}
                  />
                ))}
              </div>

              {!showAll && allResults.length > 10 && (
                <div style={{ textAlign: "center", marginTop: 12 }}>
                  <button
                    onClick={() => setShowAll(true)}
                    style={{
                      padding: "10px 24px", borderRadius: 10, cursor: "pointer",
                      background: "rgba(245,158,11,0.1)", border: "1px solid rgba(245,158,11,0.25)",
                      color: "#f59e0b", fontSize: 13, fontWeight: 600,
                      display: "inline-flex", alignItems: "center", gap: 8,
                    }}
                  >
                    <ChevronRight size={14} />
                    View all {allResults.length} ranked candidates
                  </button>
                </div>
              )}
            </motion.div>
          )}

          {/* Empty state */}
          {!running && !isComplete && allResults.length === 0 && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              style={{
                textAlign: "center", padding: "80px 40px",
                color: "var(--text-muted)",
              }}
            >
              <Trophy size={48} color="rgba(245,158,11,0.3)" style={{ marginBottom: 16 }} />
              <div style={{ fontSize: 17, fontWeight: 700, marginBottom: 8, color: "var(--text-secondary)" }}>
                Ready to Rank
              </div>
              <p style={{ fontSize: 13, lineHeight: 1.7, maxWidth: 360, margin: "0 auto", color: "var(--text-muted)" }}>
                Select a dataset mode and hit <strong style={{ color: "#f59e0b" }}>Run Challenge Ranking</strong>.
                The system will score all candidates across 4 dimensions without any keyword gaming.
              </p>
              <div style={{ display: "flex", gap: 12, justifyContent: "center", marginTop: 20, flexWrap: "wrap" }}>
                {["NDCG@10 optimized", "100k candidates in ~90s", "Honeypot-proof", "Behavioral signals"].map(t => (
                  <span key={t} style={{
                    fontSize: 11, padding: "5px 12px", borderRadius: 20,
                    background: "rgba(245,158,11,0.08)", border: "1px solid rgba(245,158,11,0.2)",
                    color: "#fbbf24", fontWeight: 600,
                  }}>{t}</span>
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
