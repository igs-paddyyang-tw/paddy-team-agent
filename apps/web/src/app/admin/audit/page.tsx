"use client";
import { useState } from "react";
import useSWR from "swr";
import { fetcher } from "@/lib/api";

export default function AuditPage() {
  const [actor, setActor] = useState("");
  const [action, setAction] = useState("");
  const params = new URLSearchParams();
  if (actor) params.set("actor", actor);
  if (action) params.set("action", action);

  const { data } = useSWR(`/api/admin/audit?${params.toString()}&limit=200`, fetcher, { refreshInterval: 10000 });

  const actorColors: Record<string, string> = {
    human: "bg-blue-900/50 text-blue-400",
    agent: "bg-green-900/50 text-green-400",
    system: "bg-slate-700/50 text-slate-400",
  };

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Audit Log</h2>

      {/* Filters */}
      <div className="flex gap-3">
        <input
          placeholder="Filter actor..."
          value={actor}
          onChange={(e) => setActor(e.target.value)}
          className="px-3 py-1.5 bg-slate-800 border border-slate-700 rounded text-sm text-slate-200 w-40"
        />
        <input
          placeholder="Filter action..."
          value={action}
          onChange={(e) => setAction(e.target.value)}
          className="px-3 py-1.5 bg-slate-800 border border-slate-700 rounded text-sm text-slate-200 w-40"
        />
        <span className="text-sm text-slate-500 self-center">{data?.total || 0} events</span>
      </div>

      {/* Table */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
        <div className="max-h-[600px] overflow-y-auto">
          <table className="w-full text-sm">
            <thead className="bg-slate-800/50 sticky top-0">
              <tr className="text-left text-slate-400">
                <th className="px-4 py-2">Time</th>
                <th className="px-4 py-2">Actor</th>
                <th className="px-4 py-2">Action</th>
                <th className="px-4 py-2">Resource</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800">
              {(!data?.events || data.events.length === 0) && (
                <tr><td colSpan={4} className="px-4 py-8 text-center text-slate-500">尚無事件</td></tr>
              )}
              {data?.events?.map((e: any) => (
                <tr key={e.id} className="hover:bg-slate-800/30">
                  <td className="px-4 py-2 text-slate-500 text-xs whitespace-nowrap">{e.timestamp?.slice(11, 19)}</td>
                  <td className="px-4 py-2">
                    <span className={`px-1.5 py-0.5 rounded text-xs ${actorColors[e.actor_type] || ""}`}>
                      {e.actor_name || e.actor_type}
                    </span>
                  </td>
                  <td className="px-4 py-2 text-slate-300">{e.action}</td>
                  <td className="px-4 py-2 text-slate-500 text-xs">{e.resource_name || e.resource_id?.slice(0, 8)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
