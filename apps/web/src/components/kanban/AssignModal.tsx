"use client";

interface Agent {
  id: string;
  name: string;
  role: string;
}

interface AssignModalProps {
  agents: Agent[];
  onAssign: (agentId: string) => void;
  onClose: () => void;
}

const roleIcons: Record<string, string> = {
  admin: "👑",
  leader: "🧠",
  worker: "💻",
};

export function AssignModal({ agents, onAssign, onClose }: AssignModalProps) {
  // Only show workers (and leader) as assignable
  const assignable = agents.filter(a => a.role === "worker" || a.role === "leader");

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={onClose}>
      <div
        className="bg-slate-900 border border-slate-700 rounded-lg p-4 w-80 shadow-xl"
        onClick={e => e.stopPropagation()}
      >
        <h3 className="text-sm font-semibold text-slate-200 mb-3">指派給哪個 Agent？</h3>
        <div className="space-y-2">
          {assignable.map(agent => (
            <button
              key={agent.id}
              onClick={() => onAssign(agent.id)}
              className="w-full flex items-center gap-3 px-3 py-2 rounded-md bg-slate-800 hover:bg-slate-700 border border-slate-700 hover:border-cyan-600 transition-colors text-left"
            >
              <span>{roleIcons[agent.role] || "🤖"}</span>
              <div>
                <div className="text-sm text-slate-200">{agent.name}</div>
                <div className="text-xs text-slate-500">{agent.role}</div>
              </div>
            </button>
          ))}
        </div>
        <button
          onClick={onClose}
          className="mt-3 w-full text-xs text-slate-500 hover:text-slate-300 py-1"
        >
          取消
        </button>
      </div>
    </div>
  );
}
