"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";
import {
  BookOpenCheck,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { Icon } from "@/components/ui";
import { navigation } from "@/lib/navigation";
import type { Role } from "@/types/role";

export function Sidebar({
  role,
  mobileOpen = false,
  collapsed = false,
  onClose,
  onToggleCollapse,
}: {
  role: Role;
  mobileOpen?: boolean;
  collapsed?: boolean;
  onClose?: () => void;
  onToggleCollapse?: () => void;
}) {
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    navigation[role].forEach((item) => {
      router.prefetch(item.href);
    });
    router.prefetch(`/${role}/profile`);
  }, [role, router]);

  const panel = (mobile = false) => (
    <aside
      className={`flex h-full flex-col border-r border-(--border) bg-white py-5 transition-[width] duration-200 ${
        mobile ? "w-[270px] px-4" : collapsed ? "w-20 px-3" : "w-[270px] px-4"
      }`}
    >
      <div className={`mb-5 flex items-center ${collapsed && !mobile ? "justify-center" : "justify-between"}`}>
        <Link
          href={`/${role}/dashboard`}
          prefetch
          onClick={mobile ? onClose : undefined}
          className={`flex items-center gap-3 ${collapsed && !mobile ? "px-0" : "px-3"}`}
          aria-label="LearnSphere dashboard"
        >
          <span className="grid h-11 w-11 shrink-0 place-items-center rounded-2xl bg-(--brand) text-white shadow-lg shadow-indigo-200">
            <BookOpenCheck size={22} />
          </span>

          {(!collapsed || mobile) && (
            <div>
              <div className="text-lg font-bold tracking-tight">LearnSphere</div>
              <div className="text-xs text-(--muted)">Learning Management</div>
            </div>
          )}
        </Link>

        {mobile && (
          <button
            type="button"
            onClick={onClose}
            className="icon-button"
            aria-label="Close navigation"
          >
            <ChevronLeft size={19} />
          </button>
        )}
      </div>

      {!mobile && (
        <button
          type="button"
          onClick={onToggleCollapse}
          className={`mb-4 flex items-center rounded-xl py-2 text-xs font-semibold text-slate-500 transition hover:bg-slate-50 hover:text-slate-900 ${
            collapsed ? "justify-center px-2" : "gap-2 px-3"
          }`}
          aria-label="Toggle sidebar"
        >
          {collapsed ? <ChevronRight size={17} /> : <ChevronLeft size={17} />}
        </button>
      )}

      <nav className="soft-scrollbar flex-1 space-y-1 overflow-y-auto pr-1">
        {(!collapsed || mobile) && (
          <div className="mb-2 px-3 text-[11px] font-bold uppercase tracking-[0.18em] text-slate-400">
            Workspace
          </div>
        )}

        {navigation[role].map((item) => {
          const active = pathname === item.href || pathname.startsWith(`${item.href}/`);

          return (
            <Link
              key={item.href}
              href={item.href}
              prefetch
              onClick={mobile ? onClose : undefined}
              title={collapsed && !mobile ? item.label : undefined}
              className={`flex items-center rounded-xl py-2.5 text-sm font-medium transition ${
                collapsed && !mobile ? "justify-center px-2" : "gap-3 px-3"
              } ${
                active
                  ? "bg-(--brand-soft) text-(--brand)"
                  : "text-slate-600 hover:bg-slate-50 hover:text-slate-950"
              }`}
            >
              <Icon
                name={item.icon}
                size={18}
                strokeWidth={active ? 2.5 : 2}
              />

              {(!collapsed || mobile) && <span>{item.label}</span>}
            </Link>
          );
        })}
      </nav>
    </aside>
  );

  return (
    <>
      <div className="fixed inset-y-0 left-0 z-30 hidden lg:block">
        {panel(false)}
      </div>

      {mobileOpen && (
        <div className="fixed inset-0 z-50 lg:hidden">
          <button
            type="button"
            onClick={onClose}
            className="absolute inset-0 bg-slate-950/35 backdrop-blur-[2px]"
            aria-label="Close navigation"
          />

          <div className="relative h-full w-[270px] shadow-2xl">
            {panel(true)}
          </div>
        </div>
      )}
    </>
  );
}
