"use client";

import { useEffect, useState } from "react";
import { useParams, useRouter } from "next/navigation";
import { motion } from "framer-motion";
import Link from "next/link";
import {
  Brain, Zap, Play, ChevronLeft, Loader2,
  Target, Shield, TrendingUp, Eye, History, Download, FileSpreadsheet, ExternalLink
} from "lucide-react";
import { jobsApi, rankingApi } from "@/lib/api";
import type { Job } from "@/lib/types";
import RoleGenomeChart from "@/components/jobs/RoleGenomeChart";

export default function JobDetailPage() {
  const { id } = useParams() as { id: string };
  const router = useRouter();
  const [job, setJob] = useState<Job | null>(null);
  const [loading, setLoading] = useState(true);
  const [analyzing, setAnalyzing] = useState(false);
  const [ranking, setRanking] = useState(false);
  const [rankStatus, setRankStatus] = useState("");
  const [runId, setRunId] = useState<string | null>(null);
  const [preFilterLimit, setPreFilterLimit] = useState(50);
  const [pastRuns, setPastRuns] = useState<Array<{
    run_id: string; status: string; total_candidates: number;
    shortlist_size: number; created_at: string;
  }>>([]);

  useEffect(() => {
    jobsApi.get(id).then((j) => {
      setJob(j); setLoading(false);
      // Load past runs after job loads
      rankingApi.listRuns(id).then(setPastRuns).catch(() => {});
    }).catch(() => setLoading(false));
  }, [id]);

  const handleAnalyze = async () => {
    if (!job) return;
    setAnalyzing(true);
    try {
      const updated = await jobsApi.analyze(id);
      setJob(updated);
    } finally {
      setAnalyzing(false);
    }
  };

  const handleRank = async () => {
    if (!job) return;
    setRanking(true);
    setRankStatus("Starting ranking pipeline...");
    try {
      const { run_id } = await rankingApi.startRun(job.id, 10, preFilterLimit);
      setRunId(run_id);
      await rankingApi.pollResults(run_id, (status, count) => {
        const label =
          status === "prefiltering" ? `Phase 1: Filtering ${count} candidates…` :
          status === "processing" ? `Phase 2: Running 5-agent analysis… ${count} candidates` :
          status;
        setRankStatus(label);
      });
      // Refresh past runs list
      rankingApi.listRuns(job.id).then(setPastRuns).catch(() => {});
      router.push(`/ranking/${run_id}`);
    } catch (e) {
      setRankStatus("Ranking failed. Please try again.");
      setRanking(false);
    }
  };

  if (loading) {
    return (
      <div style={{ display: "flex", alignItems: "center", justifyContent: "center", height: 400 }}>
        <Loader2 size={32} className="animate-spin" color="var(--cortex-purple)" />
      </div>
    );
  }
  if (!job) return <div>Job not found</div>;

  const genome = job.role_genome;

  return (
    <div style={{ maxWidth: 1100 }}>
      {/* Back */}
      <Link href="/jobs" style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--text-muted)", fontSize: 13, marginBottom: 24, textDecoration: "none" }}>
        <ChevronLeft size={14} /> Back to Jobs
      </Link>

      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 28 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
          <div>
            <div style={{ fontSize: 12, color: "var(--text-muted)", marginBottom: 6, fontWeight: 500 }}>
              {job.company} • {job.seniority} • {job.location}
            </div>
            <h1 style={{ fontSize: 32, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif", marginBottom: 8 }}>
              {job.title}
            </h1>
            <span style={{
              fontSize: 11, fontWeight: 600, padding: "4px 10px", borderRadius: 20,
              background: job.status === "ready" ? "rgba(16,185,129,0.12)" : "rgba(245,158,11,0.12)",
              color: job.status === "ready" ? "#10b981" : "#f59e0b",
              border: `1px solid ${job.status === "ready" ? "rgba(16,185,129,0.3)" : "rgba(245,158,11,0.3)"}`
            }}>
              {job.status.toUpperCase()}
            </span>
          </div>

          <div style={{ display: "flex", gap: 10, flexDirection: "column", alignItems: "flex-end" }}>
            {job.status !== "ready" && (
              <button
                onClick={handleAnalyze}
                disabled={analyzing}
                style={{
                  display: "flex", alignItems: "center", gap: 8,
                  padding: "10px 18px", borderRadius: 10,
                  background: "rgba(124,58,237,0.15)", border: "1px solid rgba(124,58,237,0.35)",
                  color: "#a78bfa", fontSize: 13, fontWeight: 600, cursor: "pointer"
                }}
              >
                {analyzing ? <Loader2 size={14} /> : <Brain size={14} />}
                {analyzing ? "Analyzing..." : "Analyze JD"}
              </button>
            )}

            {/* Pre-filter slider */}
            {job.status === "ready" && !ranking && (
              <div style={{ textAlign: "right" }}>
                <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 4 }}>
                  Analyze top <strong style={{ color: "#a78bfa" }}>{preFilterLimit}</strong> candidates
                  {" "}· ~{Math.ceil(preFilterLimit / 3 * 0.5)} min
                </div>
                <input
                  id="prefilter-slider"
                  type="range" min={25} max={500} step={25}
                  value={preFilterLimit}
                  onChange={e => setPreFilterLimit(Number(e.target.value))}
                  style={{ width: 160, accentColor: "#7c3aed", cursor: "pointer" }}
                />
              </div>
            )}

            <button
              onClick={handleRank}
              disabled={ranking || job.status !== "ready"}
              style={{
                display: "flex", alignItems: "center", gap: 8,
                padding: "10px 18px", borderRadius: 10,
                background: ranking ? "rgba(124,58,237,0.1)" : "linear-gradient(135deg, #7c3aed, #4338ca)",
                border: "none", color: "white", fontSize: 13, fontWeight: 600,
                cursor: job.status === "ready" && !ranking ? "pointer" : "not-allowed",
                opacity: job.status !== "ready" ? 0.5 : 1,
                boxShadow: job.status === "ready" ? "0 0 20px rgba(124,58,237,0.4)" : "none"
              }}
            >
              {ranking ? <Loader2 size={14} /> : <Play size={14} />}
              {ranking ? rankStatus : "Run AI Ranking"}
            </button>
          </div>
        </div>
      </motion.div>

      {/* Past Ranking Runs */}
      {pastRuns.length > 0 && (
        <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15 }}
          className="glass-card" style={{ padding: 20, marginBottom: 24 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 14 }}>
            <History size={14} color="#a78bfa" />
            <span style={{ fontSize: 12, fontWeight: 700, color: "#a78bfa", letterSpacing: "0.06em" }}>RANKING HISTORY</span>
            <span style={{ fontSize: 11, color: "var(--text-muted)", marginLeft: 4 }}>{pastRuns.length} run{pastRuns.length !== 1 ? "s" : ""}</span>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
            {pastRuns.map((run, i) => (
              <div key={run.run_id} style={{
                display: "flex", alignItems: "center", justifyContent: "space-between",
                padding: "10px 14px", borderRadius: 10,
                background: "var(--bg-elevated)", border: "1px solid var(--border-subtle)",
              }}>
                <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                  <span style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)" }}>#{i + 1}</span>
                  <div>
                    <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-primary)" }}>
                      {run.total_candidates ?? "—"} candidates · top {run.shortlist_size}
                    </div>
                    <div style={{ fontSize: 11, color: "var(--text-muted)" }}>
                      {run.created_at ? new Date(run.created_at).toLocaleString() : ""}
                    </div>
                  </div>
                </div>
                <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
                  <span style={{
                    fontSize: 10, fontWeight: 700, padding: "3px 8px", borderRadius: 6,
                    background: run.status === "complete" ? "rgba(16,185,129,0.12)" : "rgba(245,158,11,0.12)",
                    color: run.status === "complete" ? "#10b981" : "#f59e0b",
                    border: `1px solid ${run.status === "complete" ? "rgba(16,185,129,0.3)" : "rgba(245,158,11,0.3)"}`
                  }}>
                    {run.status.toUpperCase()}
                  </span>
                  {run.status === "complete" && (
                    <>
                      <Link href={`/ranking/${run.run_id}`} style={{
                        display: "flex", alignItems: "center", gap: 4,
                        padding: "5px 10px", borderRadius: 7, textDecoration: "none",
                        background: "rgba(124,58,237,0.15)", color: "#a78bfa",
                        fontSize: 11, fontWeight: 600
                      }}>
                        <ExternalLink size={11} /> View
                      </Link>
                      <button
                        onClick={() => rankingApi.downloadCsv(run.run_id)}
                        style={{
                          display: "flex", alignItems: "center", gap: 4,
                          padding: "5px 10px", borderRadius: 7, cursor: "pointer",
                          background: "rgba(16,185,129,0.15)", border: "none",
                          color: "#10b981", fontSize: 11, fontWeight: 600
                        }}
                      >
                        <Download size={11} /> CSV
                      </button>
                    </>
                  )}
                </div>
              </div>
            ))}
          </div>
        </motion.div>
      )}

      <div style={{ display: "grid", gridTemplateColumns: genome ? "minmax(0, 1fr) 380px" : "1fr", gap: 20 }}>
        {/* Left: JD + genome details */}
        <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
          {/* Role summary */}
          {genome?.role_summary && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.2 }}
              className="glass-card" style={{ padding: 22 }}>
              <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 12 }}>
                <Eye size={14} color="#a78bfa" />
                <span style={{ fontSize: 12, fontWeight: 700, color: "#a78bfa", letterSpacing: "0.05em" }}>
                  AI ROLE UNDERSTANDING
                </span>
              </div>
              <p style={{ fontSize: 14, lineHeight: 1.7, color: "var(--text-secondary)" }}>
                {genome.role_summary}
              </p>
            </motion.div>
          )}

          {/* Functional + hidden needs */}
          {genome && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(160px, 1fr))", gap: 12 }}>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
                className="glass-card" style={{ padding: 18 }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: "#06b6d4", marginBottom: 10 }}>FUNCTIONAL NEEDS</div>
                {genome.functional_needs.map((n, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 6 }}>
                    <div style={{ width: 5, height: 5, borderRadius: "50%", background: "#06b6d4", marginTop: 6, flexShrink: 0 }} />
                    <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>{n}</span>
                  </div>
                ))}
              </motion.div>
              <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.35 }}
                className="glass-card" style={{ padding: 18 }}>
                <div style={{ fontSize: 11, fontWeight: 700, color: "#f59e0b", marginBottom: 10 }}>HIDDEN NEEDS</div>
                {genome.hidden_needs.map((n, i) => (
                  <div key={i} style={{ display: "flex", alignItems: "flex-start", gap: 8, marginBottom: 6 }}>
                    <div style={{ width: 5, height: 5, borderRadius: "50%", background: "#f59e0b", marginTop: 6, flexShrink: 0 }} />
                    <span style={{ fontSize: 13, color: "var(--text-secondary)" }}>{n}</span>
                  </div>
                ))}
              </motion.div>
            </div>
          )}

          {/* Context cards */}
          {genome && (
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(140px, 1fr))", gap: 10 }}>
              {[
                { icon: Target, label: "Cognitive Style", value: genome.cognitive_style, color: "#a78bfa" },
                { icon: Shield, label: "Risk Profile", value: genome.risk_profile, color: "#06b6d4" },
                { icon: TrendingUp, label: "Team Dynamics", value: genome.team_dynamics, color: "#10b981" },
              ].map(({ icon: Icon, label, value, color }) => (
                <div key={label} className="glass-card" style={{ padding: 14 }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 6 }}>
                    <Icon size={11} color={color} />
                    <span style={{ fontSize: 10, fontWeight: 700, color, letterSpacing: "0.04em" }}>{label.toUpperCase()}</span>
                  </div>
                  <p style={{ fontSize: 11, color: "var(--text-secondary)", lineHeight: 1.5 }}>{value}</p>
                </div>
              ))}
            </div>
          )}

          {/* JD text */}
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.4 }}
            className="glass-card" style={{ padding: 22 }}>
            <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-muted)", marginBottom: 12, letterSpacing: "0.06em" }}>JOB DESCRIPTION</div>
            <pre style={{
              fontSize: 13, lineHeight: 1.7, color: "var(--text-secondary)",
              whiteSpace: "pre-wrap", fontFamily: "inherit", margin: 0
            }}>
              {job.description}
            </pre>
          </motion.div>
        </div>

        {/* Right: Radar chart */}
        {genome && (
          <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.3 }}
              className="glass-card" style={{ padding: 22 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "#a78bfa", marginBottom: 4, letterSpacing: "0.05em" }}>ROLE GENOME</div>
              <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 12 }}>AI-extracted capability requirements</div>
              <RoleGenomeChart genome={genome} size={280} />
            </motion.div>

            {/* Score breakdown */}
            <motion.div initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: 0.4 }}
              className="glass-card" style={{ padding: 20 }}>
              <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-muted)", marginBottom: 14, letterSpacing: "0.06em" }}>DIMENSION SCORES</div>
              {[
                ["Technical Depth", genome.technical_depth, "#7c3aed"],
                ["Ownership", genome.ownership, "#06b6d4"],
                ["Startup Readiness", genome.startup_readiness, "#10b981"],
                ["Leadership", genome.leadership_potential, "#f59e0b"],
                ["Creativity", genome.creativity, "#f43f5e"],
                ["Communication", genome.communication, "#8b5cf6"],
              ].map(([label, val, color]) => (
                <div key={label as string} style={{ marginBottom: 10 }}>
                  <div style={{ display: "flex", justifyContent: "space-between", marginBottom: 4 }}>
                    <span style={{ fontSize: 11, color: "var(--text-secondary)" }}>{label as string}</span>
                    <span style={{ fontSize: 11, fontWeight: 700, color: color as string }}>{((val as number) * 100).toFixed(0)}%</span>
                  </div>
                  <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${(val as number) * 100}%`, background: color as string }} />
                  </div>
                </div>
              ))}
            </motion.div>
          </div>
        )}
      </div>
    </div>
  );
}
