"use client";

interface KpiCardProps {
  label: string;
  value: string | number;
  icon: string;
  color?: string;
}

export function KpiCard({ label, value, icon, color = "text-cyan-400" }: KpiCardProps) {
  return (
    <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-slate-400 text-sm">{label}</span>
        <span className="text-lg">{icon}</span>
      </div>
      <div className={`text-2xl font-bold ${color}`}>{value}</div>
    </div>
  );
}
