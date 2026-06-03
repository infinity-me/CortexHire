"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Bot, User, Briefcase, ChevronDown, Loader2 } from "lucide-react";
import { copilotApi, jobsApi } from "@/lib/api";
import type { Job, CopilotMessage } from "@/lib/types";

const STARTER_QUESTIONS = [
  "Why is the #1 candidate ranked above #2?",
  "Who is the sleeper pick in this shortlist?",
  "What are the biggest risks in the top 3?",
  "Which candidate has the highest growth trajectory?",
  "Is there anyone who might be underrated by a traditional ATS?",
];

export default function CopilotPage() {
  const [jobs, setJobs] = useState<Job[]>([]);
  const [selectedJob, setSelectedJob] = useState<Job | null>(null);
  const [messages, setMessages] = useState<{ role: "user" | "assistant"; content: string }[]>([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingJobs, setLoadingJobs] = useState(true);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    jobsApi.list().then((j) => {
      // Show all jobs, not just "ready" ones - copilot works even without role genome
      setJobs(j);
      if (j.length > 0) setSelectedJob(j[0]);
      setLoadingJobs(false);
    }).catch(() => setLoadingJobs(false));
  }, []);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSend = async (text?: string) => {
    const msg = text || input.trim();
    if (!msg || !selectedJob || loading) return;
    setInput("");
    setMessages((prev) => [...prev, { role: "user", content: msg }]);
    setLoading(true);
    try {
      const res = await copilotApi.chat(selectedJob.id, msg);
      setMessages((prev) => [...prev, { role: "assistant", content: res.response }]);
    } catch {
      setMessages((prev) => [...prev, { role: "assistant", content: "I encountered an error. Please check the API connection and try again." }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ maxWidth: 900, display: "flex", flexDirection: "column", height: "calc(100vh - 130px)" }}>
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 20 }}>
        <div style={{ display: "flex", alignItems: "center", gap: 12, marginBottom: 6 }}>
          <div style={{
            width: 40, height: 40, borderRadius: 12,
            background: "linear-gradient(135deg, #06b6d4, #0891b2)",
            display: "flex", alignItems: "center", justifyContent: "center",
            boxShadow: "0 0 20px rgba(6,182,212,0.4)"
          }}>
            <Bot size={20} color="white" />
          </div>
          <div>
            <h1 style={{ fontSize: 24, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif" }}>
              Recruiter Copilot
            </h1>
            <p style={{ fontSize: 12, color: "var(--text-muted)" }}>Ask anything about your candidates</p>
          </div>
        </div>
      </motion.div>

      {/* Job selector */}
      <div style={{ marginBottom: 16 }}>
        <div style={{ fontSize: 11, fontWeight: 600, color: "var(--text-muted)", marginBottom: 6, letterSpacing: "0.06em" }}>
          ACTIVE JOB CONTEXT
        </div>
        <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
          {loadingJobs ? (
            <div className="skeleton" style={{ width: 200, height: 36, borderRadius: 8 }} />
          ) : jobs.length === 0 ? (
            <div style={{ fontSize: 13, color: "var(--text-muted)" }}>No jobs found. Jobs will appear here automatically.</div>
          ) : (
            jobs.map((job) => (
              <button key={job.id} onClick={() => { setSelectedJob(job); setMessages([]); }} style={{
                display: "flex", alignItems: "center", gap: 6,
                padding: "7px 14px", borderRadius: 8, fontSize: 12, fontWeight: 500,
                background: selectedJob?.id === job.id ? "rgba(6,182,212,0.15)" : "var(--bg-card)",
                border: selectedJob?.id === job.id ? "1px solid rgba(6,182,212,0.4)" : "1px solid var(--border-subtle)",
                color: selectedJob?.id === job.id ? "#06b6d4" : "var(--text-secondary)",
                cursor: "pointer"
              }}>
                <Briefcase size={11} />
                {job.title} @ {job.company}
              </button>
            ))
          )}
        </div>
      </div>

      {/* Chat area */}
      <div className="glass-card" style={{ flex: 1, display: "flex", flexDirection: "column", overflow: "hidden" }}>
        {/* Messages */}
        <div style={{ flex: 1, overflowY: "auto", padding: "20px 24px" }}>
          {messages.length === 0 ? (
            <div style={{ textAlign: "center", paddingTop: 40 }}>
              <div style={{ fontSize: 32, marginBottom: 12 }}>🤖</div>
              <div style={{ fontSize: 15, fontWeight: 600, marginBottom: 6 }}>Ready to help you hire smarter</div>
              <div style={{ fontSize: 13, color: "var(--text-secondary)", marginBottom: 28 }}>
                Ask me anything about the candidate rankings, tradeoffs, or risks.
              </div>
              <div style={{ display: "flex", flexDirection: "column", gap: 8, maxWidth: 500, margin: "0 auto" }}>
                {STARTER_QUESTIONS.map((q) => (
                  <button key={q} onClick={() => handleSend(q)} style={{
                    padding: "10px 16px", borderRadius: 10, fontSize: 13,
                    background: "var(--bg-elevated)", border: "1px solid var(--border-default)",
                    color: "var(--text-secondary)", cursor: "pointer", textAlign: "left",
                    transition: "all 0.2s ease"
                  }}>
                    {q}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: 16 }}>
              <AnimatePresence>
                {messages.map((msg, i) => (
                  <motion.div
                    key={i}
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    style={{
                      display: "flex",
                      gap: 12,
                      flexDirection: msg.role === "user" ? "row-reverse" : "row",
                      alignItems: "flex-start"
                    }}
                  >
                    {/* Avatar */}
                    <div style={{
                      width: 32, height: 32, borderRadius: 8, flexShrink: 0,
                      background: msg.role === "assistant"
                        ? "linear-gradient(135deg, #06b6d4, #0891b2)"
                        : "rgba(124,58,237,0.2)",
                      border: msg.role === "user" ? "1px solid rgba(124,58,237,0.4)" : "none",
                      display: "flex", alignItems: "center", justifyContent: "center"
                    }}>
                      {msg.role === "assistant" ? <Bot size={14} color="white" /> : <User size={14} color="#a78bfa" />}
                    </div>

                    {/* Bubble */}
                    <div style={{
                      maxWidth: "75%", padding: "12px 16px", borderRadius: 14,
                      background: msg.role === "assistant" ? "var(--bg-elevated)" : "rgba(124,58,237,0.15)",
                      border: `1px solid ${msg.role === "assistant" ? "var(--border-subtle)" : "rgba(124,58,237,0.3)"}`,
                      fontSize: 13, lineHeight: 1.7, color: "var(--text-primary)"
                    }}>
                      {msg.content}
                    </div>
                  </motion.div>
                ))}
              </AnimatePresence>

              {loading && (
                <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} style={{ display: "flex", gap: 12, alignItems: "flex-start" }}>
                  <div style={{
                    width: 32, height: 32, borderRadius: 8, flexShrink: 0,
                    background: "linear-gradient(135deg, #06b6d4, #0891b2)",
                    display: "flex", alignItems: "center", justifyContent: "center"
                  }}>
                    <Bot size={14} color="white" />
                  </div>
                  <div style={{
                    padding: "12px 16px", borderRadius: 14,
                    background: "var(--bg-elevated)", border: "1px solid var(--border-subtle)",
                    display: "flex", alignItems: "center", gap: 8
                  }}>
                    <Loader2 size={14} style={{ animation: "spin 1s linear infinite" }} color="#06b6d4" />
                    <span style={{ fontSize: 13, color: "var(--text-muted)" }}>Analyzing ranking data...</span>
                  </div>
                </motion.div>
              )}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input */}
        <div style={{
          padding: "16px 20px",
          borderTop: "1px solid var(--border-subtle)",
          display: "flex", gap: 10
        }}>
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && !e.shiftKey && handleSend()}
            placeholder={selectedJob ? `Ask about ${selectedJob.title} candidates...` : "Select a job first"}
            disabled={!selectedJob || loading}
            style={{
              flex: 1, padding: "12px 16px", borderRadius: 10, fontSize: 13,
              background: "var(--bg-elevated)", border: "1px solid var(--border-default)",
              color: "var(--text-primary)", outline: "none",
              fontFamily: "inherit"
            }}
          />
          <button
            onClick={() => handleSend()}
            disabled={!input.trim() || !selectedJob || loading}
            style={{
              width: 44, height: 44, borderRadius: 10,
              background: !input.trim() || !selectedJob ? "var(--bg-elevated)" : "linear-gradient(135deg, #06b6d4, #0891b2)",
              border: "none", display: "flex", alignItems: "center", justifyContent: "center",
              cursor: input.trim() && selectedJob ? "pointer" : "not-allowed",
              boxShadow: input.trim() && selectedJob ? "0 0 15px rgba(6,182,212,0.4)" : "none"
            }}
          >
            <Send size={16} color={!input.trim() || !selectedJob ? "var(--text-muted)" : "white"} />
          </button>
        </div>
      </div>
    </div>
  );
}
