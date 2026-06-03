import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/layout/Sidebar";
import Header from "@/components/layout/Header";

const inter = Inter({
  subsets: ["latin"],
  weight: ["300", "400", "500", "600", "700", "800", "900"],
  variable: "--font-inter",
  display: "swap",
});

export const metadata: Metadata = {
  title: "CortexHire — AI Recruitment Intelligence",
  description:
    "Don't hire resumes. Hire potential. AI-powered candidate ranking that thinks like an elite recruiter.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <div style={{ display: "flex", minHeight: "100vh", background: "var(--bg-base)" }}>
          <Sidebar />
          <div style={{ flex: 1, display: "flex", flexDirection: "column", marginLeft: "240px" }}>
            <Header />
            <main style={{ flex: 1, padding: "28px 32px" }}>{children}</main>
          </div>
        </div>
      </body>
    </html>
  );
}
