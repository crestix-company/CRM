import Link from "next/link";
import { Icon } from "@/components/ui/icon";
import { BusinessUnitSwitcher } from "./business-unit-switcher";
import { OrganizationSwitcher } from "./organization-switcher";

type HeaderProps = {
  user: { name: string; email: string };
  activeOrganizationId: string;
  memberships: Array<{ organization: { id: string; name: string } }>;
  businessUnits: Array<{ id: string; name: string; slug: string }>;
  selectedBusinessUnitId: string | null;
  canSelectAllBusinessUnits: boolean;
  canCreateInternalAppointment: boolean;
  unreadNotificationCount: number;
};

export function AppHeader({
  user,
  activeOrganizationId,
  memberships,
  businessUnits,
  selectedBusinessUnitId,
  canSelectAllBusinessUnits,
  canCreateInternalAppointment,
  unreadNotificationCount,
}: HeaderProps) {
  const initial =
    user.name.trim().charAt(0) || user.email.charAt(0).toUpperCase();

  return (
    <header className="sticky top-0 z-20 border-b border-line bg-white/90 px-3 py-2 backdrop-blur md:px-8 lg:ml-64">
      <div className="flex min-w-0 items-center justify-between gap-2">
        <div className="flex min-w-0 items-center gap-2 md:gap-3">
          <Link
            href="/dashboard"
            className="grid h-10 w-10 shrink-0 place-items-center rounded-lg bg-ink font-bold text-white lg:hidden"
          >
            S
          </Link>
          <OrganizationSwitcher
            activeOrganizationId={activeOrganizationId}
            memberships={memberships}
          />
          <div className="hidden md:block">
            <BusinessUnitSwitcher
              units={businessUnits}
              selectedBusinessUnitId={selectedBusinessUnitId}
              canSelectAll={canSelectAllBusinessUnits}
            />
          </div>
        </div>
        <div className="flex shrink-0 items-center gap-2 md:gap-3">
          {canCreateInternalAppointment ? (
            <Link
              href="/appointments/new"
              className="primary-button inline-flex whitespace-nowrap px-3 sm:px-4"
            >
              <span className="sm:hidden">＋ アポ</span>
              <span className="hidden sm:inline">＋ アポ登録</span>
            </Link>
          ) : null}
          <Link
            href="/approvals"
            aria-label="承認"
            className="hidden h-10 items-center rounded-lg border border-line bg-white px-3 text-xs font-bold text-slate-600 shadow-sm transition hover:border-brand-200 hover:text-brand-700 sm:inline-flex"
          >
            承認
          </Link>
          <Link
            href="/notifications"
            aria-label="通知"
            className="relative grid h-10 w-10 place-items-center rounded-lg border border-line bg-white text-slate-600 shadow-sm transition hover:border-brand-200 hover:text-brand-700"
          >
            <Icon name="bell" className="h-5 w-5" />
            {unreadNotificationCount ? (
              <span className="absolute -right-1 -top-1 grid min-h-5 min-w-5 place-items-center rounded-full bg-brand-600 px-1 text-[10px] font-bold text-white">
                {unreadNotificationCount > 99 ? "99+" : unreadNotificationCount}
              </span>
            ) : null}
          </Link>
          <div className="hidden text-right sm:block">
            <p className="text-sm font-bold">{user.name}</p>
            <p className="hidden text-xs text-slate-500 xl:block">
              {user.email}
            </p>
          </div>
          <div className="hidden h-10 w-10 place-items-center rounded-full bg-brand-100 text-sm font-bold text-brand-700 sm:grid">
            {initial}
          </div>
          <form action="/api/auth/logout" method="post">
            <button
              aria-label="ログアウト"
              className="grid h-10 w-10 place-items-center rounded-lg border border-line bg-white text-slate-500 hover:border-brand-200 hover:text-ink md:hidden"
              type="submit"
              title="ログアウト"
            >
              <Icon name="logout" className="h-5 w-5" />
            </button>
            <button
              className="hidden text-xs font-bold text-slate-500 hover:text-ink md:inline"
              type="submit"
            >
              ログアウト
            </button>
          </form>
        </div>
      </div>
      <div className="mt-2 md:hidden">
        <BusinessUnitSwitcher
          units={businessUnits}
          selectedBusinessUnitId={selectedBusinessUnitId}
          canSelectAll={canSelectAllBusinessUnits}
        />
      </div>
    </header>
  );
}
