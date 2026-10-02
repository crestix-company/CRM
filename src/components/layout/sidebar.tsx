"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Icon } from "@/components/ui/icon";

const primaryNavigation = [
  { href: "/dashboard", label: "ダッシュボード", icon: "dashboard" },
  {
    href: "/appointments/new",
    label: "IS連携フォーム",
    icon: "forms",
    requiresAppointmentAccess: true,
  },
  {
    href: "/companies",
    label: "会社",
    icon: "contacts",
    activePrefixes: ["/companies"],
  },
  { href: "/deals", label: "商談", icon: "deals" },
  {
    href: "/delivery-projects",
    label: "CS案件",
    icon: "tasks",
    activePrefixes: ["/delivery-projects"],
  },
  { href: "/tasks", label: "タスク", icon: "tasks" },
  { href: "/approvals", label: "承認", icon: "tasks" },
] as const;

const managementNavigation = [
  { href: "/imports", label: "インポート", icon: "import" },
  { href: "/settings", label: "設定", icon: "settings" },
] as const;

export function Sidebar({
  canCreateInternalAppointment,
  canManage,
}: {
  canCreateInternalAppointment: boolean;
  canManage: boolean;
}) {
  const pathname = usePathname();

  return (
    <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 border-r border-white/10 bg-ink text-white lg:flex lg:flex-col">
      <div className="flex h-16 items-center gap-3 border-b border-white/10 px-5 text-base font-bold">
        <span className="grid h-9 w-9 place-items-center rounded-lg bg-brand-600 shadow-sm">
          S
        </span>
        Crestix AIOS
      </div>
      <nav className="flex-1 px-3 py-5">
        <div className="space-y-1">
        {primaryNavigation
          .filter(
            (item) =>
              !("requiresAppointmentAccess" in item) ||
              !item.requiresAppointmentAccess ||
              canCreateInternalAppointment,
          )
          .map((item) => {
            const prefixes =
              "activePrefixes" in item ? item.activePrefixes : [item.href];
            const active = prefixes.some(
              (prefix) =>
                pathname === prefix || pathname.startsWith(`${prefix}/`),
            );
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition ${
                  active
                    ? "bg-white/10 text-white shadow-sm ring-1 ring-white/10"
                    : "text-white/60 hover:bg-white/10 hover:text-white"
                }`}
              >
                <Icon
                  name={item.icon}
                  className={`h-[18px] w-[18px] ${active ? "text-brand-500" : ""}`}
                />
                {item.label}
              </Link>
            );
          })}
        </div>
        {canManage ? (
          <div className="mt-7 border-t border-white/10 pt-5">
            <p className="mb-2 px-3 text-[11px] font-semibold text-white/35">
              管理
            </p>
            <div className="space-y-1">
              {managementNavigation.map((item) => {
                const active =
                  pathname === item.href || pathname.startsWith(`${item.href}/`);
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-3 rounded-lg px-3 py-2.5 text-sm font-semibold transition ${
                      active
                        ? "bg-white/10 text-white ring-1 ring-white/10"
                        : "text-white/60 hover:bg-white/10 hover:text-white"
                    }`}
                  >
                    <Icon
                      name={item.icon}
                      className={`h-[18px] w-[18px] ${active ? "text-brand-500" : ""}`}
                    />
                    {item.label}
                  </Link>
                );
              })}
            </div>
          </div>
        ) : null}
      </nav>
      <div className="m-4 rounded-lg border border-white/10 bg-white/[0.04] p-4">
        <p className="text-xs font-bold text-brand-500">SALESNEST CORE</p>
        <p className="mt-2 text-sm leading-6 text-white/60">
          今日の実行・承認・顧客・案件を一つの業務体験で管理します。
        </p>
      </div>
    </aside>
  );
}
