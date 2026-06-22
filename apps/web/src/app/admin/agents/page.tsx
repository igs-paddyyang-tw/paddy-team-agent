"use client";
import useSWR from "swr";
import { fetcher } from "@/lib/api";

const roleIcons: Record<string, string> = { admin: "⚙️", leader: "🧠", worker: "💻" };
const statusDot: Record<string, string> = { idle: "bg-green-500", busy: "bg-cyan-500", offline: "bg-red-500" };

export default function AgentsPage() {
  const { data: agents } = useSWR("/api/agents", fetcher);

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Agents</h2>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {agents?.map((a: any) => (
          <div key={a.id} className="bg-slate-900 border border-slate-800 rounded-lg p-4">
            <div className="flex items-center gap-3 mb-3">
              <span className={`w-3 h-3 rounded-full ${statusDot[a.status] || "bg-gray-500"}`} />
              <span className="text-lg">{roleIcons[a.role] || "🤖"}</span>
              <h3 className="font-medium">{a.name}</h3>
            </div>
            <div className="space-y-1 text-sm text-slate-400">
              <div>Role: <span className="text-slate-300">{a.role}</span></div>
              <div>Provider: <span className="text-slate-300">{a.provider}</span></div>
              <div>Model: <span className="text-slate-300">{a.model}</span></div>
              <div>Status: <span className="text-slate-300">{a.status}</span></div>
            </div>
          </div>
        ))}
        {(!agents || agents.length === 0) && (
          <p className="text-slate-500 col-span-full text-center py-8">尚無 Agent</p>
        )}
      </div>
    </div>
  );
}
