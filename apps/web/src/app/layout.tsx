import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Ark Agent Platform",
  description: "AI Agent Team Management Dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="zh-TW" className="dark">
      <body className="antialiased">{children}</body>
    </html>
  );
}
