import type { NextConfig } from "next";

const API_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const nextConfig: NextConfig = {
  // Proxy /api/* → backend (works both locally and on Vercel)
  async rewrites() {
    return [
      {
        source: "/api/:path*",
        destination: `${API_URL}/api/:path*`,
      },
    ];
  },

  // Security & caching headers
  async headers() {
    return [
      {
        source: "/(.*)",
        headers: [
          { key: "X-Content-Type-Options", value: "nosniff" },
          { key: "X-Frame-Options", value: "DENY" },
          { key: "Referrer-Policy", value: "strict-origin-when-cross-origin" },
        ],
      },
    ];
  },

  // Allow images from backend (if any)
  images: {
    remotePatterns: [
      { protocol: "https", hostname: "cortexhire.onrender.com" },
    ],
  },
};

export default nextConfig;
