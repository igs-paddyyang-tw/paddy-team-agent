"use client";

interface IssueCardProps {
  issue: {
    id: string;
    title: string;
    priority: number;
    assignee: string | null;
    status: string;
    created_at: string;
    description?: string;
  };
  isDragging?: boolean;
}

const priorityConfig: Record<number, { icon: string; color: string; label: string }> = {
  1: { icon: "🔴", color: "border-l-red-500", label: "P1" },
  2: { icon: "🟠", color: "border-l-orange-500", label: "P2" },
  3: { icon: "🔵", color: "border-l-blue-500", label: "P3" },
  4: { icon: "⚪", color: "border-l-slate-500", label: "P4" },
};

function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const mins = Math.floor(diff / 60000);
  if (mins < 60) return `${mins}m ago`;
  const hours = Math.floor(mins / 60);
  if (hours < 24) return `${hours}h ago`;
  const days = Math.floor(hours / 24);
  return `${days}d ago`;
}

export function IssueCard({ issue, isDragging }: IssueCardProps) {
  const p = priorityConfig[issue.priority] || priorityConfig[3];
  const isFailed = issue.status === "pending" && issue.description?.includes("❌");

  return (
    <div
      className={`
        bg-slate-800 border border-slate-700 border-l-4 ${p.color}
        rounded-md p-3 cursor-grab active:cursor-grabbing
        transition-all duration-150
        ${isDragging ? "opacity-50 scale-95 shadow-2xl" : "hover:border-slate-600"}
        ${isFailed ? "ring-1 ring-red-500/50" : ""}
      `}
    >
      {/* Header */}
      <div className="flex items-center justify-between mb-1">
        <span className="text-xs text-slate-500 font-mono">{issue.id}</span>
        <span className="text-xs">{p.icon} {p.label}</span>
      </div>

      {/* Title */}
      <h4 className="text-sm font-medium text-slate-200 mb-2 line-clamp-2">
        {isFailed && <span className="text-red-400 mr-1">❌</span>}
        {issue.title}
      </h4>

      {/* Footer */}
      <div className="flex items-center justify-between text-xs text-slate-500">
        <span>
          {issue.assignee ? `👤 ${issue.assignee.replace("-agent", "")}` : "—"}
        </span>
        <span>⏱ {timeAgo(issue.created_at)}</span>
      </div>
    </div>
  );
}
