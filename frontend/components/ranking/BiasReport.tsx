"use client";

import { motion } from "framer-motion";
import type { BiasReport as BiasReportType } from "@/lib/types";
import { Shield, AlertTriangle, CheckCircle, Info } from "lucide-react";

interface Props {
  report: BiasReportType;
}

const FLAG_LABELS: Record<string, { label: string; color: string; emoji: string }> = {
  "prestige_halo_detected": { label: "Prestige Halo Detected", color: "#f59e0b", emoji: "⚠️" },
  "pedigree_bias_correction_applied": { label: "Pedigree Correction Applied", color: "#10b981", emoji: "✅" },
  "career_gap_detected_contextualized": { label: "Career Gap Contextualized", color: "#06b6d4", emoji: "📋" },
  "gap_productive_learning_detected": { label: "Productive Gap Learning", color: "#10b981", emoji: "✅" },
  "geographic_underrepresentation_detected": { label: "Geographic Bias Corrected", color: "#a78bfa", emoji: "🌍" },
  "non_traditional_path_high_achiever": { label: "Non-Traditional High Achiever", color: "#10b981", emoji: "⭐" },
};

export default function BiasReport({ report }: Props) {
  const flags = report.bias_flags || [];
  const adjustment = report.raw_adjustment || 0;
  const isPositive = adjustment > 0;

  return (
    <div>
      <div style={{ fontSize: 12, fontWeight: 700, color: "var(--text-muted)", marginBottom: 16, letterSpacing: "0.08em" }}>
        ETHICAL AI — BIAS ANALYSIS
      </div>

      {/* Score adjustment */}
      <motion.div
        initial={{ opacity: 0, scale: 0.95 }}
        animate={{ opacity: 1, scale: 1 }}
        style={{
          padding: 20, borderRadius: 14, marginBottom: 14,
          background: isPositive
            ? "rgba(16,185,129,0.08)"
            : adjustment < 0
            ? "rgba(244,63,94,0.08)"
            : "var(--bg-elevated)",
          border: `1px solid ${isPositive ? "rgba(16,185,129,0.25)" : adjustment < 0 ? "rgba(244,63,94,0.25)" : "var(--border-subtle)"}`,
          textAlign: "center"
        }}
      >
        <div style={{ fontSize: 11, color: "var(--text-muted)", marginBottom: 6, fontWeight: 600 }}>BIAS SCORE ADJUSTMENT</div>
        <div style={{
          fontSize: 42, fontWeight: 900, fontFamily: "'Space Grotesk', sans-serif",
          color: isPositive ? "#10b981" : adjustment < 0 ? "#f43f5e" : "var(--text-secondary)"
        }}>
          {isPositive ? "+" : ""}{adjustment.toFixed(1)} pts
        </div>
        <div style={{ fontSize: 12, color: "var(--text-secondary)", marginTop: 4 }}>
          {isPositive
            ? "Positive correction — underrepresented talent or non-traditional path"
            : adjustment < 0
            ? "Negative adjustment — pedigree signals without commensurate output"
            : "No significant bias detected"}
        </div>
      </motion.div>

      {/* Bias flags */}
      {flags.length > 0 ? (
        <div style={{ marginBottom: 14 }}>
          <div style={{ fontSize: 11, fontWeight: 700, color: "var(--text-muted)", marginBottom: 10 }}>DETECTED BIAS SIGNALS</div>
          {flags.map((flag, i) => {
            const info = FLAG_LABELS[flag] || { label: flag, color: "#94a3b8", emoji: "🔍" };
            return (
              <motion.div
                key={flag}
                initial={{ opacity: 0, x: -10 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: i * 0.08 }}
                style={{
                  display: "flex", alignItems: "center", gap: 10,
                  padding: "10px 14px", borderRadius: 10, marginBottom: 8,
                  background: `${info.color}0f`,
                  border: `1px solid ${info.color}25`
                }}
              >
                <span style={{ fontSize: 16 }}>{info.emoji}</span>
                <span style={{ fontSize: 12, color: info.color, fontWeight: 600 }}>{info.label}</span>
              </motion.div>
            );
          })}
        </div>
      ) : (
        <div style={{
          display: "flex", alignItems: "center", gap: 10,
          padding: "14px 16px", borderRadius: 12, marginBottom: 14,
          background: "rgba(16,185,129,0.08)", border: "1px solid rgba(16,185,129,0.25)"
        }}>
          <CheckCircle size={16} color="#10b981" />
          <span style={{ fontSize: 13, color: "#10b981" }}>No significant bias signals detected</span>
        </div>
      )}

      {/* Indicator pills */}
      <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: 8, marginBottom: 14 }}>
        {[
          { label: "Prestige Halo", active: report.has_prestige_halo, warn: true },
          { label: "Gap Penalized", active: report.has_gap_penalty, warn: false },
          { label: "Pedigree Corrected", active: report.has_pedigree_correction, warn: false },
          { label: "Geo Corrected", active: report.has_geo_correction, warn: false },
        ].map(({ label, active, warn }) => (
          <div key={label} style={{
            display: "flex", alignItems: "center", gap: 8,
            padding: "8px 12px", borderRadius: 8,
            background: active
              ? (warn ? "rgba(245,158,11,0.10)" : "rgba(16,185,129,0.10)")
              : "var(--bg-elevated)",
            border: "1px solid var(--border-subtle)"
          }}>
            <div style={{
              width: 6, height: 6, borderRadius: "50%",
              background: active ? (warn ? "#f59e0b" : "#10b981") : "var(--text-muted)"
            }} />
            <span style={{ fontSize: 11, color: active ? (warn ? "#f59e0b" : "#10b981") : "var(--text-muted)" }}>
              {label}
            </span>
          </div>
        ))}
      </div>

      {/* Recommendation */}
      <div style={{
        padding: 14, borderRadius: 12,
        background: "var(--bg-elevated)", border: "1px solid var(--border-subtle)"
      }}>
        <div style={{ display: "flex", alignItems: "center", gap: 6, marginBottom: 8 }}>
          <Info size={13} color="#a78bfa" />
          <span style={{ fontSize: 11, fontWeight: 700, color: "#a78bfa" }}>RECRUITER RECOMMENDATION</span>
        </div>
        <p style={{ fontSize: 12, color: "var(--text-secondary)", lineHeight: 1.6 }}>
          {report.recommendation}
        </p>
      </div>
    </div>
  );
}
