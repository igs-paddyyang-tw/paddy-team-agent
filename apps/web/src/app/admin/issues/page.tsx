"use client";
import { useState, useCallback, useEffect } from "react";
import useSWR, { mutate } from "swr";
import { fetcher, api } from "@/lib/api";
import { useEventStream } from "@/hooks/useEventStream";
import { KanbanBoard } from "@/components/kanban/KanbanBoard";
import { CreateIssueModal } from "@/components/kanban/CreateIssueModal";

export default function IssuesPage() {
  const { data: issues, mutate: mutateIssues } = useSWR("/api/issues", fetcher, { refreshInterval: 30000 });
  const { data: agents } = useSWR("/api/agents", fetcher);
  const { events, connected } = useEventStream();
  const [showCreate, setShowCreate] = useState(false);
  const [agentFilter, setAgentFilter] = useState<string>("");

  // WS 即時更新：收到 TASK_* 事件時 revalidate
  useEffect(() => {
    if (events.length > 0) {
      const last = events[events.length - 1];
      if (last?.type?.startsWith("task.")) {
        mutateIssues();
      }
    }
  }, [events, mutateIssues]);

  const handleStatusChange = useCallback(async (issueId: string, newStatus: string, assignee?: string) => {
    try {
      if (newStatus === "assigned" && assignee) {
        await api.patch(`/api/issues/${issueId}/assign`, { assignee });
      } else {
        await api.patch(`/api/issues/${issueId}/status`, { status: newStatus });
      }
      mutateIssues();
    } catch (err) {
      console.error("Status change failed:", err);
    }
  }, [mutateIssues]);

  // 篩選
  const allIssues = issues || [];
  // Done 欄只保留最近 7 天
  const sevenDaysMs = 7 * 24 * 60 * 60 * 1000;
  const filteredIssues = allIssues.filter((i: any) => {
    if (agentFilter && i.assignee !== agentFilter) return false;
    if (i.status === "completed") {
      const age = new Date().getTime() - new Date(i.created_at).getTime();
      if (age > sevenDaysMs) return false;
    }
    return true;
  });

  // 取得可篩選的 agents
  const agentList = agents || [];

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-4">
          <h2 className="text-2xl font-bold">Issues</h2>
          <span className="text-sm text-slate-500">{filteredIssues.length} 個任務</span>
        </div>
        <div className="flex items-center gap-3">
          {/* Agent Filter */}
          <select
            value={agentFilter}
            onChange={e => setAgentFilter(e.target.value)}
            className="bg-slate-800 border border-slate-700 rounded px-3 py-1.5 text-sm text-slate-300"
          >
            <option value="">全部 Agent</option>
            {agentList.map((a: any) => (
              <option key={a.id} value={a.id}>{a.name}</option>
            ))}
          </select>

          {/* Create Button */}
          <button
            onClick={() => setShowCreate(true)}
            className="bg-cyan-600 hover:bg-cyan-700 text-white text-sm font-medium px-4 py-1.5 rounded transition-colors"
          >
            + 新增任務
          </button>
        </div>
      </div>

      {/* Connection Status */}
      {!connected && (
        <div className="bg-yellow-900/30 border border-yellow-700 text-yellow-300 text-xs px-3 py-2 rounded">
          ⚠️ WebSocket 連線中斷，資料可能不是最新。自動重連中...
        </div>
      )}

      {/* Kanban Board */}
      <KanbanBoard
        issues={filteredIssues}
        agents={agentList}
        onStatusChange={handleStatusChange}
      />

      {/* Create Modal */}
      {showCreate && (
        <CreateIssueModal
          agents={agentList}
          onCreated={() => mutateIssues()}
          onClose={() => setShowCreate(false)}
        />
      )}
    </div>
  );
}
