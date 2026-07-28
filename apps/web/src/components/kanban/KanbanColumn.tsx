"use client";
import { useDroppable } from "@dnd-kit/core";
import { SortableContext, verticalListSortingStrategy } from "@dnd-kit/sortable";
import { SortableCard } from "./SortableCard";

interface Issue {
  id: string;
  title: string;
  priority: number;
  assignee: string | null;
  status: string;
  created_at: string;
  description?: string;
}

interface KanbanColumnProps {
  id: string;
  title: string;
  icon: string;
  issues: Issue[];
  color: string;
}

export function KanbanColumn({ id, title, icon, issues, color }: KanbanColumnProps) {
  const { setNodeRef, isOver } = useDroppable({ id });

  return (
    <div
      ref={setNodeRef}
      className={`
        flex flex-col min-h-[500px] bg-slate-900/50 border border-slate-800 rounded-lg
        ${isOver ? "ring-2 ring-cyan-500/50 bg-slate-900" : ""}
        transition-all duration-200
      `}
    >
      {/* Column Header */}
      <div className={`px-3 py-2 border-b border-slate-800 flex items-center justify-between`}>
        <div className="flex items-center gap-2">
          <span>{icon}</span>
          <h3 className={`text-sm font-semibold ${color}`}>{title}</h3>
        </div>
        <span className="text-xs text-slate-500 bg-slate-800 px-2 py-0.5 rounded-full">
          {issues.length}
        </span>
      </div>

      {/* Cards */}
      <div className="flex-1 p-2 space-y-2 overflow-y-auto max-h-[calc(100vh-220px)]">
        <SortableContext items={issues.map(i => i.id)} strategy={verticalListSortingStrategy}>
          {issues.map(issue => (
            <SortableCard key={issue.id} issue={issue} />
          ))}
        </SortableContext>
        {issues.length === 0 && (
          <p className="text-center text-slate-600 text-xs py-8">無任務</p>
        )}
      </div>
    </div>
  );
}
