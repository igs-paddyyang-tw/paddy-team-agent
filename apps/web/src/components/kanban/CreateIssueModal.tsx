"use client";
import { useState } from "react";
import { api } from "@/lib/api";

interface CreateIssueModalProps {
  agents: { id: string; name: string; role: string }[];
  onCreated: () => void;
  onClose: () => void;
}

export function CreateIssueModal({ agents, onCreated, onClose }: CreateIssueModalProps) {
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [priority, setPriority] = useState(3);
  const [assignee, setAssignee] = useState<string>("");
  const [loading, setLoading] = useState(false);

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!title.trim()) return;
    setLoading(true);
    try {
      await api.post("/api/issues", {
        title: title.trim(),
        description,
        priority,
        assignee: assignee || null,
      });
      onCreated();
      onClose();
    } catch (err) {
      console.error("Failed to create issue:", err);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60" onClick={onClose}>
      <div
        className="bg-slate-900 border border-slate-700 rounded-lg p-5 w-96 shadow-xl"
        onClick={e => e.stopPropagation()}
      >
        <h3 className="text-lg font-semibold text-slate-200 mb-4">建立新任務</h3>
        <form onSubmit={handleSubmit} className="space-y-3">
          {/* Title */}
          <div>
            <label className="text-xs text-slate-400 block mb-1">標題 *</label>
            <input
              type="text"
              value={title}
              onChange={e => setTitle(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-slate-200 focus:border-cyan-600 focus:outline-none"
              placeholder="任務標題..."
              autoFocus
            />
          </div>

          {/* Description */}
          <div>
            <label className="text-xs text-slate-400 block mb-1">描述</label>
            <textarea
              value={description}
              onChange={e => setDescription(e.target.value)}
              className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-slate-200 focus:border-cyan-600 focus:outline-none h-20 resize-none"
              placeholder="任務描述..."
            />
          </div>

          {/* Priority + Assignee */}
          <div className="grid grid-cols-2 gap-3">
            <div>
              <label className="text-xs text-slate-400 block mb-1">優先級</label>
              <select
                value={priority}
                onChange={e => setPriority(Number(e.target.value))}
                className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-slate-200"
              >
                <option value={1}>🔴 P1 Urgent</option>
                <option value={2}>🟠 P2 High</option>
                <option value={3}>🔵 P3 Normal</option>
                <option value={4}>⚪ P4 Low</option>
              </select>
            </div>
            <div>
              <label className="text-xs text-slate-400 block mb-1">指派</label>
              <select
                value={assignee}
                onChange={e => setAssignee(e.target.value)}
                className="w-full bg-slate-800 border border-slate-700 rounded px-3 py-2 text-sm text-slate-200"
              >
                <option value="">（稍後指派）</option>
                {agents
                  .filter(a => a.role === "worker" || a.role === "leader")
                  .map(a => (
                    <option key={a.id} value={a.id}>{a.name}</option>
                  ))}
              </select>
            </div>
          </div>

          {/* Actions */}
          <div className="flex gap-2 pt-2">
            <button
              type="submit"
              disabled={!title.trim() || loading}
              className="flex-1 bg-cyan-600 hover:bg-cyan-700 disabled:opacity-50 text-white text-sm font-medium py-2 rounded transition-colors"
            >
              {loading ? "建立中..." : "建立"}
            </button>
            <button
              type="button"
              onClick={onClose}
              className="px-4 text-sm text-slate-400 hover:text-slate-200 py-2"
            >
              取消
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
