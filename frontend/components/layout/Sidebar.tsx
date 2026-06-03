"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  LayoutDashboard,
  Briefcase,
  Users,
  TrendingUp,
  Bot,
  Zap,
  Video,
} from "lucide-react";

const NAV = [
  { href: "/", label: "Command Center", icon: LayoutDashboard },
  { href: "/jobs", label: "Jobs", icon: Briefcase },
  { href: "/candidates", label: "Candidates", icon: Users },
  { href: "/ranking", label: "Rankings", icon: TrendingUp },
  { href: "/interview", label: "Live Interview", icon: Video },
];

export default function Sidebar() {
  const pathname = usePathname();

  return (
    <aside
      style={{
        width: 240,
        minHeight: "100vh",
        background: "var(--bg-surface)",
        borderRight: "1px solid var(--border-subtle)",
        position: "fixed",
        top: 0,
        left: 0,
        display: "flex",
        flexDirection: "column",
        zIndex: 50,
      }}
    >
      {/* Logo */}
      <div
        style={{
          padding: "24px 20px 20px",
          borderBottom: "1px solid var(--border-subtle)",
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <div
            style={{
              width: 36,
              height: 36,
              borderRadius: 10,
              background: "linear-gradient(135deg, #7c3aed, #06b6d4)",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              boxShadow: "0 0 20px rgba(124,58,237,0.4)",
            }}
          >
            <Zap size={18} color="white" fill="white" />
          </div>
          <div>
            <div
              style={{
                fontFamily: "'Space Grotesk', sans-serif",
                fontWeight: 700,
                fontSize: 17,
                background: "linear-gradient(135deg, #a78bfa, #06b6d4)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent",
              }}
            >
              CortexHire
            </div>
            <div style={{ fontSize: 10, color: "var(--text-muted)", marginTop: 1 }}>
              AI Intelligence
            </div>
          </div>
        </div>
      </div>

      {/* Nav */}
      <nav style={{ flex: 1, padding: "16px 12px" }}>
        <div style={{ marginBottom: 6, padding: "0 8px" }}>
          <span style={{ fontSize: 10, fontWeight: 600, color: "var(--text-muted)", letterSpacing: "0.08em", textTransform: "uppercase" }}>
            Navigation
          </span>
        </div>
        {NAV.map(({ href, label, icon: Icon }) => {
          const isActive = pathname === href || (href !== "/" && pathname.startsWith(href));
          return (
            <Link
              key={href}
              href={href}
              className={`sidebar-link ${isActive ? "active" : ""}`}
            >
              <Icon size={16} />
              {label}
            </Link>
          );
        })}

        <div style={{ margin: "20px 0 6px", padding: "0 8px" }}>
          <span style={{ fontSize: 10, fontWeight: 600, color: "var(--text-muted)", letterSpacing: "0.08em", textTransform: "uppercase" }}>
            Copilot
          </span>
        </div>
        <Link
          href="/copilot"
          className={`sidebar-link ${pathname === "/copilot" ? "active" : ""}`}
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
      <div
        style={{
          padding: "16px 20px",
          borderTop: "1px solid var(--border-subtle)",
          fontSize: 11,
          color: "var(--text-muted)",
        }}
      >
        <div style={{ marginBottom: 4, fontWeight: 600, color: "var(--text-secondary)" }}>
          CortexHire v1.0
        </div>
        <div>Don&apos;t hire resumes.</div>
        <div>Hire potential.</div>
      </div>
    </aside>
  );
}
