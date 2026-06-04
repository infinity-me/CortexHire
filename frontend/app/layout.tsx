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
  icons: {
    icon: [
      { url: "/favicon.svg", type: "image/svg+xml" },
      { url: "/favicon.png", type: "image/png" },
    ],
    apple: "/favicon.png",
    shortcut: "/favicon.png",
  },
  openGraph: {
    title: "CortexHire — AI Recruitment Intelligence",
    description: "Don't hire resumes. Hire potential. AI-powered candidate ranking that thinks like an elite recruiter.",
    images: [{ url: "/logo.png", width: 1200, height: 630, alt: "CortexHire Logo" }],
    type: "website",
  },
  twitter: {
    card: "summary_large_image",
    title: "CortexHire — AI Recruitment Intelligence",
    description: "Don't hire resumes. Hire potential.",
    images: ["/logo.png"],
  },
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
