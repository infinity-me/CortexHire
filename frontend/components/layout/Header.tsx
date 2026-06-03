"use client";

import { useEffect, useState } from "react";
import { healthApi } from "@/lib/api";
import { Activity, Cpu, Wifi, WifiOff } from "lucide-react";

export default function Header() {
  const [health, setHealth] = useState<{ llm: string; status: string } | null>(null);
  const [connected, setConnected] = useState<boolean | null>(null);

  useEffect(() => {
    healthApi.check()
      .then((h) => { setHealth(h); setConnected(true); })
      .catch(() => setConnected(false));
  }, []);

  return (
    <header
      style={{
        height: 64,
        borderBottom: "1px solid var(--border-subtle)",
        background: "var(--bg-surface)",
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "0 32px",
        position: "sticky",
        top: 0,
        zIndex: 40,
      }}
    >
      <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
        <Activity size={16} color="var(--cortex-purple)" />
        <span
          style={{
            fontSize: 13,
            color: "var(--text-secondary)",
            fontWeight: 500,
          }}
        >
          AI Recruitment Intelligence System
        </span>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
        {/* LLM Provider */}
        {health && (
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: 6,
              padding: "5px 12px",
              borderRadius: 20,
              background: "rgba(124,58,237,0.12)",
              border: "1px solid rgba(124,58,237,0.25)",
              fontSize: 12,
              color: "#a78bfa",
              fontWeight: 500,
            }}
          >
            <Cpu size={12} />
            {health.llm.toUpperCase()}
          </div>
        )}

        {/* Connection status */}
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: 6,
            padding: "5px 12px",
            borderRadius: 20,
            background: connected
              ? "rgba(16,185,129,0.10)"
              : connected === false
              ? "rgba(244,63,94,0.10)"
              : "rgba(100,116,139,0.10)",
            border: `1px solid ${connected ? "rgba(16,185,129,0.25)" : connected === false ? "rgba(244,63,94,0.25)" : "rgba(100,116,139,0.25)"}`,
            fontSize: 12,
            color: connected ? "#10b981" : connected === false ? "#f43f5e" : "var(--text-muted)",
            fontWeight: 500,
          }}
        >
          {connected ? <Wifi size={12} /> : <WifiOff size={12} />}
          {connected === null ? "Connecting..." : connected ? "API Online" : "API Offline"}
        </div>
      </div>
    </header>
  );
}
