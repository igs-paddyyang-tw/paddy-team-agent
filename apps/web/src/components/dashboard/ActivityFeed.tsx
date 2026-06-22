"use client";

interface WsEvent {
  type: string;
  data: Record<string, unknown>;
  source: string;
  timestamp: string;
}

const typeIcons: Record<string, string> = {
  "agent.output": "💬",
  "task.completed": "✅",
  "task.failed": "❌",
  "task.created": "📋",
  "task.assigned": "🎯",
  "cost.recorded": "💰",
  "budget.warning": "⚠️",
  "system.restart": "🔄",
};

export function ActivityFeed({ events, connected }: { events: WsEvent[]; connected: boolean }) {
  return (
    <div>
      <div className="flex items-center gap-2 mb-3">
        <span className={`w-2 h-2 rounded-full ${connected ? "bg-green-500" : "bg-red-500"}`} />
        <span className="text-xs text-slate-500">{connected ? "Live" : "Disconnected"}</span>
      </div>
      <div className="space-y-2 max-h-64 overflow-y-auto">
        {events.length === 0 && <p className="text-slate-500 text-sm">等待事件...</p>}
        {events.map((e, i) => (
          <div key={i} className="flex items-start gap-2 text-sm">
            <span>{typeIcons[e.type] || "📌"}</span>
            <div className="flex-1 min-w-0">
              <span className="text-slate-300">{e.type}</span>
              <span className="text-slate-500 ml-2 text-xs">{e.timestamp?.slice(11, 19)}</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
