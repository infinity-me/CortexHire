"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { TrendingUp, Briefcase, ChevronRight, Play } from "lucide-react";
import { jobsApi } from "@/lib/api";
import type { Job } from "@/lib/types";

export default function RankingIndexPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    jobsApi.list().then((j) => { setJobs(j); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const readyJobs = jobs.filter((j) => j.status === "ready");

  return (
    <div style={{ maxWidth: 800 }}>
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 30, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif", marginBottom: 6 }}>
          Rankings
        </h1>
        <p style={{ fontSize: 14, color: "var(--text-secondary)" }}>
          Select an AI-analyzed job to run the ranking pipeline or view results.
        </p>
      </motion.div>

      {loading ? (
        <div style={{ display: "flex", flexDirection: "column", gap: 12 }}>
          {[1,2,3].map(i => <div key={i} className="skeleton" style={{ height: 80, borderRadius: 14 }} />)}
        </div>
      ) : readyJobs.length === 0 ? (
        <div className="glass-card" style={{ padding: 40, textAlign: "center" }}>
          <div style={{ fontSize: 32, marginBottom: 12 }}>🧠</div>
          <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 8 }}>No analyzed jobs yet</div>
          <div style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 20 }}>
            Go to Jobs, select a job, and click &quot;Analyze JD&quot; to get started.
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
          {readyJobs.map((job, i) => (
            <motion.div key={job.id} initial={{ opacity: 0, y: 15 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.07 }}>
              <Link href={`/jobs/${job.id}`} style={{ textDecoration: "none" }}>
                <div className="glass-card" style={{ padding: "18px 22px", cursor: "pointer", display: "flex", alignItems: "center", justifyContent: "space-between" }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 14 }}>
                    <div style={{
                      width: 42, height: 42, borderRadius: 10,
                      background: "linear-gradient(135deg, rgba(124,58,237,0.2), rgba(6,182,212,0.15))",
                      border: "1px solid rgba(124,58,237,0.3)",
                      display: "flex", alignItems: "center", justifyContent: "center"
                    }}>
                      <TrendingUp size={18} color="#a78bfa" />
                    </div>
                    <div>
                      <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 3 }}>{job.title}</div>
                      <div style={{ fontSize: 12, color: "var(--text-secondary)" }}>{job.company} • {job.seniority}</div>
                    </div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 12, color: "#a78bfa", fontWeight: 600 }}>
                      <Play size={11} /> Run Ranking
                    </div>
                    <ChevronRight size={14} color="var(--text-muted)" />
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      )}
    </div>
  );
}
