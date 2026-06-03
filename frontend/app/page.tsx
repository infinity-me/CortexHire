"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import {
  Briefcase, Users, TrendingUp, Brain,
  ArrowRight, Zap, Target, Shield, Clock,
  ChevronRight, Video
} from "lucide-react";
import { jobsApi, candidatesApi, rankingApi } from "@/lib/api";
import type { Job } from "@/lib/types";

const INNOVATIONS = [
  { icon: "🧠", label: "Role Cognition Engine",  desc: "Extracts Role Genome from JDs",      href: "/jobs" },
  { icon: "🌐", label: "Life Graph Intelligence", desc: "Career trajectories, not resumes",   href: "/candidates" },
  { icon: "⚡", label: "Capability Embeddings",   desc: "Multi-vector semantic matching",    href: "/ranking" },
  { icon: "🤖", label: "5-Agent Simulation",      desc: "Parallel expert recruiter AI",      href: "/ranking" },
  { icon: "📊", label: "Explainable Rankings",    desc: "Evidence-based reasoning",          href: "/ranking" },
  { icon: "🏢", label: "Org DNA Matching",        desc: "Culture-capability alignment",      href: "/candidates" },
  { icon: "📈", label: "Temporal Intelligence",   desc: "Career momentum analysis",          href: "/ranking" },
  { icon: "⚖️", label: "Ethical AI Layer",        desc: "Bias detection & correction",       href: "/ranking" },
  { icon: "💬", label: "Recruiter Copilot",       desc: "Conversational AI assistant",       href: "/copilot" },
  { icon: "🎥", label: "Live Interview AI",       desc: "Posture & answer scoring",          href: "/interview" },
];

