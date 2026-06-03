"use client";

import { useState } from "react";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

export default function LayoutShell({ children }: { children: React.ReactNode }) {
  const [sidebarOpen, setSidebarOpen] = useState(false);

  return (
    <div className="layout-shell">
      <Sidebar open={sidebarOpen} onClose={() => setSidebarOpen(false)} />
      <div className="layout-body">
        <Header onMenuClick={() => setSidebarOpen(true)} />
        <main className="layout-main">{children}</main>
      </div>
    </div>
  );
}
