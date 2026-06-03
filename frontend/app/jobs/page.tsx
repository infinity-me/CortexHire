"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { Briefcase, Plus, ChevronRight, MapPin, Clock, Brain, X, Loader2 } from "lucide-react";
import { jobsApi } from "@/lib/api";
import type { Job } from "@/lib/types";

const SENIORITY_OPTIONS = ["intern", "junior", "mid", "senior", "staff", "principal", "manager", "director"];

export default function JobsPage() {
  const router = useRouter();
  const [jobs, setJobs] = useState<Job[]>([]);
  const [loading, setLoading] = useState(true);
  const [showModal, setShowModal] = useState(false);
  const [creating, setCreating] = useState(false);
  const [form, setForm] = useState({
    title: "", company: "", location: "", seniority: "senior",
    employment_type: "full-time", description: "",
  });

  useEffect(() => {
    jobsApi.list().then((j) => { setJobs(j); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  const handleCreate = async () => {
    if (!form.title || !form.company || !form.description) return;
    setCreating(true);
    try {
      const job = await jobsApi.create(form);
      router.push(`/jobs/${job.id}`);
    } catch {
      setCreating(false);
    }
  };

  const statusColor = (s: string) =>
    s === "ready" ? { bg: "rgba(16,185,129,0.12)", text: "#10b981", border: "rgba(16,185,129,0.3)" } :
    s === "processing" ? { bg: "rgba(245,158,11,0.12)", text: "#f59e0b", border: "rgba(245,158,11,0.3)" } :
    { bg: "rgba(100,116,139,0.12)", text: "var(--text-muted)", border: "rgba(100,116,139,0.3)" };

  const inputStyle: React.CSSProperties = {
    width: "100%", padding: "10px 14px", borderRadius: 10, fontSize: 14,
    background: "var(--bg-elevated)", border: "1px solid var(--border-subtle)",
    color: "var(--text-primary)", outline: "none", boxSizing: "border-box",
  };

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
          <button
            id="new-job-btn"
            onClick={() => setShowModal(true)}
            style={{
              display: "flex", alignItems: "center", gap: 8,
              padding: "10px 18px", borderRadius: 10,
              background: "linear-gradient(135deg, #7c3aed, #4338ca)",
              border: "none", color: "white", fontSize: 13, fontWeight: 600,
              cursor: "pointer", boxShadow: "0 0 20px rgba(124,58,237,0.35)",
            }}
          >
            <Plus size={15} /> New Job
          </button>
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

      {/* New Job Modal */}
      <AnimatePresence>
        {showModal && (
          <motion.div
            initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
            onClick={() => !creating && setShowModal(false)}
            style={{
              position: "fixed", inset: 0, zIndex: 1000,
              background: "rgba(0,0,0,0.6)", backdropFilter: "blur(8px)",
              display: "flex", alignItems: "center", justifyContent: "center", padding: 24,
            }}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              onClick={e => e.stopPropagation()}
              className="glass-card"
              style={{ width: "100%", maxWidth: 600, padding: 32, position: "relative", maxHeight: "90vh", overflowY: "auto" }}
            >
              <button
                onClick={() => setShowModal(false)}
                style={{ position: "absolute", top: 16, right: 16, background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)" }}
              >
                <X size={18} />
              </button>

              <div style={{ fontSize: 11, fontWeight: 700, color: "#a78bfa", letterSpacing: "0.08em", marginBottom: 6 }}>NEW JOB REQUIREMENT</div>
              <h2 style={{ fontSize: 22, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif", marginBottom: 24 }}>
                Create Job
              </h2>

              <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                  <div>
                    <label style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)", display: "block", marginBottom: 6 }}>JOB TITLE *</label>
                    <input id="new-job-title" style={inputStyle} placeholder="e.g. Senior Backend Engineer"
                      value={form.title} onChange={e => setForm(f => ({ ...f, title: e.target.value }))} />
                  </div>
                  <div>
                    <label style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)", display: "block", marginBottom: 6 }}>COMPANY *</label>
                    <input id="new-job-company" style={inputStyle} placeholder="e.g. Acme Corp"
                      value={form.company} onChange={e => setForm(f => ({ ...f, company: e.target.value }))} />
                  </div>
                </div>

                <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 12 }}>
                  <div>
                    <label style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)", display: "block", marginBottom: 6 }}>LOCATION</label>
                    <input id="new-job-location" style={inputStyle} placeholder="e.g. Bengaluru, India (Remote)"
                      value={form.location} onChange={e => setForm(f => ({ ...f, location: e.target.value }))} />
                  </div>
                  <div>
                    <label style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)", display: "block", marginBottom: 6 }}>SENIORITY</label>
                    <select id="new-job-seniority" style={{ ...inputStyle, cursor: "pointer" }}
                      value={form.seniority} onChange={e => setForm(f => ({ ...f, seniority: e.target.value }))}>
                      {SENIORITY_OPTIONS.map(s => <option key={s} value={s}>{s}</option>)}
                    </select>
                  </div>
                </div>

                <div>
                  <label style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)", display: "block", marginBottom: 6 }}>JOB DESCRIPTION *</label>
                  <textarea
                    id="new-job-description"
                    style={{ ...inputStyle, minHeight: 160, resize: "vertical", fontFamily: "inherit", lineHeight: 1.6 }}
                    placeholder="Paste your full job description here. The AI will extract a Role Genome automatically…"
                    value={form.description}
                    onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
                  />
                </div>

                <button
                  id="new-job-submit"
                  onClick={handleCreate}
                  disabled={creating || !form.title || !form.company || !form.description}
                  style={{
                    display: "flex", alignItems: "center", justifyContent: "center", gap: 8,
                    padding: "12px 24px", borderRadius: 10, marginTop: 4,
                    background: creating || !form.title ? "rgba(124,58,237,0.3)" : "linear-gradient(135deg, #7c3aed, #4338ca)",
                    border: "none", color: "white", fontSize: 14, fontWeight: 700,
                    cursor: creating || !form.title || !form.company || !form.description ? "not-allowed" : "pointer",
                    boxShadow: "0 0 20px rgba(124,58,237,0.3)",
                  }}
                >
                  {creating
                    ? <><Loader2 size={16} className="animate-spin" /> Creating &amp; Analyzing…</>
                    : <><Brain size={16} /> Create Job &amp; Auto-Analyze</>
                  }
                </button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