function StatCard({
  icon: Icon, label, value, color, delay
}: {
  icon: React.ElementType;
  label: string;
  value: string | number;
  color: string;
  delay: number;
}) {
  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      transition={{ delay, duration: 0.5 }}
      className="glass-card"
      style={{ padding: "24px", flex: 1 }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start" }}>
        <div>
          <div style={{ color: "var(--text-muted)", fontSize: 12, fontWeight: 500, marginBottom: 8 }}>{label}</div>
          <div style={{ fontSize: 36, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif", color }}>
            {value}
          </div>
        </div>
        <div style={{
          width: 44, height: 44, borderRadius: 12,
          background: `${color}15`,
          border: `1px solid ${color}30`,
          display: "flex", alignItems: "center", justifyContent: "center"
        }}>
          <Icon size={20} color={color} />
        </div>
      </div>
    </motion.div>
  );
}

export default function DashboardPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [candidateCount, setCandidateCount] = useState<number>(0);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      jobsApi.list().catch(() => []),
      candidatesApi.count().catch(() => 0),
    ]).then(([j, c]) => {
      setJobs(j);
      setCandidateCount(c);
      setLoading(false);
    });
  }, []);

  const readyJobs = jobs.filter((j) => j.status === "ready").length;

  return (
    <div style={{ maxWidth: 1200 }}>
      {/* Hero */}
      <motion.div
        initial={{ opacity: 0, y: -20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
        style={{ marginBottom: 40 }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 12 }}>
          <div style={{
            padding: "4px 12px", borderRadius: 20,
            background: "rgba(124,58,237,0.15)", border: "1px solid rgba(124,58,237,0.3)",
            fontSize: 11, fontWeight: 600, color: "#a78bfa", letterSpacing: "0.05em"
          }}>
            AI INTELLIGENCE ACTIVE
          </div>
        </div>
        <h1 style={{
          fontSize: 42, fontWeight: 900, fontFamily: "'Space Grotesk', sans-serif",
          lineHeight: 1.15, marginBottom: 12
        }}>
          Command Center
          <span className="gradient-text" style={{ display: "block" }}>
            AI Recruitment Intelligence
          </span>
        </h1>
        <p style={{ fontSize: 16, color: "var(--text-secondary)", maxWidth: 540, lineHeight: 1.6 }}>
          Stop matching keywords. Start understanding potential. CortexHire ranks candidates
          the way an elite recruiter thinks — with full context, zero bias.
        </p>
      </motion.div>

      {/* Stats */}
      <div style={{ display: "flex", gap: 16, marginBottom: 32 }}>
        <StatCard icon={Briefcase} label="Active Jobs" value={loading ? "—" : jobs.length} color="#7c3aed" delay={0.1} />
        <StatCard icon={Users} label="Candidates" value={loading ? "—" : candidateCount} color="#06b6d4" delay={0.2} />
        <StatCard icon={Brain} label="AI-Ready Jobs" value={loading ? "—" : readyJobs} color="#10b981" delay={0.3} />
        <StatCard icon={TrendingUp} label="Innovations" value="10" color="#f59e0b" delay={0.4} />
      </div>

      {/* Quick Actions */}
      <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: 20, marginBottom: 32 }}>
        {/* Run Ranking */}
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.5, duration: 0.4 }}
        >
          <Link href="/jobs" style={{ textDecoration: "none" }}>
            <div className="glass-card border-gradient" style={{
              padding: 28, cursor: "pointer",
              background: "linear-gradient(135deg, rgba(124,58,237,0.12), rgba(6,182,212,0.08))",
              transition: "all 0.3s ease"
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 14 }}>
                <div style={{
                  width: 44, height: 44, borderRadius: 12,
                  background: "linear-gradient(135deg, #7c3aed, #4338ca)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  boxShadow: "0 0 20px rgba(124,58,237,0.4)"
                }}>
                  <Zap size={20} color="white" />
                </div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 2 }}>Run AI Ranking</div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Analyze candidates for a job</div>
                </div>
              </div>
              <p style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.6, marginBottom: 16 }}>
                Select a job → trigger the 5-agent pipeline → get a ranked shortlist with full explainability in minutes.
              </p>
              <div style={{ display: "flex", alignItems: "center", gap: 6, color: "#a78bfa", fontSize: 13, fontWeight: 600 }}>
                Start ranking <ArrowRight size={14} />
              </div>
            </div>
          </Link>
        </motion.div>

        {/* Recruiter Copilot */}
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.6, duration: 0.4 }}
        >
          <Link href="/copilot" style={{ textDecoration: "none" }}>
            <div className="glass-card" style={{
              padding: 28, cursor: "pointer",
              background: "linear-gradient(135deg, rgba(6,182,212,0.08), rgba(16,185,129,0.06))",
              transition: "all 0.3s ease"
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 14 }}>
                <div style={{
                  width: 44, height: 44, borderRadius: 12,
                  background: "linear-gradient(135deg, #06b6d4, #0891b2)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  boxShadow: "0 0 20px rgba(6,182,212,0.4)"
                }}>
                  <Brain size={20} color="white" />
                </div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 2 }}>Recruiter Copilot</div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)" }}>Ask anything about rankings</div>
                </div>
              </div>
              <p style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.6, marginBottom: 16 }}>
                "Why is #3 ranked above #1?" Ask the AI recruiter anything. Get honest, evidence-based answers instantly.
              </p>
              <div style={{ display: "flex", alignItems: "center", gap: 6, color: "#06b6d4", fontSize: 13, fontWeight: 600 }}>
                Open Copilot <ArrowRight size={14} />
              </div>
            </div>
          </Link>
        </motion.div>

        {/* Live Interview */}
        <motion.div
          initial={{ opacity: 0, scale: 0.97 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.7, duration: 0.4 }}
        >
          <Link href="/interview" style={{ textDecoration: "none" }}>
            <div className="glass-card" style={{
              padding: 28, cursor: "pointer",
              background: "linear-gradient(135deg, rgba(244,63,94,0.08), rgba(245,158,11,0.06))",
              transition: "all 0.3s ease"
            }}>
              <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 14 }}>
                <div style={{
                  width: 44, height: 44, borderRadius: 12,
                  background: "linear-gradient(135deg, #f43f5e, #f59e0b)",
                  display: "flex", alignItems: "center", justifyContent: "center",
                  boxShadow: "0 0 20px rgba(244,63,94,0.4)"
                }}>
                  <Video size={20} color="white" />
                </div>
                <div>
                  <div style={{ fontWeight: 700, fontSize: 15, marginBottom: 2 }}>Live Interview Panel</div>
                  <div style={{ fontSize: 12, color: "var(--text-muted)" }}>AI-powered video interviews</div>
                </div>
              </div>
              <p style={{ fontSize: 13, color: "var(--text-secondary)", lineHeight: 1.6, marginBottom: 16 }}>
                Run live video interviews with AI-generated role-specific questions. Score posture, communication, and answer quality in real-time.
              </p>
              <div style={{ display: "flex", alignItems: "center", gap: 6, color: "#f43f5e", fontSize: 13, fontWeight: 600 }}>
                Start interview <ArrowRight size={14} />
              </div>
            </div>
          </Link>
        </motion.div>
      </div>

      {/* Recent Jobs */}
      {jobs.length > 0 && (
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.7 }}
          className="glass-card"
          style={{ padding: 24, marginBottom: 32 }}
        >
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: 20 }}>
            <div style={{ fontWeight: 700, fontSize: 15 }}>Recent Jobs</div>
            <Link href="/jobs" style={{ fontSize: 13, color: "#a78bfa", display: "flex", alignItems: "center", gap: 4, textDecoration: "none" }}>
              View all <ChevronRight size={14} />
            </Link>
          </div>
          <div style={{ display: "flex", flexDirection: "column", gap: 10 }}>
            {jobs.slice(0, 4).map((job) => (
              <Link key={job.id} href={`/jobs/${job.id}`} style={{ textDecoration: "none" }}>
                <div style={{
                  display: "flex", alignItems: "center", justifyContent: "space-between",
                  padding: "12px 16px", borderRadius: 10,
                  background: "var(--bg-elevated)", border: "1px solid var(--border-subtle)",
                  transition: "all 0.2s ease", cursor: "pointer"
                }}>
                  <div style={{ display: "flex", alignItems: "center", gap: 12 }}>
                    <div style={{
                      width: 36, height: 36, borderRadius: 8,
                      background: "rgba(124,58,237,0.15)", border: "1px solid rgba(124,58,237,0.25)",
                      display: "flex", alignItems: "center", justifyContent: "center"
                    }}>
                      <Briefcase size={14} color="#a78bfa" />
                    </div>
                    <div>
                      <div style={{ fontSize: 13, fontWeight: 600, marginBottom: 2 }}>{job.title}</div>
                      <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{job.company} • {job.seniority}</div>
                    </div>
                  </div>
                  <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
                    <span style={{
                      fontSize: 10, fontWeight: 600, padding: "3px 8px", borderRadius: 20,
                      background: job.status === "ready" ? "rgba(16,185,129,0.15)" : "rgba(245,158,11,0.15)",
                      color: job.status === "ready" ? "#10b981" : "#f59e0b",
                      border: `1px solid ${job.status === "ready" ? "rgba(16,185,129,0.3)" : "rgba(245,158,11,0.3)"}`
                    }}>
                      {job.status.toUpperCase()}
                    </span>
                    <ChevronRight size={14} color="var(--text-muted)" />
                  </div>
                </div>
              </Link>
            ))}
          </div>
        </motion.div>
      )}

      {/* 10 Innovations Grid */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.8 }}
      >
        <div style={{ marginBottom: 16 }}>
          <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-muted)", letterSpacing: "0.08em", textTransform: "uppercase", marginBottom: 6 }}>
            Active Innovations
          </div>
          <div style={{ fontSize: 18, fontWeight: 700 }}>10 AI Modules Powering CortexHire</div>
        </div>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(5, 1fr)", gap: 10 }}>
          {INNOVATIONS.map((item, i) => (
            <Link key={i} href={item.href} style={{ textDecoration: "none" }}>
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.8 + i * 0.05 }}
                className="glass-card"
                style={{ padding: "14px 16px", textAlign: "center", cursor: "pointer", transition: "all 0.2s ease" }}
              >
                <div style={{ fontSize: 22, marginBottom: 6 }}>{item.icon}</div>
                <div style={{ fontSize: 11, fontWeight: 700, marginBottom: 3, color: "var(--text-primary)" }}>{item.label}</div>
                <div style={{ fontSize: 10, color: "var(--text-muted)", lineHeight: 1.4 }}>{item.desc}</div>
              </motion.div>
            </Link>
          ))}
        </div>
      </motion.div>
    </div>
  );
}
