"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { TrendingUp, Briefcase, ChevronRight, Play, Clock, CheckCircle } from "lucide-react";
import { jobsApi, rankingApi } from "@/lib/api";
import type { Job } from "@/lib/types";

export default function RankingIndexPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [runCounts, setRunCounts] = useState<Record<string, number>>({});

  useEffect(() => {
    jobsApi.list()
      .then(async (j) => {
        setJobs(j);
        setLoading(false);
        // Load run counts for each job in parallel
        const counts: Record<string, number> = {};
        await Promise.all(
          j.map(async (job) => {
            try {
              const runs = await rankingApi.listRuns(job.id);
              counts[job.id] = runs.filter(r => r.status === "complete").length;
            } catch { counts[job.id] = 0; }
          })
        );
        setRunCounts(counts);
      })
      .catch(() => setLoading(false));
  }, []);

  return (
    <div style={{ maxWidth: 860 }}>
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 32 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 10, marginBottom: 8 }}>
          <TrendingUp size={22} color="#a78bfa" />
          <h1 style={{ fontSize: 30, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif" }}>
            Rankings
          </h1>
        </div>
        <p style={{ fontSize: 14, color: "var(--text-secondary)" }}>
          Select a job to run AI ranking or view past results. Jobs must be analyzed before ranking.
        </p>
      </motion.div>

      {loading ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {[1,2,3].map(i => <div key={i} className="skeleton" style={{ height: 80, borderRadius: 14 }} />)}
        </div>
      ) : jobs.length === 0 ? (
        <div className="glass-card" style={{ padding: 40, textAlign: "center" }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>🧠</div>
          <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 8 }}>No jobs yet</div>
          <div style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 20 }}>
            Create a job first, then analyze it to enable AI ranking.
          </div>
          <Link href="/jobs" style={{
            display: "inline-flex", alignItems: "center", gap: 8,
            padding: "10px 20px", borderRadius: 10,
            background: "linear-gradient(135deg, #7c3aed, #4338ca)",
            color: "white", fontSize: 13, fontWeight: 600, textDecoration: "none"
          }}>
            <Briefcase size={14} /> Go to Jobs
          </Link>
        </div>
      ) : (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {jobs.map((job, i) => {
            const isReady = job.status === "ready";
            const completedRuns = runCounts[job.id] ?? 0;
            return (
              <motion.div key={job.id} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.06 }}>
                <Link href={`/jobs/${job.id}`} style={{ textDecoration: "none" }}>
                  <div className="glass-card" style={{
                    padding: "18px 22px", cursor: "pointer",
                    display: "flex", alignItems: "center", justifyContent: "space-between",
                    opacity: isReady ? 1 : 0.72,
                    transition: "all 0.2s ease",
                  }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                      <div style={{
                        width: 42, height: 42, borderRadius: 10,
                        background: isReady
                          ? "linear-gradient(135deg, rgba(124,58,237,0.2), rgba(6,182,212,0.15))"
                          : "rgba(245,158,11,0.1)",
                        border: `1px solid ${isReady ? "rgba(124,58,237,0.3)" : "rgba(245,158,11,0.3)"}`,
                        display: "flex", alignItems: "center", justifyContent: "center"
                      }}>
                        {isReady
                          ? <TrendingUp size={18} color="#a78bfa" />
                          : <Clock size={18} color="#f59e0b" />}
                      </div>
                      <div>
                        <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 3 }}>{job.title}</div>
                        <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>{job.company} • {job.seniority}</div>
                      </div>
                    </div>
                    <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                      {completedRuns > 0 && (
                        <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: "#10b981" }}>
                          <CheckCircle size={11} /> {completedRuns} run{completedRuns !== 1 ? "s" : ""}
                        </div>
                      )}
                      <span style={{
                        fontSize: 10, fontWeight: 600, padding: "3px 8px", borderRadius: 20,
                        background: isReady ? "rgba(16,185,129,0.12)" : "rgba(245,158,11,0.12)",
                        color: isReady ? "#10b981" : "#f59e0b",
                        border: `1px solid ${isReady ? "rgba(16,185,129,0.3)" : "rgba(245,158,11,0.3)"}`
                      }}>
                        {isReady ? "READY" : job.status.toUpperCase()}
                      </span>
                      <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 12, color: "#a78bfa", fontWeight: 600 }}>
                        {isReady ? <><Play size={11} /> Run Ranking</> : "Analyze first"}
                      </div>
                      <ChevronRight size={14} color="var(--text-muted)" />
                    </div>
                  </div>
                </Link>
              </motion.div>
            );
          })}
        </div>
      )}
    </div>
  );
}
