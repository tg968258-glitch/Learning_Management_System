"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import {
  Bell,
  BookOpen,
  ChevronDown,
  ClipboardList,
  LogOut,
  Search,
  UserRound,
  X,
} from "lucide-react";
import { useEffect, useMemo, useRef, useState } from "react";
import { api, clearStoredSession, getStoredSession } from "@/lib/api";
import type { Role } from "@/types/role";

type SearchResult = {
  label: string;
  description: string;
  href: string;
  type: "Course" | "Student" | "Teacher" | "Assignment";
};

export function Navbar({
  role,
  onMenu,
}: {
  role: Role;
  onMenu?: () => void;
}) {
  const router = useRouter();
  const searchInputRef = useRef<HTMLInputElement>(null);
  const searchDataPromiseRef = useRef<Promise<void> | null>(null);
  const profileRef = useRef<HTMLDivElement>(null);
  const [search, setSearch] = useState("");
  const [searchOpen, setSearchOpen] = useState(false);
  const [profileOpen, setProfileOpen] = useState(false);
  const [session, setSession] = useState<{ token: string; user: { uid: string; email: string; role: string; name?: string } } | null>(null);

  const [coursesList, setCoursesList] = useState<any[]>([]);
  const [assignmentsList, setAssignmentsList] = useState<any[]>([]);
  const [unreadNotifications, setUnreadNotifications] = useState(0);

  useEffect(() => {
    const s = getStoredSession();
    if (s) {
      setSession(s);
    }
  }, []);

  const ensureSearchData = () => {
    if (searchDataPromiseRef.current) return;
    searchDataPromiseRef.current = Promise.all([
      role === "admin" ? api.courses.getAll() : api.courses.getMyCourses(),
      api.assignments.getAll(),
    ])
      .then(([courses, assignments]) => {
        setCoursesList(Array.isArray(courses) ? courses : []);
        setAssignmentsList(Array.isArray(assignments) ? assignments : []);
      })
      .catch(() => {
        // Search remains usable for navigation even if optional suggestions fail.
      });
  };

  useEffect(() => {
    const refreshUnread = () => {
      api.notifications.getUnreadCount()
        .then(({ count }) => setUnreadNotifications(count))
        .catch(() => setUnreadNotifications(0));
    };
    refreshUnread();
    const timer = window.setInterval(refreshUnread, 30000);
    window.addEventListener("learnsphere:notifications-read", refreshUnread);
    return () => {
      window.clearInterval(timer);
      window.removeEventListener("learnsphere:notifications-read", refreshUnread);
    };
  }, []);

  const displayName = session?.user?.name || session?.user?.email || (role.charAt(0).toUpperCase() + role.slice(1) + " User");
  const initials = displayName
    .split(/[\s@._]+/)
    .filter(Boolean)
    .map((part) => part[0])
    .join("")
    .slice(0, 2)
    .toUpperCase() || role.slice(0, 2).toUpperCase();

  const handleSignOut = () => {
    clearStoredSession();
    setProfileOpen(false);
    router.push("/login");
  };

  useEffect(() => {
    const handleShortcut = (event: KeyboardEvent) => {
      if ((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === "k") {
        event.preventDefault();
        ensureSearchData();
        searchInputRef.current?.focus();
        setSearchOpen(true);
      }

      if (event.key === "Escape") {
        setSearchOpen(false);
        setProfileOpen(false);
        searchInputRef.current?.blur();
      }
    };

    const handleClick = (event: MouseEvent) => {
      if (profileRef.current && !profileRef.current.contains(event.target as Node)) {
        setProfileOpen(false);
      }
    };

    window.addEventListener("keydown", handleShortcut);
    window.addEventListener("mousedown", handleClick);

    return () => {
      window.removeEventListener("keydown", handleShortcut);
      window.removeEventListener("mousedown", handleClick);
    };
  }, []);

  const searchResults = useMemo<SearchResult[]>(() => {
    const query = search.trim().toLowerCase();
    if (!query) return [];

    const results: SearchResult[] = [];

    coursesList.forEach((course) => {
      const name = course.course_name || "";
      const code = course.category || "";
      if ([name, code].some((val) => String(val).toLowerCase().includes(query))) {
        results.push({
          label: name,
          description: code || "Course",
          href: `/${role}/courses/${course.course_id}`,
          type: "Course",
        });
      }
    });

    assignmentsList.forEach((assignment) => {
      const title = assignment.title || "";
      if (title.toLowerCase().includes(query)) {
        results.push({
          label: title,
          description: assignment.due_date ? `Due ${new Date(assignment.due_date).toLocaleDateString()}` : "Assignment",
          href: `/${role}/assignments?q=${encodeURIComponent(title)}`,
          type: "Assignment",
        });
      }
    });

    return results.slice(0, 8);
  }, [assignmentsList, coursesList, role, search]);

  const goToResult = (result: SearchResult) => {
    setSearchOpen(false);
    setSearch("");
    router.push(result.href);
  };

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center justify-between border-b border-(--border) bg-white/95 px-4 backdrop-blur-md sm:px-6 lg:px-8">
      <div className="flex items-center gap-3">
        <div className="relative w-72 sm:w-80 md:w-96">
          <Search
            size={17}
            className="pointer-events-none absolute left-3.5 top-1/2 -translate-y-1/2 text-slate-400"
          />

          <input
            ref={searchInputRef}
            type="search"
            value={search}
            onChange={(event) => {
              ensureSearchData();
              setSearch(event.target.value);
              setSearchOpen(true);
            }}
            onFocus={() => {
              ensureSearchData();
              setSearchOpen(true);
            }}
            placeholder="Search courses, assignments..."
            className="w-full rounded-2xl border border-(--border) bg-slate-50/70 py-2.5 pl-10 pr-10 text-sm outline-none transition placeholder:text-slate-400 focus:border-indigo-300 focus:bg-white focus:shadow-xs"
          />

          {search && (
            <button
              type="button"
              onClick={() => {
                setSearch("");
                setSearchOpen(false);
              }}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-slate-600"
              aria-label="Clear search"
            >
              <X size={15} />
            </button>
          )}

          {searchOpen && search.trim() && (
            <div className="card absolute left-0 right-0 top-full mt-2 max-h-80 overflow-y-auto p-2 shadow-xl">
              <div className="px-3 py-1 text-[11px] font-bold uppercase tracking-wider text-slate-400">
                Matching Results ({searchResults.length})
              </div>

              {searchResults.map((result) => (
                <button
                  key={`${result.type}-${result.label}`}
                  type="button"
                  onClick={() => goToResult(result)}
                  className="flex w-full items-center justify-between gap-3 rounded-xl p-3 text-left transition hover:bg-slate-50"
                >
                  <div className="flex items-center gap-3 min-w-0">
                    <span className="grid h-8 w-8 shrink-0 place-items-center rounded-lg bg-indigo-50 text-(--brand)">
                      {result.type === "Course" ? (
                        <BookOpen size={16} />
                      ) : (
                        <ClipboardList size={16} />
                      )}
                    </span>

                    <div className="min-w-0">
                      <div className="truncate text-sm font-semibold">
                        {result.label}
                      </div>
                      <div className="truncate text-xs text-slate-500">
                        {result.description}
                      </div>
                    </div>
                  </div>

                  <span className="shrink-0 rounded-full bg-slate-100 px-2.5 py-1 text-[10px] font-semibold text-slate-600">
                    {result.type}
                  </span>
                </button>
              ))}

              {searchResults.length === 0 && (
                <div className="p-4 text-center text-sm text-slate-500">
                  No matching results for “{search}”.
                </div>
              )}
            </div>
          )}
        </div>
      </div>

      <div className="flex items-center gap-3">
        <Link
          href={`/${role}/notifications`}
          prefetch
          className="icon-button relative"
          aria-label="View notifications"
        >
          <Bell size={19} />
          {unreadNotifications > 0 && (
            <span className="absolute right-1.5 top-1.5 grid min-h-4 min-w-4 place-items-center rounded-full bg-red-500 px-1 text-[9px] font-bold text-white">
              {unreadNotifications > 9 ? "9+" : unreadNotifications}
            </span>
          )}
        </Link>

        <div ref={profileRef} className="relative">
          <button
            type="button"
            onClick={() => setProfileOpen((current) => !current)}
            className="flex items-center gap-2 rounded-2xl border border-(--border) bg-white p-1.5 pr-3 transition hover:border-slate-300"
            aria-expanded={profileOpen}
            aria-haspopup="menu"
          >
            <div className="grid h-8 w-8 place-items-center rounded-xl bg-(--brand) text-xs font-bold text-white">
              {initials}
            </div>

            <div className="hidden text-left sm:block">
              <div className="text-xs font-bold text-slate-900 line-clamp-1 max-w-[120px]">
                {displayName}
              </div>
              <div className="text-[10px] uppercase tracking-wider text-slate-400">
                {role}
              </div>
            </div>

            <ChevronDown size={14} className="text-slate-400" />
          </button>

          {profileOpen && (
            <div className="card absolute right-0 top-full mt-2 w-56 p-2 shadow-xl">
              <div className="border-b border-(--border) px-3 py-2 text-xs">
                <div className="font-bold text-slate-900">{displayName}</div>
                <div className="text-slate-500 truncate">{session?.user?.email}</div>
              </div>

              <div className="py-1">
                <Link
                  href={`/${role}/profile`}
                  onClick={() => setProfileOpen(false)}
                  prefetch
                  className="flex items-center gap-2.5 rounded-xl px-3 py-2 text-sm text-slate-700 hover:bg-slate-50"
                >
                  <UserRound size={16} />
                  Profile Settings
                </Link>

                <button
                  type="button"
                  onClick={handleSignOut}
                  className="flex w-full items-center gap-2.5 rounded-xl px-3 py-2 text-sm text-rose-600 hover:bg-rose-50"
                >
                  <LogOut size={16} />
                  Sign Out
                </button>
              </div>
            </div>
          )}
        </div>
      </div>
    </header>
  );
}
