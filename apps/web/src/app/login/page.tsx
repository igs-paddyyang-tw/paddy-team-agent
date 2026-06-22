"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { setApiKey } from "@/lib/api";

export default function LoginPage() {
  const [key, setKey] = useState("");
  const [error, setError] = useState("");
  const router = useRouter();

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    try {
      const res = await fetch(
        `${process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:33333"}/api/health`,
        { headers: { "X-API-Key": key } }
      );
      if (res.ok) {
        setApiKey(key);
        router.push("/admin/dashboard");
      } else {
        setError("Invalid API Key");
      }
    } catch {
      setError("Cannot connect to backend");
    }
  }

  return (
    <div className="min-h-screen bg-slate-950 flex items-center justify-center">
      <form onSubmit={handleSubmit} className="bg-slate-900 p-8 rounded-lg border border-slate-800 w-80">
        <h1 className="text-xl font-bold text-cyan-400 mb-6 text-center">⚡ Ark Platform</h1>
        <input
          type="password"
          placeholder="API Key"
          value={key}
          onChange={(e) => setKey(e.target.value)}
          className="w-full px-3 py-2 bg-slate-800 border border-slate-700 rounded text-sm text-slate-200 mb-4"
        />
        {error && <p className="text-red-400 text-xs mb-3">{error}</p>}
        <button
          type="submit"
          className="w-full py-2 bg-cyan-600 hover:bg-cyan-500 rounded text-sm font-medium transition-colors"
        >
          Login
        </button>
        <p className="text-xs text-slate-500 mt-4 text-center">
          開發模式：留空直接進入
        </p>
      </form>
    </div>
  );
}
