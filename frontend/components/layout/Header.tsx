"use client";

import { useEffect, useState, useCallback } from "react";
import { healthApi } from "@/lib/api";
import { Activity, Cpu, Wifi, WifiOff, RefreshCw, Menu } from "lucide-react";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

interface HeaderProps {
  onMenuClick: () => void;
}

export default function Header({ onMenuClick }: HeaderProps) {
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
    <header style={{
      height: "var(--header-height)",
      borderBottom: "1px solid var(--border-subtle)",
      background: "var(--bg-surface)",
      display: "flex",
      alignItems: "center",
      justifyContent: "space-between",
      padding: "0 20px",
      position: "sticky",
      top: 0,
      zIndex: 40,
      gap: 12,
    }}>
      {/* Left: hamburger + title */}
      <div style={{ display: "flex", alignItems: "center", gap: 12, minWidth: 0 }}>
        {/* Hamburger — shown on tablet/mobile via CSS */}
        <button
          className="hamburger-btn"
          onClick={onMenuClick}
          aria-label="Open menu"
        >
          <Menu size={18} />
        </button>

        <div style={{ display: "flex", alignItems: "center", gap: 8 }}>
          <Activity size={16} color="var(--cortex-purple)" style={{ flexShrink: 0 }} />
          <span style={{
            fontSize: 13, color: "var(--text-secondary)", fontWeight: 500,
            whiteSpace: "nowrap", overflow: "hidden", textOverflow: "ellipsis",
          }} className="hide-mobile">
            AI Recruitment Intelligence System
          </span>
        </div>
      </div>

      {/* Right: status badges */}
      <div style={{ display: "flex", alignItems: "center", gap: 8, flexShrink: 0 }}>
        {/* Environment badge */}
        <div
          title={`Backend: ${BACKEND_URL}`}
          style={{
            fontSize: 10, fontWeight: 700, padding: "3px 8px", borderRadius: 10,
            background: isProduction ? "rgba(16,185,129,0.12)" : "rgba(245,158,11,0.12)",
            border: `1px solid ${isProduction ? "rgba(16,185,129,0.25)" : "rgba(245,158,11,0.25)"}`,
            color: isProduction ? "#10b981" : "#f59e0b",
            letterSpacing: "0.05em", textTransform: "uppercase" as const,
            cursor: "help", whiteSpace: "nowrap",
          }}
        >
          {isProduction ? "⚡ Render" : "🔧 Local"}
        </div>

        {/* LLM Provider — hide on small mobile */}
        {health && (
          <div
            className="hide-mobile"
            style={{
              display: "flex", alignItems: "center", gap: 6,
              padding: "5px 12px", borderRadius: 20,
              background: "rgba(124,58,237,0.12)",
              border: "1px solid rgba(124,58,237,0.25)",
              fontSize: 12, color: "#a78bfa", fontWeight: 600, whiteSpace: "nowrap",
            }}
          >
            <Cpu size={12} />
            {health.llm.toUpperCase()}
          </div>
        )}

        {/* Connection status */}
        <div style={{
          display: "flex", alignItems: "center", gap: 6,
          padding: "5px 10px", borderRadius: 20,
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
          fontSize: 12, fontWeight: 500, whiteSpace: "nowrap",
          color: connected ? "#10b981" : connected === false ? "#f43f5e" : "var(--text-muted)",
        }}>
          {retrying
            ? <RefreshCw size={12} style={{ animation: "spin 0.8s linear infinite" }} />
            : connected ? <Wifi size={12} /> : <WifiOff size={12} />
          }
          <span className="hide-mobile">
            {connected === null ? "Connecting..." : connected ? "API Online" : "API Offline"}
          </span>
        </div>

        {/* Retry button */}
        {connected === false && !retrying && (
          <button
            onClick={handleRetry}
            title="Retry connection"
            style={{
              padding: "5px 10px", borderRadius: 8, cursor: "pointer",
              background: "rgba(244,63,94,0.15)", border: "1px solid rgba(244,63,94,0.3)",
              color: "#f43f5e", fontSize: 11, fontWeight: 600,
              display: "flex", alignItems: "center", gap: 4, whiteSpace: "nowrap",
            }}
          >
            <RefreshCw size={11} />
            <span className="hide-mobile">Wake up</span>
          </button>
        )}
      </div>
    </header>
  );
}
