import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import LayoutShell from "@/components/layout/LayoutShell";

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
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en" className={inter.variable}>
      <head>
        <meta name="viewport" content="width=device-width, initial-scale=1" />
        <link
          href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>
        <LayoutShell>{children}</LayoutShell>
      </body>
    </html>
  );
}
