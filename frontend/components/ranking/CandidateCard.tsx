"use client";

import { motion } from "framer-motion";
import type { RankedCandidate } from "@/lib/types";
import { TrendingUp, Shield, Zap, MapPin, GraduationCap } from "lucide-react";

interface Props {
  ranked: RankedCandidate;
  index: number;
  isSelected: boolean;
  onClick: () => void;
}

const RANK_COLORS = ["#f59e0b", "#94a3b8", "#cd7c3a", "#7c3aed", "#06b6d4"];
const TIER_LABELS: Record<string, string> = {
  tier1: "Tier 1", tier2: "Tier 2", tier3: "Tier 3",
  bootcamp: "Bootcamp", "self-taught": "Self-Taught",
};

function ScorePill({ label, value, color }: { label: string; value: number; color: string }) {
  return (
    <div style={{ display: "flex", flexDirection: "column", alignItems: "center", minWidth: 52 }}>
      <div style={{ fontSize: 16, fontWeight: 800, fontFamily: "'Space Grotesk', sans-serif", color }}>
        {value.toFixed(0)}
      </div>
      <div style={{ fontSize: 9, color: "var(--text-muted)", fontWeight: 500, letterSpacing: "0.04em" }}>
        {label}
      </div>
    </div>
  );
}

export default function CandidateCard({ ranked, index, isSelected, onClick }: Props) {
  const { candidate, fit_score, risk_score, growth_score, success_probability } = ranked;
  const rank = ranked.rank_position;
  const rankColor = RANK_COLORS[Math.min(rank - 1, RANK_COLORS.length - 1)] || "#64748b";

  const trajectory = candidate.temporal_profile?.trajectory || "unknown";
  const trajectoryClass = `trajectory-${trajectory}`;

  const skills = (candidate.skills || []).slice(0, 4).map((s) =>
    typeof s === "string" ? s : s.name
  );

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.06 }}
      onClick={onClick}
      style={{
        padding: "16px 18px",
        borderRadius: 14,
        background: isSelected
          ? "rgba(124,58,237,0.12)"
          : "var(--bg-card)",
        border: isSelected
          ? "1px solid rgba(124,58,237,0.4)"
          : "1px solid var(--border-subtle)",
        cursor: "pointer",
        transition: "all 0.25s ease",
      }}
    >
      <div style={{ display: "flex", alignItems: "flex-start", gap: 14 }}>
        {/* Rank badge */}
        <div style={{
          width: 38, height: 38, borderRadius: 10, flexShrink: 0,
          background: `${rankColor}18`,
          border: `1.5px solid ${rankColor}40`,
          display: "flex", alignItems: "center", justifyContent: "center",
          fontFamily: "'Space Grotesk', sans-serif",
          fontWeight: 800, fontSize: 15, color: rankColor,
        }}>
          {rank}
        </div>

        {/* Info */}
        <div style={{ flex: 1, minWidth: 0 }}>
          <div style={{ display: "flex", alignItems: "center", gap: 8, marginBottom: 2 }}>
            <div style={{ fontWeight: 700, fontSize: 14, whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis" }}>
              {candidate.name}
            </div>
            {trajectory !== "unknown" && (
              <span className={trajectoryClass} style={{ fontSize: 9, padding: "2px 7px", borderRadius: 20, fontWeight: 600 }}>
                {trajectory.toUpperCase()}
              </span>
            )}
          </div>
          <div style={{ fontSize: 11, color: "var(--text-secondary)", marginBottom: 6, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>
            {candidate.headline}
          </div>

          <div style={{ display: "flex", gap: 10, flexWrap: "wrap" }}>
            {candidate.location && (
              <div style={{ display: "flex", alignItems: "center", gap: 3, fontSize: 10, color: "var(--text-muted)" }}>
                <MapPin size={9} />{candidate.location}
              </div>
            )}
            {candidate.education_tier && (
              <div style={{ display: "flex", alignItems: "center", gap: 3, fontSize: 10, color: "var(--text-muted)" }}>
                <GraduationCap size={9} />{TIER_LABELS[candidate.education_tier] || candidate.education_tier}
              </div>
            )}
            <div style={{ fontSize: 10, color: "var(--text-muted)" }}>
              {candidate.years_experience}y exp
            </div>
          </div>
        </div>

        {/* Scores */}
        <div style={{ display: "flex", gap: 8, alignItems: "center" }}>
          <ScorePill label="FIT" value={fit_score} color="#10b981" />
          <div style={{ width: 1, height: 30, background: "var(--border-subtle)" }} />
          <ScorePill label="RISK↓" value={risk_score} color="#f43f5e" />
          <div style={{ width: 1, height: 30, background: "var(--border-subtle)" }} />
          <ScorePill label="GROWTH" value={growth_score} color="#06b6d4" />
        </div>
      </div>

      {/* Skills */}
      {skills.length > 0 && (
        <div style={{ display: "flex", gap: 5, marginTop: 10, flexWrap: "wrap" }}>
          {skills.map((s) => (
            <span key={s} style={{
              fontSize: 9, padding: "2px 7px", borderRadius: 5,
              background: "var(--bg-elevated)",
              border: "1px solid var(--border-subtle)",
              color: "var(--text-secondary)"
            }}>
              {s}
            </span>
          ))}
        </div>
      )}

      {/* Success bar */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, marginTop: 10 }}>
        <div style={{ fontSize: 9, color: "var(--text-muted)", whiteSpace: "nowrap" }}>Success probability</div>
        <div className="progress-bar" style={{ flex: 1 }}>
          <div className="progress-fill" style={{
            width: `${success_probability * 100}%`,
            background: `linear-gradient(90deg, #7c3aed, #06b6d4)`
          }} />
        </div>
        <div style={{ fontSize: 10, fontWeight: 700, color: "#a78bfa", whiteSpace: "nowrap" }}>
          {(success_probability * 100).toFixed(0)}%
        </div>
      </div>
    </motion.div>
  );
}
