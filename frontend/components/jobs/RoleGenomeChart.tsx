"use client";

import {
  Radar, RadarChart, PolarGrid, PolarAngleAxis, ResponsiveContainer, Tooltip
} from "recharts";
import type { RoleGenome } from "@/lib/types";

interface Props {
  genome: RoleGenome;
  size?: number;
}

const GENOME_LABELS: Record<string, string> = {
  technical_depth: "Technical",
  ambiguity_tolerance: "Ambiguity",
  ownership: "Ownership",
  communication: "Comms",
  startup_readiness: "Startup",
  leadership_potential: "Leadership",
  creativity: "Creativity",
  execution_speed: "Execution",
};

export default function RoleGenomeChart({ genome, size = 320 }: Props) {
  const data = Object.entries(GENOME_LABELS).map(([key, label]) => ({
    dimension: label,
    value: Math.round((genome[key as keyof RoleGenome] as number) * 100),
    fullMark: 100,
  }));

  return (
    <div style={{ width: "100%", height: size }}>
      <ResponsiveContainer width="100%" height="100%">
        <RadarChart data={data} margin={{ top: 10, right: 20, bottom: 10, left: 20 }}>
          <PolarGrid
            gridType="polygon"
            stroke="rgba(255,255,255,0.08)"
            strokeWidth={1}
          />
          <PolarAngleAxis
            dataKey="dimension"
            tick={{ fill: "#94a3b8", fontSize: 11, fontWeight: 500 }}
            axisLine={false}
          />
          <Radar
            name="Role Requirement"
            dataKey="value"
            stroke="#7c3aed"
            fill="#7c3aed"
            fillOpacity={0.25}
            strokeWidth={2}
            dot={{ fill: "#a78bfa", strokeWidth: 0, r: 4 }}
          />
          <Tooltip
            contentStyle={{
              background: "#1a2035",
              border: "1px solid rgba(124,58,237,0.3)",
              borderRadius: 10,
              fontSize: 12,
              color: "#f1f5f9",
            }}
            formatter={(val) => [`${val}%`, "Required"]}
          />
        </RadarChart>
      </ResponsiveContainer>
    </div>
  );
}
