"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { rankingApi } from "@/lib/api";
import type { RankingRun, RankedCandidate } from "@/lib/types";
import CandidateCard from "@/components/ranking/CandidateCard";
import AgentDebate from "@/components/ranking/AgentDebate";
import BiasReport from "@/components/ranking/BiasReport";
import { Trophy, Users, Loader2, ChevronLeft, Download, FileSpreadsheet } from "lucide-react";
import Link from "next/link";

export default function RankingResultsPage() {
  const { runId } = useParams() as { runId: string };
  const [data, setData] = useState<RankingRun | null>(null);
  const [loading, setLoading] = useState(true);
  const [selected, setSelected] = useState<RankedCandidate | null>(null);
  const [activeTab, setActiveTab] = useState<"overview" | "agents" | "bias">("overview");

  useEffect(() => {
    rankingApi.getResults(runId).then((r) => { setData(r); setLoading(false); }).catch(() => setLoading(false));
  }, [runId]);

  if (loading) return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", justifyContent: "center", height: 500, gap: 16 }}>
      <Loader2 size={40} style={{ animation: "spin 1s linear infinite" }} color="#7c3aed" />
      <div style={{ color: "var(--text-secondary)" }}>Loading ranking results...</div>
    </div>
  );
  if (!data || data.status === "no_results") return <div style={{ color: "var(--text-secondary)", padding: 40 }}>No results found.</div>;

  const results = data.results || [];
  const top = results[0];

  return (
    <div style={{ maxWidth: 1200 }}>
      <Link href="/jobs" style={{ display: "flex", alignItems: "center", gap: 6, color: "var(--text-muted)", fontSize: 13, marginBottom: 24, textDecoration: "none" }}>
        <ChevronLeft size={14} /> Back to Jobs
      </Link>

      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 28 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: 8 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <Trophy size={20} color="#f59e0b" />
            <h1 style={{ fontSize: 28, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif" }}>
              AI Ranking Results
            </h1>
          </div>
          {/* Download CSV — competition format */}
          <button
            onClick={() => rankingApi.downloadCsv(runId)}
            style={{
              display: "flex", alignItems: "center", gap: 8,
              padding: "10px 18px", borderRadius: 10, cursor: "pointer",
              background: "linear-gradient(135deg, #059669, #10b981)",
              border: "none", color: "white", fontSize: 13, fontWeight: 600,
              boxShadow: "0 4px 16px rgba(16,185,129,0.3)",
            }}
          >
            <FileSpreadsheet size={15} />
            Download Rankings CSV
            <Download size={13} />
          </button>
        </div>
        <div style={{ display: "flex", gap: 20 }}>
          <span style={{ fontSize: 14, color: "var(--text-secondary)" }}>
            <strong style={{ color: "var(--text-primary)" }}>{results.length}</strong> candidates ranked from{" "}
            <strong style={{ color: "var(--text-primary)" }}>{data.total_candidates}</strong> analyzed
          </span>
          <span style={{ fontSize: 13, color: "var(--text-muted)" }}>·</span>
          <span style={{ fontSize: 13, color: "var(--text-muted)" }}>Format: candidate_id, rank, score, reasoning</span>
        </div>
      </motion.div>

      <div style={{ display: "grid", gridTemplateColumns: selected ? "400px 1fr" : "1fr", gap: 24 }}>
        {/* Ranking list */}
        <div>
          {/* Summary stats */}
          {top && (
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
              className="glass-card" style={{
                padding: 20, marginBottom: 16,
                background: "linear-gradient(135deg, rgba(124,58,237,0.12), rgba(6,182,212,0.08))",
                border: "1px solid rgba(124,58,237,0.25)"
              }}>
              <div style={{ fontSize: 11, color: "#a78bfa", fontWeight: 700, marginBottom: 6 }}>🏆 TOP CANDIDATE</div>
              <div style={{ fontWeight: 700, fontSize: 16, marginBottom: 4 }}>{top.candidate.name}</div>
              <div style={{ fontSize: 12, color: "var(--text-secondary)", marginBottom: 12 }}>{top.candidate.headline}</div>
              <div style={{ display: "flex", gap: 16 }}>
                {[
                  { label: "Fit", val: top.fit_score, color: "#10b981" },
                  { label: "Growth", val: top.growth_score, color: "#06b6d4" },
                  { label: "Success", val: `${(top.success_probability * 100).toFixed(0)}%`, color: "#f59e0b" },
                ].map(({ label, val, color }) => (
                  <div key={label}>
                    <div style={{ fontSize: 10, color: "var(--text-muted)", marginBottom: 2 }}>{label}</div>
                    <div style={{ fontSize: 20, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif", color }}>
                      {typeof val === "number" ? val.toFixed(0) : val}
                    </div>
                  </div>
                ))}
              </div>
            </motion.div>
          )}

          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {results.map((r, i) => (
              <CandidateCard
                key={r.candidate.id}
                ranked={r}
                index={i}
                isSelected={selected?.candidate.id === r.candidate.id}
                onClick={() => setSelected(selected?.candidate.id === r.candidate.id ? null : r)}
              />
            ))}
          </div>
        </div>

        {/* Detail panel */}
        <AnimatePresence>
          {selected && (
            <motion.div
              key="detail"
              initial={{ opacity: 0, x: 30 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: 30 }}
              transition={{ duration: 0.3 }}
            >
              {/* Tabs */}
              <div style={{ display: "flex", gap: 4, marginBottom: 16 }}>
                {(["overview", "agents", "bias"] as const).map((tab) => (
                  <button key={tab} onClick={() => setActiveTab(tab)} style={{
                    padding: "8px 16px", borderRadius: 8, border: "none",
                    background: activeTab === tab ? "rgba(124,58,237,0.2)" : "transparent",
                    color: activeTab === tab ? "#a78bfa" : "var(--text-muted)",
                    fontSize: 12, fontWeight: 600, cursor: "pointer",
                    borderBottom: activeTab === tab ? "2px solid #7c3aed" : "2px solid transparent"
                  }}>
                    {tab === "overview" ? "Overview" : tab === "agents" ? "5 Agents" : "Bias Report"}
                  </button>
                ))}
              </div>

              {activeTab === "overview" && (
                <div className="glass-card" style={{ padding: 24 }}>
                  <div style={{ fontWeight: 700, fontSize: 17, marginBottom: 4 }}>{selected.candidate.name}</div>
                  <div style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 20 }}>{selected.candidate.headline}</div>

                  {/* Score grid */}
                  <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12, marginBottom: 20 }}>
                    {[
                      { label: "Fit Score", val: selected.fit_score, color: "#10b981" },
                      { label: "Risk Score", val: selected.risk_score, color: "#f43f5e", lower: true },
                      { label: "Growth Score", val: selected.growth_score, color: "#06b6d4" },
                      { label: "Confidence", val: selected.confidence_score, color: "#a78bfa" },
                    ].map(({ label, val, color, lower }) => (
                      <div key={label} style={{
                        padding: 14, borderRadius: 12,
                        background: "var(--bg-elevated)", border: "1px solid var(--border-subtle)"
                      }}>
                        <div style={{ fontSize: 10, color: "var(--text-muted)", marginBottom: 4 }}>
                          {label}{lower ? " (lower=better)" : ""}
                        </div>
                        <div style={{ fontSize: 28, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif", color }}>
                          {val.toFixed(0)}
                        </div>
                        <div className="progress-bar" style={{ marginTop: 6 }}>
                          <div className="progress-fill" style={{ width: `${val}%`, background: color }} />
                        </div>
                      </div>
                    ))}
                  </div>

                  {/* Success probability */}
                  <div style={{
                    padding: 16, borderRadius: 12, marginBottom: 20,
                    background: "linear-gradient(135deg, rgba(16,185,129,0.1), rgba(6,182,212,0.08))",
                    border: "1px solid rgba(16,185,129,0.25)", textAlign: "center"
                  }}>
                    <div style={{ fontSize: 11, color: "#10b981", marginBottom: 4, fontWeight: 600 }}>PREDICTED SUCCESS PROBABILITY</div>
                    <div style={{ fontSize: 48, fontWeight: 900, fontFamily: "'Space Grotesk', sans-serif", color: "#10b981" }}>
                      {(selected.success_probability * 100).toFixed(0)}%
                    </div>
                  </div>

                  {/* Explanation */}
                  {selected.explanation && (
                    <div>
                      <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", marginBottom: 10 }}>AI EXPLANATION</div>
                      <p style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.7 }}>{selected.explanation}</p>
                    </div>
                  )}
                </div>
              )}

              {activeTab === "agents" && selected.agent_scores && (
                <AgentDebate agentResults={selected.agent_scores.agent_results} />
              )}

              {activeTab === "bias" && selected.bias_report && (
                <BiasReport report={selected.bias_report} />
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
