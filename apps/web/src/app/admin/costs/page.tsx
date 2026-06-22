"use client";
import useSWR from "swr";
import { fetcher } from "@/lib/api";
import { BarChart, Bar, PieChart, Pie, Cell, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";

const COLORS = ["#22d3ee", "#f59e0b", "#22c55e", "#ef4444", "#a78bfa"];

export default function CostsPage() {
  const { data } = useSWR("/api/admin/costs", fetcher);
  const { data: budget } = useSWR("/api/admin/costs/budget", fetcher);

  const byAgent = Object.entries(data?.by_agent || {}).map(([name, cost]) => ({ name: name.slice(0, 12), cost }));
  const byModel = Object.entries(data?.by_model || {}).map(([name, cost]) => ({ name, value: cost as number }));

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Costs</h2>

      {/* Overview */}
      <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
        <Card label="Total" value={`$${data?.total_usd?.toFixed(4) || "0"}`} />
        <Card label="Records" value={data?.total_records || 0} />
        <Card label="Daily Limit" value={`$${budget?.daily_limit_usd || 30}`} />
        <Card label="Alert At" value={`${budget?.alert_threshold || 80}%`} />
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* By Agent Bar */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <h3 className="text-sm text-slate-400 mb-3">By Agent</h3>
          <div className="h-48">
            {byAgent.length ? (
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={byAgent} layout="vertical">
                  <XAxis type="number" stroke="#94a3b8" fontSize={11} />
                  <YAxis type="category" dataKey="name" stroke="#94a3b8" fontSize={11} width={90} />
                  <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155" }} />
                  <Bar dataKey="cost" fill="#22d3ee" radius={[0, 4, 4, 0]} />
                </BarChart>
              </ResponsiveContainer>
            ) : <Empty />}
          </div>
        </div>

        {/* By Model Pie */}
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <h3 className="text-sm text-slate-400 mb-3">By Model</h3>
          <div className="h-48">
            {byModel.length ? (
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={byModel} dataKey="value" nameKey="name" cx="50%" cy="50%" outerRadius={70} label={({ name }) => name}>
                    {byModel.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                  </Pie>
                  <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155" }} />
                </PieChart>
              </ResponsiveContainer>
            ) : <Empty />}
          </div>
        </div>
      </div>
    </div>
  );
}

function Card({ label, value }: { label: string; value: string | number }) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
      <div className="text-sm text-slate-400">{label}</div>
      <div className="text-xl font-bold text-cyan-400 mt-1">{value}</div>
    </div>
  );
}

function Empty() {
  return <div className="h-full flex items-center justify-center text-slate-500 text-sm">尚無資料</div>;
}
