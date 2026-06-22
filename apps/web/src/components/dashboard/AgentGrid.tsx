"use client";

interface Agent {
  id: string;
  name: string;
  role: string;
  status: string;
}

export function AgentGrid({ agents }: { agents: Agent[] }) {
  const statusColor: Record<string, string> = {
    idle: "bg-green-500",
    busy: "bg-cyan-500",
    executing: "bg-cyan-500",
    offline: "bg-red-500",
  };

  return (
    <div className="grid grid-cols-2 gap-2">
      {agents.map((a) => (
        <div key={a.id} className="bg-slate-900 border border-slate-800 rounded p-3 flex items-center gap-3">
          <span className={`w-2.5 h-2.5 rounded-full ${statusColor[a.status] || "bg-gray-500"}`} />
          <div>
            <div className="text-sm font-medium">{a.name}</div>
            <div className="text-xs text-slate-500">{a.role}</div>
          </div>
        </div>
      ))}
    </div>
  );
}
