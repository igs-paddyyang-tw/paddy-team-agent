"use client";
import useSWR from "swr";
import { fetcher, api } from "@/lib/api";
import { useState } from "react";

export default function SettingsPage() {
  const { data: budget, mutate: refresh } = useSWR("/api/admin/costs/budget", fetcher);
  const [daily, setDaily] = useState("");

  async function saveBudget() {
    if (!daily) return;
    await api.post("/api/admin/costs/budget", { daily_limit_usd: Number(daily) });
    refresh();
    setDaily("");
  }

  return (
    <div className="space-y-6">
      <h2 className="text-2xl font-bold">Settings</h2>

      <div className="bg-slate-900 border border-slate-800 rounded-lg p-6 max-w-md">
        <h3 className="font-medium mb-4">Budget</h3>
        <div className="space-y-3 text-sm">
          <div className="flex justify-between">
            <span className="text-slate-400">Daily Limit</span>
            <span className="text-cyan-400">${budget?.daily_limit_usd}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-400">Alert Threshold</span>
            <span>{budget?.alert_threshold}%</span>
          </div>
          <div className="flex gap-2 mt-4">
            <input
              type="number"
              placeholder="New daily limit"
              value={daily}
              onChange={(e) => setDaily(e.target.value)}
              className="flex-1 px-3 py-1.5 bg-slate-800 border border-slate-700 rounded text-sm"
            />
            <button onClick={saveBudget} className="px-3 py-1.5 bg-cyan-600 hover:bg-cyan-500 rounded text-sm">
              Save
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
