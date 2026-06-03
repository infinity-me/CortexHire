"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Briefcase, Plus, ChevronRight, MapPin, Clock, Brain } from "lucide-react";
import { jobsApi } from "@/lib/api";
import type { Job } from "@/lib/types";

export default function JobsPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    jobsApi.list().then((j) => { setJobs(j); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const statusColor = (s: string) =>
    s === "ready" ? { bg: "rgba(16,185,129,0.12)", text: "#10b981", border: "rgba(16,185,129,0.3)" } :
    s === "processing" ? { bg: "rgba(245,158,11,0.12)", text: "#f59e0b", border: "rgba(245,158,11,0.3)" } :
    { bg: "rgba(100,116,139,0.12)", text: "var(--text-muted)", border: "rgba(100,116,139,0.3)" };

  return (
    <div style={{ maxWidth: 1100 }}>
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 32 }}>
        <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-end" }}>
          <div>
            <h1 style={{ fontSize: 30, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif", marginBottom: 6 }}>
              Jobs
            </h1>
            <p style={{ fontSize: 14, color: "var(--text-secondary)" }}>
              {jobs.length} active jobs — {jobs.filter(j => j.status === "ready").length} AI-analyzed
            </p>
          </div>
        </div>
      </motion.div>

      {loading ? (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          {[1,2,3,4].map(i => (
            <div key={i} className="skeleton" style={{ height: 160, borderRadius: 16 }} />
          ))}
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 16 }}>
          {jobs.map((job, i) => {
            const sc = statusColor(job.status);
            return (
              <motion.div
                key={job.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.07 }}
              >
                <Link href={`/jobs/${job.id}`} style={{ textDecoration: "none" }}>
                  <div className="glass-card" style={{ padding: 24, cursor: "pointer", transition: "all 0.3s ease" }}>
                    <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 14 }}>
                      <div style={{
                        width: 44, height: 44, borderRadius: 12,
                        background: "linear-gradient(135deg, rgba(124,58,237,0.2), rgba(6,182,212,0.15))",
                        border: "1px solid rgba(124,58,237,0.3)",
                        display: "flex", alignItems: "center", justifyContent: "center"
                      }}>
                        <Briefcase size={18} color="#a78bfa" />
                      </div>
                      <span style={{
                        fontSize: 10, fontWeight: 700, padding: "4px 10px", borderRadius: 20,
                        background: sc.bg, color: sc.text, border: `1px solid ${sc.border}`,
                        letterSpacing: "0.05em"
                      }}>
                        {job.status.toUpperCase()}
                      </span>
                    </div>

                    <div style={{ marginBottom: 8 }}>
                      <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 4 }}>{job.title}</div>
                      <div style={{ fontSize: 13, color: "var(--text-secondary)", fontWeight: 600 }}>{job.company}</div>
                    </div>

                    <div style={{ display: "flex", gap: 14, marginBottom: 14 }}>
                      {job.location && (
                        <div style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 11, color: "var(--text-muted)" }}>
                          <MapPin size={10} />{job.location}
                        </div>
                      )}
                      {job.seniority && (
                        <div style={{ display: "flex", alignItems: "center", gap: 4, fontSize: 11, color: "var(--text-muted)" }}>
                          <Clock size={10} />{job.seniority}
                        </div>
                      )}
                    </div>

                    {/* Role genome preview */}
                    {job.role_genome && (
                      <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 12 }}>
                        {[
                          ["Technical", job.role_genome.technical_depth],
                          ["Ownership", job.role_genome.ownership],
                          ["Startup", job.role_genome.startup_readiness],
                        ].map(([label, val]) => (
                          <div key={label as string} style={{
                            fontSize: 10, padding: "3px 8px", borderRadius: 6,
                            background: "var(--bg-elevated)",
                            border: "1px solid var(--border-subtle)",
                            color: "var(--text-secondary)"
                          }}>
                            {label}: {((val as number) * 100).toFixed(0)}%
                          </div>
                        ))}
                      </div>
                    )}

                    <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                      <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 12, color: "#a78bfa", fontWeight: 600 }}>
                        <Brain size={12} />
                        {job.status === "ready" ? "AI Analyzed" : "Analyze & Rank"}
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
