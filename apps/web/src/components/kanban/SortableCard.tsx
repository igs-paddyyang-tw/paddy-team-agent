"use client";
import { useSortable } from "@dnd-kit/sortable";
import { CSS } from "@dnd-kit/utilities";
import { IssueCard } from "./IssueCard";

interface Issue {
  id: string;
  title: string;
  priority: number;
  assignee: string | null;
  status: string;
  created_at: string;
  description?: string;
}

export function SortableCard({ issue }: { issue: Issue }) {
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: issue.id,
    data: { issue },
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
  };

  return (
    <div ref={setNodeRef} style={style} {...attributes} {...listeners}>
      <IssueCard issue={issue} isDragging={isDragging} />
    </div>
  );
}
