"use client";
import useSWR, { mutate } from "swr";
import { fetcher, api } from "@/lib/api";

const priorityLabel: Record<number, { icon: string; color: string }> = {
  1: { icon: "🔴", color: "text-red-400" },
  2: { icon: "🟠", color: "text-orange-400" },
  3: { icon: "🔵", color: "text-blue-400" },
  4: { icon: "⚪", color: "text-slate-400" },
};

export default function QueuePage() {
  const { data: queue } = useSWR("/api/admin/queue", fetcher, { refreshInterval: 5000 });

  async function setPriority(id: string, priority: number) {
    await api.patch(`/api/admin/queue/${id}/priority?priority=${priority}`, {});
    mutate("/api/admin/queue");
  }

  return (
    <div className="space-y-4">
      <h2 className="text-2xl font-bold">Queue</h2>
      <p className="text-slate-400 text-sm">{queue?.length || 0} pending items</p>

      <div className="bg-slate-900 border border-slate-800 rounded-lg overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-800/50">
            <tr className="text-left text-slate-400">
              <th className="px-4 py-3">Priority</th>
              <th className="px-4 py-3">Title</th>
              <th className="px-4 py-3">Assignee</th>
              <th className="px-4 py-3">Actions</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-800">
            {(!queue || queue.length === 0) && (
              <tr><td colSpan={4} className="px-4 py-8 text-center text-slate-500">佇列為空 ✨</td></tr>
            )}
            {queue?.map((item: any) => {
              const p = priorityLabel[item.priority] || priorityLabel[3];
              return (
                <tr key={item.id} className="hover:bg-slate-800/30">
                  <td className="px-4 py-3">
                    <span className={p.color}>{p.icon} P{item.priority}</span>
                  </td>
                  <td className="px-4 py-3 text-slate-200">{item.title}</td>
                  <td className="px-4 py-3 text-slate-400">{item.assignee || "—"}</td>
                  <td className="px-4 py-3">
                    <select
                      className="bg-slate-800 border border-slate-700 rounded px-2 py-1 text-xs"
                      value={item.priority}
                      onChange={(e) => setPriority(item.id, Number(e.target.value))}
                    >
                      <option value={1}>P1 Urgent</option>
                      <option value={2}>P2 High</option>
                      <option value={3}>P3 Normal</option>
                      <option value={4}>P4 Low</option>
                    </select>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>
    </div>
  );
}
