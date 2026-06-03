"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { motion } from "framer-motion";
import { Users, MapPin, GraduationCap, TrendingUp, ChevronRight } from "lucide-react";
import { candidatesApi } from "@/lib/api";
import type { Candidate } from "@/lib/types";

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

  useEffect(() => {
    candidatesApi.list().then((c) => { setCandidates(c); setLoading(false); }).catch(() => setLoading(false));
  }, []);

  return (
    <div style={{ maxWidth: 1100 }}>
      <motion.div initial={{ opacity: 0, y: -10 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 32 }}>
        <h1 style={{ fontSize: 30, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif", marginBottom: 6 }}>
          Candidates
        </h1>
        <p style={{ fontSize: 14, color: "var(--text-secondary)" }}>
          {candidates.length} candidates in the system
        </p>
      </motion.div>

      {loading ? (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
          {Array.from({length: 6}).map((_, i) => (
            <div key={i} className="skeleton" style={{ height: 180, borderRadius: 16 }} />
          ))}
        </div>
      ) : (
        <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr 1fr", gap: 14 }}>
          {candidates.map((c, i) => {
            const tier = c.education_tier ? TIER_LABELS[c.education_tier] : null;
            const cap = c.capability_profile;
            const trajectory = (c as any).temporal_profile?.trajectory;

            const skills = (c.skills || []).slice(0, 3).map((s) =>
              typeof s === "string" ? s : (s as any).name
            );

            return (
              <motion.div
                key={c.id}
                initial={{ opacity: 0, scale: 0.97 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: i * 0.04 }}
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
                        background: `${tier.color}12`, color: tier.color,
                        border: `1px solid ${tier.color}30`, fontWeight: 700, whiteSpace: "nowrap"
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

                  {/* Capability bars (mini) */}
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
                              width: `${((cap as any)[key] || 0) * 100}%`,
                              background: color
                            }} />
                          </div>
                          <div style={{ fontSize: 9, color: "var(--text-secondary)", width: 24, textAlign: "right" }}>
                            {Math.round(((cap as any)[key] || 0) * 100)}
                          </div>
                        </div>
                      ))}
                    </div>
                  )}

                  {/* Skills */}
                  <div style={{ display: "flex", gap: 5, flexWrap: "wrap" }}>
                    {skills.map((s) => (
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
    </div>
  );
}
