"use client";
import { useParams } from "next/navigation";
import useSWR from "swr";
import { fetcher } from "@/lib/api";
import { ConversationView } from "@/components/sessions/ConversationView";

export default function SessionDetailPage() {
  const params = useParams();
  const id = params?.id as string;
  const { data: session } = useSWR(id ? `/api/admin/sessions/${id}` : null, fetcher);

  if (!session) {
    return <div className="text-slate-500">載入中...</div>;
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Session #{id?.slice(0, 8)}</h2>
          <p className="text-slate-400 text-sm mt-1">Agent: {session.agent_id}</p>
        </div>
        <div className="flex items-center gap-4">
          <StatusBadge status={session.status} />
          <TokenMeter tokens={session.total_tokens} />
          <span className="text-orange-400 text-sm">${session.cost_usd?.toFixed(4)}</span>
        </div>
      </div>

      {/* Output summary */}
      {session.output && (
        <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
          <h3 className="text-sm font-medium text-slate-400 mb-2">Output</h3>
          <pre className="text-sm text-slate-300 whitespace-pre-wrap">{session.output}</pre>
        </div>
      )}

      {/* Conversation (if turns available) */}
      <div className="bg-slate-900 border border-slate-800 rounded-lg p-4">
        <h3 className="text-sm font-medium text-slate-400 mb-3">對話回放</h3>
        <ConversationView turns={session.turns || []} />
      </div>
    </div>
  );
}

function StatusBadge({ status }: { status: string }) {
  const colors: Record<string, string> = {
    completed: "bg-green-900/50 text-green-400 border-green-800",
    running: "bg-cyan-900/50 text-cyan-400 border-cyan-800",
    failed: "bg-red-900/50 text-red-400 border-red-800",
  };
  return (
    <span className={`px-2 py-0.5 rounded text-xs border ${colors[status] || "border-slate-700"}`}>
      {status}
    </span>
  );
}

function TokenMeter({ tokens }: { tokens: number }) {
  const pct = Math.min((tokens || 0) / 100000 * 100, 100);
  return (
    <div className="w-24">
      <div className="text-xs text-slate-500 mb-0.5">{tokens?.toLocaleString()} tok</div>
      <div className="h-1.5 bg-slate-800 rounded-full overflow-hidden">
        <div className="h-full bg-cyan-500 rounded-full" style={{ width: `${pct}%` }} />
      </div>
    </div>
  );
}
