"use client";

import { useEffect, useRef, useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import {
  Users, MapPin, Upload, X, CheckCircle, AlertCircle,
  Loader2, FileText, ChevronRight, TrendingUp, Sparkles
} from "lucide-react";
import { candidatesApi } from "@/lib/api";
import type { Candidate } from "@/lib/types";

type UploadResult = {
  filename: string;
  status: "success" | "error" | "parsing";
  name?: string;
  headline?: string;
  candidate_id?: string;
  error?: string;
};

const TIER_LABELS: Record<string, { label: string; color: string }> = {
  tier1: { label: "Tier 1", color: "#a78bfa" },
  tier2: { label: "Tier 2", color: "#06b6d4" },
  tier3: { label: "Tier 3", color: "#f59e0b" },
  bootcamp: { label: "Bootcamp", color: "#10b981" },
  "self-taught": { label: "Self-Taught", color: "#f43f5e" },
};

export default function CandidatesPage() {
  const [candidates, setCandidates] = useState<Candidate[]>([]);
  const [loading, setLoading] = useState(true);

  // Upload state
  const [dragOver, setDragOver] = useState(false);
  const [queued, setQueued] = useState<File[]>([]);
  const [uploading, setUploading] = useState(false);
  const [results, setResults] = useState<UploadResult[]>([]);
  const [uploadDone, setUploadDone] = useState(false);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const loadCandidates = () => {
    candidatesApi.list()
      .then(c => { setCandidates(c); setLoading(false); })
      .catch(() => setLoading(false));
  };

  useEffect(() => { loadCandidates(); }, []);

  function addFiles(newFiles: FileList | File[]) {
    const accepted = Array.from(newFiles).filter(f => {
      const ext = f.name.split(".").pop()?.toLowerCase();
      return ["pdf", "docx", "txt", "md"].includes(ext || "");
    });
    setQueued(prev => {
      const existing = new Set(prev.map(f => f.name));
      return [...prev, ...accepted.filter(f => !existing.has(f.name))].slice(0, 20);
    });
    setUploadDone(false);
    setResults([]);
  }

  async function handleUpload() {
    if (!queued.length || uploading) return;
    setUploading(true);
    setResults(queued.map(f => ({ filename: f.name, status: "parsing" })));
    try {
      const res = await candidatesApi.bulkUpload(queued);
      setResults(res.results as UploadResult[]);
      setUploadDone(true);
      setQueued([]);
      // Reload candidate list
      setLoading(true);
      loadCandidates();
    } catch (e: unknown) {
      const msg = e instanceof Error ? e.message : "Upload failed";
      setResults(queued.map(f => ({ filename: f.name, status: "error", error: msg })));
    } finally {
      setUploading(false);
    }
  }

  function removeFile(name: string) {
    setQueued(prev => prev.filter(f => f.name !== name));
  }

  const successCount = results.filter(r => r.status === "success").length;
  const failCount = results.filter(r => r.status === "error").length;

  return (
    <div style={{ maxWidth: 1100 }}>
      {/* Header */}
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 28 }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between" }}>
          <div>
            <h1 style={{ fontSize: 30, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif", marginBottom: 4 }}>
              Candidates
            </h1>
            <p style={{ fontSize: 14, color: "var(--text-secondary)" }}>
              {candidates.length} candidates in the system · Upload resumes to add more
            </p>
          </div>
          <button
            onClick={() => fileInputRef.current?.click()}
            style={{
              display: "flex", alignItems: "center", gap: 8,
              padding: "10px 18px", borderRadius: 10, cursor: "pointer",
              background: "linear-gradient(135deg, #7c3aed, #6d28d9)",
              border: "none", color: "white", fontSize: 13, fontWeight: 600,
              boxShadow: "0 4px 16px rgba(124,58,237,0.35)",
            }}
          >
            <Upload size={15} />
            Upload Resumes
          </button>
        </div>
      </motion.div>

      {/* Bulk Upload Section */}
      <motion.div
        initial={{ opacity: 0, y: 10 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.05 }}
        className="glass-card"
        style={{ padding: 24, marginBottom: 24 }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 16 }}>
          <Sparkles size={16} color="#a78bfa" />
          <span style={{ fontSize: 13, fontWeight: 700, color: "var(--text-secondary)", textTransform: "uppercase", letterSpacing: "0.06em" }}>
            AI Resume Bulk Import
          </span>
          <span style={{ fontSize: 11, color: "var(--text-muted)", marginLeft: 4 }}>
            PDF · DOCX · TXT · up to 20 files
          </span>
        </div>

        {/* Drop zone */}
        <div
          onDragOver={e => { e.preventDefault(); setDragOver(true); }}
          onDragLeave={() => setDragOver(false)}
          onDrop={e => { e.preventDefault(); setDragOver(false); addFiles(e.dataTransfer.files); }}
          onClick={() => !queued.length && fileInputRef.current?.click()}
          style={{
            border: `2px dashed ${dragOver ? "rgba(124,58,237,0.7)" : queued.length ? "rgba(16,185,129,0.4)" : "var(--border-default)"}`,
            borderRadius: 12, padding: queued.length ? "16px" : "32px 16px",
            background: dragOver ? "rgba(124,58,237,0.05)" : "var(--bg-elevated)",
            transition: "all 0.2s ease",
            cursor: queued.length ? "default" : "pointer",
          }}
        >
          {queued.length === 0 ? (
            <div style={{ textAlign: "center" }}>
              <div style={{
                width: 44, height: 44, borderRadius: 12, margin: "0 auto 12px",
                background: dragOver ? "rgba(124,58,237,0.2)" : "rgba(255,255,255,0.05)",
                display: "flex", alignItems: "center", justifyContent: "center",
                transition: "all 0.2s ease",
              }}>
                <Upload size={20} color={dragOver ? "#a78bfa" : "var(--text-muted)"} />
              </div>
              <div style={{ fontSize: 14, fontWeight: 600, color: dragOver ? "#a78bfa" : "var(--text-secondary)", marginBottom: 4 }}>
                Drop resume files here or click to browse
              </div>
              <div style={{ fontSize: 12, color: "var(--text-muted)" }}>
                Each resume will be parsed by AI into a full structured candidate profile
              </div>
            </div>
          ) : (
            <div>
              {/* Queued files */}
              <div style={{ display: "flex", flexWrap: "wrap", gap: 8, marginBottom: queued.length ? 14 : 0 }}>
                {queued.map(f => (
                  <div key={f.name} style={{
                    display: "flex", alignItems: "center", gap: 6,
                    padding: "5px 10px", borderRadius: 8,
                    background: "rgba(124,58,237,0.1)", border: "1px solid rgba(124,58,237,0.25)",
                    fontSize: 12,
                  }}>
                    <FileText size={12} color="#a78bfa" />
                    <span style={{ color: "var(--text-primary)", maxWidth: 160, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                      {f.name}
                    </span>
                    <span style={{ color: "var(--text-muted)", fontSize: 10 }}>
                      {(f.size / 1024).toFixed(0)}KB
                    </span>
                    {!uploading && (
                      <button
                        onClick={e => { e.stopPropagation(); removeFile(f.name); }}
                        style={{ background: "none", border: "none", cursor: "pointer", color: "var(--text-muted)", padding: 0, display: "flex" }}
                      >
                        <X size={12} />
                      </button>
                    )}
                  </div>
                ))}
                {!uploading && (
                  <button
                    onClick={e => { e.stopPropagation(); fileInputRef.current?.click(); }}
                    style={{
                      display: "flex", alignItems: "center", gap: 5,
                      padding: "5px 10px", borderRadius: 8, cursor: "pointer",
                      background: "none", border: "1px dashed var(--border-default)",
                      color: "var(--text-muted)", fontSize: 12,
                    }}
                  >
                    <Upload size={11} /> Add more
                  </button>
                )}
              </div>

              {/* Upload button */}
              {!uploading && !uploadDone && (
                <button
                  onClick={handleUpload}
                  style={{
                    display: "flex", alignItems: "center", gap: 8,
                    padding: "10px 20px", borderRadius: 10, cursor: "pointer",
                    background: "linear-gradient(135deg, #7c3aed, #6d28d9)",
                    border: "none", color: "white", fontSize: 13, fontWeight: 600,
                    boxShadow: "0 4px 16px rgba(124,58,237,0.35)",
                  }}
                >
                  <Sparkles size={14} />
                  Parse & Import {queued.length} Resume{queued.length > 1 ? "s" : ""} with AI
                  <ChevronRight size={14} />
                </button>
              )}
            </div>
          )}
        </div>

        {/* Upload progress / results */}
        <AnimatePresence>
          {results.length > 0 && (
            <motion.div
              key="results"
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: "auto" }}
              exit={{ opacity: 0, height: 0 }}
              style={{ marginTop: 16, overflow: "hidden" }}
            >
              {uploadDone && (
                <div style={{
                  padding: "10px 14px", borderRadius: 10, marginBottom: 12,
                  background: successCount > 0 ? "rgba(16,185,129,0.08)" : "rgba(244,63,94,0.08)",
                  border: `1px solid ${successCount > 0 ? "rgba(16,185,129,0.25)" : "rgba(244,63,94,0.25)"}`,
                  display: "flex", alignItems: "center", gap: 8, fontSize: 13,
                  color: successCount > 0 ? "#10b981" : "#f43f5e",
                }}>
                  <CheckCircle size={14} />
                  {successCount} candidate{successCount !== 1 ? "s" : ""} imported successfully
                  {failCount > 0 && ` · ${failCount} failed`}
                </div>
              )}

              <div style={{ display: "flex", flexDirection: "column", gap: 6 }}>
                {results.map((r, i) => (
                  <motion.div
                    key={r.filename}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ delay: i * 0.05 }}
                    style={{
                      display: "flex", alignItems: "center", gap: 10,
                      padding: "10px 14px", borderRadius: 10,
                      background: r.status === "success" ? "rgba(16,185,129,0.06)"
                        : r.status === "error" ? "rgba(244,63,94,0.06)"
                        : "rgba(124,58,237,0.06)",
                      border: `1px solid ${r.status === "success" ? "rgba(16,185,129,0.2)"
                        : r.status === "error" ? "rgba(244,63,94,0.2)"
                        : "rgba(124,58,237,0.2)"}`,
                    }}
                  >
                    {r.status === "parsing" ? (
                      <Loader2 size={14} color="#a78bfa" style={{ animation: "spin 0.8s linear infinite", flexShrink: 0 }} />
                    ) : r.status === "success" ? (
                      <CheckCircle size={14} color="#10b981" style={{ flexShrink: 0 }} />
                    ) : (
                      <AlertCircle size={14} color="#f43f5e" style={{ flexShrink: 0 }} />
                    )}
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 12, fontWeight: 600, color: "var(--text-primary)" }}>
                        {r.status === "success" ? r.name : r.filename}
                      </div>
                      {r.status === "success" && (
                        <div style={{ fontSize: 11, color: "var(--text-muted)" }}>{r.headline}</div>
                      )}
                      {r.status === "error" && (
                        <div style={{ fontSize: 11, color: "#f43f5e" }}>{r.error}</div>
                      )}
                      {r.status === "parsing" && (
                        <div style={{ fontSize: 11, color: "#a78bfa" }}>AI parsing resume...</div>
                      )}
                    </div>
                    <div style={{ fontSize: 10, color: "var(--text-muted)", flexShrink: 0 }}>
                      {r.filename}
                    </div>
                  </motion.div>
                ))}
              </div>
            </motion.div>
          )}
        </AnimatePresence>
      </motion.div>

      {/* Candidates Grid */}
      {loading ? (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="skeleton" style={{ height: 180, borderRadius: 16 }} />
          ))}
        </div>
      ) : candidates.length === 0 ? (
        <div style={{ textAlign: "center", padding: "60px 20px" }}>
          <div style={{ fontSize: 40, marginBottom: 12 }}>📄</div>
          <div style={{ fontSize: 16, fontWeight: 600, marginBottom: 6 }}>No candidates yet</div>
          <div style={{ fontSize: 13, color: "var(--text-muted)" }}>
            Upload resumes above — the AI will extract full structured profiles automatically
          </div>
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 14 }}>
          {candidates.map((c, i) => {
            const tier = c.education_tier ? TIER_LABELS[c.education_tier] : null;
            const cap = c.capability_profile;
            const skills = (c.skills || []).slice(0, 4).map(s =>
              typeof s === "string" ? s : (s as { name: string }).name
            );

            return (
              <motion.div
                key={c.id}
                initial={{ opacity: 0, scale: 0.97 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.03 }}
              >
                <div className="glass-card" style={{ padding: 20 }}>
                  {/* Header */}
                  <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: 10 }}>
                    <div style={{ flex: 1, minWidth: 0 }}>
                      <div style={{ fontWeight: 700, fontSize: 14, marginBottom: 3 }}>{c.name}</div>
                      <div style={{ fontSize: 11, color: "var(--text-secondary)", overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
                        {c.headline}
                      </div>
                    </div>
                    {tier && (
                      <span style={{
                        fontSize: 9, padding: "3px 8px", borderRadius: 20, marginLeft: 8,
                        background: `${tier.color}15`, color: tier.color,
                        border: `1px solid ${tier.color}30`, fontWeight: 700, whiteSpace: "nowrap", flexShrink: 0
                      }}>
                        {tier.label}
                      </span>
                    )}
                  </div>

                  {/* Meta */}
                  <div style={{ display: "flex", gap: 10, marginBottom: 12, flexWrap: "wrap" }}>
                    {c.location && (
                      <div style={{ display: "flex", alignItems: "center", gap: 3, fontSize: 10, color: "var(--text-muted)" }}>
                        <MapPin size={9} />{c.location}
                      </div>
                    )}
                    <div style={{ fontSize: 10, color: "var(--text-muted)" }}>
                      {c.years_experience}y exp
                    </div>
                  </div>

                  {/* Capability bars */}
                  {cap && (
                    <div style={{ marginBottom: 12 }}>
                      {[
                        { key: "technical_depth", label: "Tech", color: "#7c3aed" },
                        { key: "execution", label: "Exec", color: "#10b981" },
                        { key: "adaptability", label: "Adapt", color: "#06b6d4" },
                      ].map(({ key, label, color }) => (
                        <div key={key} style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 5 }}>
                          <div style={{ fontSize: 9, color: "var(--text-muted)", width: 30 }}>{label}</div>
                          <div className="progress-bar" style={{ flex: 1 }}>
                            <div className="progress-fill" style={{
                              width: `${((cap as unknown as Record<string, number>)[key] || 0) * 100}%`,
                              background: color
                            }} />
                          </div>
                          <div style={{ fontSize: 9, color: "var(--text-secondary)", width: 24, textAlign: "right" }}>
                            {Math.round(((cap as unknown as Record<string, number>)[key] || 0) * 100)}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Skills */}
                  <div style={{ display: "flex", gap: 5, flexWrap: "wrap" }}>
                    {skills.map(s => (
                      <span key={s} style={{
                        fontSize: 9, padding: "2px 6px", borderRadius: 5,
                        background: "var(--bg-elevated)", border: "1px solid var(--border-subtle)",
                        color: "var(--text-secondary)"
                      }}>
                        {s}
                      </span>
                    ))}
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      )}

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.docx,.txt,.md"
        multiple
        style={{ display: "none" }}
        onChange={e => { if (e.target.files) addFiles(e.target.files); }}
      />

      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  );
}
