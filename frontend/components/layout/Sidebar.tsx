"use client";

import Link from "next/link";
import Image from "next/image";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard, Briefcase, Users, TrendingUp,
  Bot, Video, X, Trophy,
} from "lucide-react";

const NAV = [
  { href: "/",           label: "Command Center", icon: LayoutDashboard },
  { href: "/jobs",       label: "Jobs",           icon: Briefcase },
  { href: "/candidates", label: "Candidates",     icon: Users },
  { href: "/ranking",    label: "Rankings",       icon: TrendingUp },
  { href: "/interview",  label: "Live Interview", icon: Video },
];

interface SidebarProps {
  open?: boolean;
  onClose?: () => void;
}

export default function Sidebar({ open = false, onClose }: SidebarProps) {
  const pathname = usePathname();

  return (
    <>
      {/* Overlay — mobile only */}
      <div
        className={`sidebar-overlay ${open ? "open" : ""}`}
        onClick={onClose}
        aria-hidden="true"
      />

      <aside className={`layout-sidebar ${open ? "open" : ""}`}
        style={{
          background: "var(--bg-surface)",
          borderRight: "1px solid var(--border-subtle)",
          display: "flex",
          flexDirection: "column",
        }}
      >
        {/* Logo */}
        <div style={{
          padding: "24px 20px 20px",
          borderBottom: "1px solid var(--border-subtle)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <div style={{
              width: 36, height: 36, borderRadius: 10,
              background: "#080b14",
              border: "1px solid rgba(124,58,237,0.35)",
              display: "flex", alignItems: "center", justifyContent: "center",
              boxShadow: "0 0 16px rgba(124,58,237,0.35), 0 0 4px rgba(6,182,212,0.2)",
              flexShrink: 0,
              overflow: "hidden",
            }}>
              <Image src="/favicon.svg" alt="CortexHire" width={36} height={36} style={{ display: "block" }} />
            </div>
            <div>
              <div style={{
                fontFamily: "'Space Grotesk', sans-serif",
                fontWeight: 700, fontSize: 17,
                background: "linear-gradient(135deg, #a78bfa, #06b6d4)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}>
                CortexHire
              </div>
              <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 1 }}>
                AI Intelligence
              </div>
            </div>
          </div>

          {/* Close button — visible only on mobile via CSS */}
          <button
            onClick={onClose}
            aria-label="Close menu"
            style={{
              display: "flex", alignItems: "center", justifyContent: "center",
              width: 30, height: 30, borderRadius: 8, border: "none",
              background: "rgba(244,63,94,0.12)", color: "#f43f5e", cursor: "pointer",
            }}
            className="hamburger-btn"
          >
            <X size={16} />
          </button>
        </div>

        {/* Nav */}
        <nav style={{ flex: 1, padding: "16px 12px", overflowY: "auto" }}>
          <div style={{ marginBottom: 6, padding: "0 8px" }}>
            <span style={{ fontSize: 10, fontWeight: 600, color: "var(--text-muted)", letterSpacing: "0.08em", textTransform: "uppercase" }}>
              Navigation
            </span>
          </div>
          {NAV.map(({ href, label, icon: Icon }) => {
            const isActive = pathname === href || (href !== "/" && pathname.startsWith(href));
            return (
              <Link key={href} href={href} className={`sidebar-link ${isActive ? "active" : ""}`}
                onClick={onClose}>
                <Icon size={16} />
                {label}
              </Link>
            );
          })}

          {/* Challenge section */}
          <div style={{ margin: "20px 0 6px", padding: "0 8px" }}>
            <span style={{ fontSize: 10, fontWeight: 600, color: "var(--text-muted)", letterSpacing: "0.08em", textTransform: "uppercase" }}>
              Hackathon
            </span>
          </div>
          <Link
            href="/challenge"
            className={`sidebar-link ${pathname === "/challenge" ? "active" : ""}`}
            onClick={onClose}
            style={{
              background: pathname === "/challenge"
                ? "linear-gradient(135deg, rgba(245,158,11,0.2), rgba(251,191,36,0.1))"
                : "linear-gradient(135deg, rgba(245,158,11,0.08), rgba(251,191,36,0.04))",
              border: "1px solid rgba(245,158,11,0.3)",
              color: pathname === "/challenge" ? "#f59e0b" : "#fbbf24",
            }}
          >
            <Trophy size={16} />
            Challenge Ranker
          </Link>

          <div style={{ margin: "20px 0 6px", padding: "0 8px" }}>
            <span style={{ fontSize: 10, fontWeight: 600, color: "var(--text-muted)", letterSpacing: "0.08em", textTransform: "uppercase" }}>
              Copilot
            </span>
          </div>
          <Link
            href="/copilot"
            className={`sidebar-link ${pathname === "/copilot" ? "active" : ""}`}
            onClick={onClose}
            style={{
              background: pathname === "/copilot" ? undefined : "rgba(124,58,237,0.06)",
              border: "1px solid rgba(124,58,237,0.15)",
            }}
          >
            <Bot size={16} />
            Recruiter Copilot
          </Link>
        </nav>

        {/* Footer */}
        <div style={{
          padding: "16px 20px",
          borderTop: "1px solid var(--border-subtle)",
          fontSize: 11, color: "var(--text-muted)",
        }}>
          <div style={{ marginBottom: 4, fontWeight: 600, color: "var(--text-secondary)" }}>
            CortexHire v1.0
          </div>
          <div>Don&apos;t hire resumes.</div>
          <div>Hire potential.</div>
        </div>
      </aside>
    </>
  );
}
