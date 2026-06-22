"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { LayoutDashboard, Bot, MessageSquare, DollarSign, ScrollText, ListTodo, Settings } from "lucide-react";

const NAV = [
  { href: "/admin/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/admin/agents", label: "Agents", icon: Bot },
  { href: "/admin/sessions", label: "Sessions", icon: MessageSquare },
  { href: "/admin/costs", label: "Costs", icon: DollarSign },
  { href: "/admin/audit", label: "Audit", icon: ScrollText },
  { href: "/admin/queue", label: "Queue", icon: ListTodo },
  { href: "/admin/settings", label: "Settings", icon: Settings },
];

export default function AdminLayout({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex h-screen bg-slate-950 text-slate-200">
      {/* Sidebar */}
      <aside className="w-56 border-r border-slate-800 flex flex-col">
        <div className="p-4 border-b border-slate-800">
          <h1 className="text-lg font-bold text-cyan-400">⚡ Ark Platform</h1>
        </div>
        <nav className="flex-1 p-2 space-y-1">
          {NAV.map(({ href, label, icon: Icon }) => (
            <Link
              key={href}
              href={href}
              className={`flex items-center gap-3 px-3 py-2 rounded-md text-sm transition-colors ${
                pathname?.startsWith(href)
                  ? "bg-slate-800 text-cyan-400"
                  : "text-slate-400 hover:text-slate-200 hover:bg-slate-800/50"
              }`}
            >
              <Icon size={18} />
              {label}
            </Link>
          ))}
        </nav>
        <div className="p-3 border-t border-slate-800 text-xs text-slate-500">
          v1.0 • 5 Agents
        </div>
      </aside>

      {/* Main */}
      <main className="flex-1 overflow-auto">
        <header className="h-14 border-b border-slate-800 flex items-center px-6">
          <span className="text-sm text-slate-400">
            {NAV.find(n => pathname?.startsWith(n.href))?.label || "Admin"}
          </span>
        </header>
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
}
