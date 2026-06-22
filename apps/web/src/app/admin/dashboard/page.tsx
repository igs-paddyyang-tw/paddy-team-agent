"use client";
import useSWR from "swr";
import { fetcher } from "@/lib/api";
import { useEventStream } from "@/hooks/useEventStream";
import { KpiCard } from "@/components/dashboard/KpiCard";
import { TrendChart } from "@/components/dashboard/TrendChart";
import { AgentGrid } from "@/components/dashboard/AgentGrid";
import { ActivityFeed } from "@/components/dashboard/ActivityFeed";

export default function DashboardPage() {
  const { data: stats } = useSWR("/api/admin/dashboard/stats", fetcher, { refreshInterval: 30000 });
  const { data: trends } = useSWR("/api/admin/dashboard/trends", fetcher);
  const { data: agents } = useSWR("/api/agents", fetcher);
  const { events, connected } = useEventStream();

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Dashboard</h2>

      {/* KPI Cards */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard label="Active Agents" value={stats?.active_agents ?? "-"} icon="🤖" />
        <KpiCard label="Running Tasks" value={stats?.running_tasks ?? "-"} icon="⚡" color="text-yellow-400" />
        <KpiCard label="Completed Today" value={stats?.completed_today ?? "-"} icon="✅" color="text-green-400" />
        <KpiCard label="Cost Today" value={stats ? `$${stats.total_cost_today_usd.toFixed(2)}` : "-"} icon="💰" color="text-orange-400" />
      </div>

      {/* Chart + Agents */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 bg-slate-900 border border-slate-800 rounded-lg p-4">
          <h3 className="text-sm font-medium text-slate-400 mb-3">Completed (7 days)</h3>
          <TrendChart data={trends?.completed || {}} />
        </div>
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <h3 className="text-sm font-medium text-slate-400 mb-3">Agents</h3>
          <AgentGrid agents={agents || []} />
        </div>
      </div>

      {/* Activity Feed */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
        <h3 className="text-sm font-medium text-slate-400 mb-3">Activity Feed</h3>
        <ActivityFeed events={events} connected={connected} />
      </div>
    </div>
  );
}
