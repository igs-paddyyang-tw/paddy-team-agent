"use client";
import { useState } from "react";
import {
  DndContext,
  DragOverlay,
  DragStartEvent,
  DragEndEvent,
  PointerSensor,
  useSensor,
  useSensors,
  closestCorners,
} from "@dnd-kit/core";
import { KanbanColumn } from "./KanbanColumn";
import { IssueCard } from "./IssueCard";
import { AssignModal } from "./AssignModal";

interface Issue {
  id: string;
  title: string;
  priority: number;
  assignee: string | null;
  status: string;
  created_at: string;
  description?: string;
}

interface KanbanBoardProps {
  issues: Issue[];
  agents: { id: string; name: string; role: string }[];
  onStatusChange: (issueId: string, newStatus: string, assignee?: string) => void;
}

const COLUMNS = [
  { id: "pending", title: "Pending", icon: "📋", color: "text-slate-300" },
  { id: "assigned", title: "Assigned", icon: "👤", color: "text-blue-400" },
  { id: "in_progress", title: "In Progress", icon: "⚡", color: "text-yellow-400" },
  { id: "completed", title: "Done", icon: "✅", color: "text-green-400" },
];

// 只允許向右流轉
const ALLOWED_TRANSITIONS: Record<string, string[]> = {
  pending: ["assigned"],
  assigned: ["in_progress"],
  in_progress: ["completed"],
  completed: [],
};

export function KanbanBoard({ issues, agents, onStatusChange }: KanbanBoardProps) {
  const [activeIssue, setActiveIssue] = useState<Issue | null>(null);
  const [assignModal, setAssignModal] = useState<{ issueId: string } | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 8 } })
  );

  function getIssuesByStatus(status: string) {
    if (status === "completed") {
      // Done 欄只顯示最近 7 天（用 created_at 排序即可，篩選由外層處理）
      return issues
        .filter(i => i.status === status)
        .sort((a, b) => b.created_at.localeCompare(a.created_at))
        .slice(0, 30);
    }
    return issues
      .filter(i => i.status === status)
      .sort((a, b) => a.priority - b.priority);
  }

  function handleDragStart(event: DragStartEvent) {
    const issue = issues.find(i => i.id === event.active.id);
    setActiveIssue(issue || null);
  }

  function handleDragEnd(event: DragEndEvent) {
    setActiveIssue(null);
    const { active, over } = event;
    if (!over) return;

    const issueId = active.id as string;
    const issue = issues.find(i => i.id === issueId);
    if (!issue) return;

    // Determine target column
    let targetColumn = over.id as string;
    // If dropped on a card, find its column
    if (!COLUMNS.find(c => c.id === targetColumn)) {
      const targetIssue = issues.find(i => i.id === targetColumn);
      if (targetIssue) targetColumn = targetIssue.status;
    }

    // Same column → no-op
    if (targetColumn === issue.status) return;

    // Check allowed transition (only forward)
    const allowed = ALLOWED_TRANSITIONS[issue.status] || [];
    if (!allowed.includes(targetColumn)) return;

    // If moving to "assigned" → show agent picker
    if (targetColumn === "assigned") {
      setAssignModal({ issueId });
      return;
    }

    onStatusChange(issueId, targetColumn);
  }

  function handleAssign(agentId: string) {
    if (assignModal) {
      onStatusChange(assignModal.issueId, "assigned", agentId);
      setAssignModal(null);
    }
  }

  return (
    <>
      <DndContext
        sensors={sensors}
        collisionDetection={closestCorners}
        onDragStart={handleDragStart}
        onDragEnd={handleDragEnd}
      >
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
          {COLUMNS.map(col => (
            <KanbanColumn
              key={col.id}
              id={col.id}
              title={col.title}
              icon={col.icon}
              color={col.color}
              issues={getIssuesByStatus(col.id)}
            />
          ))}
        </div>

        <DragOverlay>
          {activeIssue && <IssueCard issue={activeIssue} isDragging />}
        </DragOverlay>
      </DndContext>

      {assignModal && (
        <AssignModal
          agents={agents}
          onAssign={handleAssign}
          onClose={() => setAssignModal(null)}
        />
      )}
    </>
  );
}
