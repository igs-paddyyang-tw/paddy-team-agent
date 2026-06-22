"use client";

interface Turn {
  id: string;
  idx: number;
  role: string;
  content: string;
  tool_calls: string;
  tokens: number;
  timestamp: string;
}

export function ConversationView({ turns }: { turns: Turn[] }) {
  if (!turns?.length) {
    return <p className="text-slate-500">尚無對話記錄</p>;
  }

  return (
    <div className="space-y-3">
      {turns.map((t) => (
        <div key={t.id || t.idx} className={`flex ${t.role === "user" ? "justify-end" : "justify-start"}`}>
          <div
            className={`max-w-[80%] rounded-lg px-4 py-2 text-sm ${
              t.role === "user"
                ? "bg-cyan-900/40 border border-cyan-800"
                : t.role === "tool"
                ? "bg-yellow-900/20 border border-yellow-800/50"
                : "bg-slate-800 border border-slate-700"
            }`}
          >
            <div className="flex items-center gap-2 mb-1">
              <span className="text-xs font-medium text-slate-400">{t.role}</span>
              <span className="text-xs text-slate-600">{t.tokens} tok</span>
            </div>
            <p className="text-slate-200 whitespace-pre-wrap break-words">{t.content?.slice(0, 2000)}</p>
            {t.tool_calls && t.tool_calls !== "[]" && (
              <ToolCallPanel toolCalls={t.tool_calls} />
            )}
          </div>
        </div>
      ))}
    </div>
  );
}

function ToolCallPanel({ toolCalls }: { toolCalls: string }) {
  let calls: any[] = [];
  try { calls = JSON.parse(toolCalls); } catch { return null; }
  if (!calls.length) return null;

  return (
    <div className="mt-2 space-y-1">
      {calls.map((c: any, i: number) => (
        <details key={i} className="bg-slate-900/50 rounded p-2 text-xs">
          <summary className="cursor-pointer text-yellow-400">
            🔧 {c.name} {c.duration_ms ? `(${c.duration_ms}ms)` : ""}
          </summary>
          <div className="mt-1 space-y-1">
            <div className="text-slate-400">Input: <code className="text-slate-300">{JSON.stringify(c.input)?.slice(0, 200)}</code></div>
            <div className="text-slate-400">Output: <code className="text-slate-300">{String(c.output)?.slice(0, 200)}</code></div>
          </div>
        </details>
      ))}
    </div>
  );
}
