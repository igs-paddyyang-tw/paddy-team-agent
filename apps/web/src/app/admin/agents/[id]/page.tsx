"use client";
import { useParams } from "next/navigation";
import useSWR from "swr";
import { fetcher } from "@/lib/api";
import Link from "next/link";

export default function AgentDetailPage() {
  const { id } = useParams<{ id: string }>();
  const { data: agent } = useSWR(`/api/agents/${id}`, fetcher);
  const { data: sessions } = useSWR(`/api/agents/sessions?agent_id=${id}&limit=20`, fetcher);
  const { data: costs } = useSWR(`/api/costs/today`, fetcher);

  if (!agent) return <div className="text-slate-400 p-8">載入中...</div>;

  const agentCost = costs?.by_agent?.find((a: any) => a.agent === id);

  return (
    <div className="space-y-6">
      <Link href="/admin/agents" className="text-sm text-slate-400 hover:text-slate-200">
        ← 返回 Agents
      </Link>

      {/* Header */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-6">
        <div className="flex items-center gap-4 mb-4">
          <span className="text-3xl">{agent.role === "admin" ? "⚙️" : agent.role === "leader" ? "🧠" : "💻"}</span>
          <div>
            <h2 className="text-2xl font-bold">{agent.name}</h2>
            <p className="text-slate-400">{agent.role} · {agent.provider} · {agent.model}</p>
          </div>
          <span className={`ml-auto px-3 py-1 rounded-full text-sm ${agent.status === "idle" ? "bg-green-900 text-green-300" : agent.status === "busy" ? "bg-cyan-900 text-cyan-300" : "bg-red-900 text-red-300"}`}>
            {agent.status}
          </span>
        </div>
        <div className="text-sm text-slate-400">
          Working dir: <code className="text-slate-300">{agent.working_dir}</code>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <div className="text-sm text-slate-400">今日費用</div>
          <div className="text-2xl font-bold text-cyan-400">${agentCost?.cost_usd?.toFixed(4) || "0.0000"}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <div className="text-sm text-slate-400">今日 Tokens</div>
          <div className="text-2xl font-bold">{agentCost?.tokens || 0}</div>
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <div className="text-sm text-slate-400">今日呼叫次數</div>
          <div className="text-2xl font-bold">{agentCost?.calls || 0}</div>
        </div>
      </div>

      {/* Recent Sessions */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
        <h3 className="text-lg font-medium mb-3">最近 Sessions</h3>
        <div className="space-y-2">
          {sessions?.map((s: any) => (
            <div key={s.id} className="flex items-center justify-between py-2 border-b border-slate-800 last:border-0">
              <div className="flex items-center gap-3">
                <span className={`w-2 h-2 rounded-full ${s.status === "completed" ? "bg-green-500" : "bg-red-500"}`} />
                <span className="text-sm text-slate-300 font-mono">{s.id}</span>
                <span className="text-sm text-slate-400 truncate max-w-[300px]">{s.output?.slice(0, 60)}</span>
              </div>
              <div className="text-xs text-slate-500">{s.started_at?.slice(11, 19)}</div>
            </div>
          )) || <p className="text-slate-500 text-sm">無 session 紀錄</p>}
        </div>
      </div>
    </div>
  );
}
