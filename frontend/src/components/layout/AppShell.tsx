"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { Sidebar } from "./Sidebar";
import { Navbar } from "./Navbar";
import { getStoredSession } from "@/lib/api";
import type { Role } from "@/types/role";

export function AppShell({
  role,
  children,
}: {
  role: Role;
  children: React.ReactNode;
}) {
  const router = useRouter();
  const [authorized, setAuthorized] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const [collapsed, setCollapsed] = useState(false);

  useEffect(() => {
    const session = getStoredSession();
    if (!session?.token) {
      router.replace("/login");
      return;
    }

    const sessionRole = session.user?.role?.toLowerCase();
    if (sessionRole !== role) {
      const destination = ["admin", "teacher", "student"].includes(sessionRole)
        ? `/${sessionRole}/dashboard`
        : "/login";
      router.replace(destination);
      return;
    }

    setAuthorized(true);
  }, [role, router]);

  if (!authorized) {
    return (
      <div className="grid min-h-screen place-items-center bg-(--background) text-sm text-slate-500">
        Checking your session...
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-(--background)">
      <Sidebar
        role={role}
        mobileOpen={mobileOpen}
        collapsed={collapsed}
        onClose={() => setMobileOpen(false)}
        onToggleCollapse={() => setCollapsed((current) => !current)}
      />

      <div className={`transition-[padding] duration-200 ${collapsed ? "lg:pl-20" : "lg:pl-67.5"}`}>
        <Navbar
          role={role}
          onMenu={() => setMobileOpen(true)}
        />

        <main className="mx-auto max-w-[1600px] p-4 lg:px-7 lg:py-4">
          {children}
        </main>
      </div>
    </div>
  );
}
