"use client";
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from "recharts";

interface TrendChartProps {
  data: Record<string, number>;
}

export function TrendChart({ data }: TrendChartProps) {
  const chartData = Object.entries(data).map(([date, count]) => ({
    date: date.slice(5), // MM-DD
    completed: count,
  }));

  if (!chartData.length) {
    return <div className="h-64 flex items-center justify-center text-slate-500">尚無資料</div>;
  }

  return (
    <div className="h-64">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
          <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
          <YAxis stroke="#94a3b8" fontSize={12} />
          <Tooltip contentStyle={{ background: "#1e293b", border: "1px solid #334155" }} />
          <Line type="monotone" dataKey="completed" stroke="#22d3ee" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
