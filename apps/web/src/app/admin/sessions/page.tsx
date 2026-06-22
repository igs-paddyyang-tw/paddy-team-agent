"use client";
import useSWR from "swr";
import Link from "next/link";
import { fetcher } from "@/lib/api";

export default function SessionsPage() {
  const { data: sessions } = useSWR("/api/admin/sessions", fetcher);

  const statusColor: Record<string, string> = {
    completed: "text-green-400",
    running: "text-cyan-400",
    failed: "text-red-400",
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Sessions</h2>
      <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-800/50">
            <tr className="text-left text-slate-400">
              <th className="px-4 py-3">ID</th>
              <th className="px-4 py-3">Agent</th>
              <th className="px-4 py-3">Status</th>
              <th className="px-4 py-3">Tokens</th>
              <th className="px-4 py-3">Cost</th>
              <th className="px-4 py-3">Time</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {(!sessions || sessions.length === 0) && (
              <tr><td colSpan={6} className="px-4 py-8 text-center text-slate-500">尚無 Session</td></tr>
            )}
            {sessions?.map((s: any) => (
              <tr key={s.id} className="hover:bg-slate-800/30 transition-colors">
                <td className="px-4 py-3">
                  <Link href={`/admin/sessions/${s.id}`} className="text-cyan-400 hover:underline">
                    {s.id.slice(0, 8)}
                  </Link>
                </td>
                <td className="px-4 py-3">{s.agent_id}</td>
                <td className={`px-4 py-3 ${statusColor[s.status] || ""}`}>{s.status}</td>
                <td className="px-4 py-3 text-slate-400">{s.total_tokens?.toLocaleString()}</td>
                <td className="px-4 py-3 text-orange-400">${s.cost_usd?.toFixed(4)}</td>
                <td className="px-4 py-3 text-slate-500 text-xs">{s.started_at?.slice(0, 16)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
}
