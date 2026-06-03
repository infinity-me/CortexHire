"use client";

import { useEffect, useState, useCallback } from "react";
import { healthApi } from "@/lib/api";
import { Activity, Cpu, Wifi, WifiOff, RefreshCw } from "lucide-react";

const BACKEND_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export default function Header() {
  const [health, setHealth] = useState<{ llm: string; status: string } | null>(null);
  const [connected, setConnected] = useState<boolean | null>(null);
  const [retrying, setRetrying] = useState(false);

  const checkHealth = useCallback(async () => {
    try {
      const h = await healthApi.check();
      setHealth(h);
      setConnected(true);
    } catch {
      setConnected(false);
      setHealth(null);
    }
    setRetrying(false);
  }, []);

  useEffect(() => {
    checkHealth();
    // Re-check every 60s (Render free tier spins down — first check may fail)
    const interval = setInterval(checkHealth, 60_000);
    return () => clearInterval(interval);
  }, [checkHealth]);

  const handleRetry = () => {
    setRetrying(true);
    setConnected(null);
    checkHealth();
  };

  const isProduction = BACKEND_URL.includes("onrender.com");

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
        <span style={{ fontSize: 13, color: "var(--text-secondary)", fontWeight: 500 }}>
          AI Recruitment Intelligence System
        </span>
      </div>

      <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
        {/* Environment badge */}
        <div
          title={`Backend: ${BACKEND_URL}`}
          style={{
            fontSize: 10, fontWeight: 700, padding: "3px 8px", borderRadius: 10,
            background: isProduction ? "rgba(16,185,129,0.12)" : "rgba(245,158,11,0.12)",
            border: `1px solid ${isProduction ? "rgba(16,185,129,0.25)" : "rgba(245,158,11,0.25)"}`,
            color: isProduction ? "#10b981" : "#f59e0b",
            letterSpacing: "0.05em", textTransform: "uppercase" as const,
            cursor: "help",
          }}
        >
          {isProduction ? "⚡ Render" : "🔧 Local"}
        </div>

        {/* LLM Provider */}
        {health && (
          <div
            style={{
              display: "flex", alignItems: "center", gap: 6,
              padding: "5px 12px", borderRadius: 20,
              background: "rgba(124,58,237,0.12)",
              border: "1px solid rgba(124,58,237,0.25)",
              fontSize: 12, color: "#a78bfa", fontWeight: 600,
            }}
          >
            <Cpu size={12} />
            {health.llm.toUpperCase()}
          </div>
        )}

        {/* Connection status */}
        <div
          style={{
            display: "flex", alignItems: "center", gap: 6,
            padding: "5px 12px", borderRadius: 20,
            background: connected
              ? "rgba(16,185,129,0.10)"
              : connected === false
              ? "rgba(244,63,94,0.10)"
              : "rgba(100,116,139,0.10)",
            border: `1px solid ${
              connected ? "rgba(16,185,129,0.25)"
              : connected === false ? "rgba(244,63,94,0.25)"
              : "rgba(100,116,139,0.25)"
            }`,
            fontSize: 12,
            color: connected ? "#10b981" : connected === false ? "#f43f5e" : "var(--text-muted)",
            fontWeight: 500,
          }}
        >
          {retrying
            ? <RefreshCw size={12} style={{ animation: "spin 0.8s linear infinite" }} />
            : connected
            ? <Wifi size={12} />
            : <WifiOff size={12} />
          }
          {connected === null ? "Connecting..." : connected ? "API Online" : "API Offline"}
        </div>

        {/* Retry button — only show when offline */}
        {connected === false && !retrying && (
          <button
            onClick={handleRetry}
            title="Retry connection (Render free tier may be sleeping)"
            style={{
              padding: "5px 10px", borderRadius: 8, cursor: "pointer",
              background: "rgba(244,63,94,0.15)", border: "1px solid rgba(244,63,94,0.3)",
              color: "#f43f5e", fontSize: 11, fontWeight: 600,
              display: "flex", alignItems: "center", gap: 4,
            }}
          >
            <RefreshCw size={11} /> Wake up
          </button>
        )}
      </div>

      <style>{`@keyframes spin { to { transform: rotate(360deg); } }`}</style>
    </header>
  );
}
