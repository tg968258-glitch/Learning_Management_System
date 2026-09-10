"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useCallback, useEffect, useState } from "react";
import {
  BookOpen,
  CalendarDays,
  ChevronRight,
  Loader2,
} from "lucide-react";

import { api } from "@/lib/api";
import {
  DataTable,
  InlineError,
  ProgressBar,
  SectionTitle,
  StatCard,
  StatusBadge,
} from "@/components/ui";

import type { DataTableColumn } from "@/components/ui";
import type { Role } from "@/types/role";
import { DashboardSkeleton } from "@/components/ui/Skeleton";


interface DashboardStat {
  label: string;
  value: string | number;
  change?: string;
  trend?: "up" | "down" | "neutral";
  iconName: "book" | "users" | "chart" | "calendar" | "bell";
}


export function DashboardOverview({
  role,
}: {
  role: Role;
}) {
  const router = useRouter();

  const [loading, setLoading] = useState(true);

  const [courses, setCourses] = useState<any[]>([]);
  const [assignments, setAssignments] = useState<any[]>([]);
  const [sessions, setSessions] = useState<any[]>([]);
  const [stats, setStats] = useState<DashboardStat[]>([]);
  const [error, setError] = useState("");


  // =========================================================
  // LOAD DASHBOARD DATA
  // =========================================================

  const loadDashboardData = useCallback(async () => {
    try {
      setLoading(true);
      setError("");
      const statsRequest = role === "admin"
        ? api.admin.getDashboardStats()
        : role === "teacher"
          ? api.dashboard.getTeacherStats()
          : api.dashboard.getStudentStats();
      const coursesRequest = role === "admin"
        ? api.courses.getAll()
        : api.courses.getMyCourses();

      // Lists below feed visible activity panels. Card totals come exclusively
      // from the lightweight aggregate endpoint above.
      const [statsData, coursesData, assignmentsData, sessionsData] = await Promise.all([
        statsRequest,
        coursesRequest,
        api.assignments.getAll(),
        api.sessions.getAll(),
      ]);

      const coursesList = Array.isArray(coursesData) ? coursesData : [];
      const assignmentsList = Array.isArray(assignmentsData) ? assignmentsData : [];
      const today = new Date().toISOString().slice(0, 10);
      const sessionsList = (Array.isArray(sessionsData) ? sessionsData : [])
        .filter((session: any) => !session.session_date || session.session_date >= today)
        .sort((a: any, b: any) =>
          `${a.session_date || ""}T${a.start_time || "00:00:00"}`.localeCompare(
            `${b.session_date || ""}T${b.start_time || "00:00:00"}`
          )
        );

      setCourses(coursesList);
      setAssignments(assignmentsList);
      setSessions(sessionsList);

      if (role === "admin") {
        const data = statsData as Awaited<ReturnType<typeof api.admin.getDashboardStats>>;
        setStats([
          { label: "Total Courses", value: data.total_courses, iconName: "book" },
          { label: "Total Students", value: data.total_students, iconName: "users" },
          { label: "Active Instructors", value: data.active_instructors, iconName: "chart" },
          { label: "Active Enrollments", value: data.active_enrollments, iconName: "calendar" },
        ]);
      } else if (role === "teacher") {
        const data = statsData as Awaited<ReturnType<typeof api.dashboard.getTeacherStats>>;
        setStats([
          { label: "Active Courses", value: data.active_courses, iconName: "book" },
          { label: "Total Students", value: data.total_students, iconName: "users" },
          { label: "Assignments", value: data.assignments, iconName: "chart" },
          { label: "Live Sessions", value: data.live_sessions, iconName: "calendar" },
        ]);
      } else {
        const data = statsData as Awaited<ReturnType<typeof api.dashboard.getStudentStats>>;
        setStats([
          { label: "Enrolled Courses", value: data.enrolled_courses, iconName: "book" },
          { label: "Completed Lessons", value: data.completed_lessons, iconName: "chart" },
          { label: "Assignments", value: data.assignments, iconName: "users" },
          { label: "Upcoming Sessions", value: data.upcoming_sessions, iconName: "calendar" },
        ]);
      }
    } catch (err) {
      console.error(
        "Failed to load dashboard data:",
        err
      );
      setError("Unable to load dashboard data. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [role]);


  // =========================================================
  // INITIAL LOAD
  // =========================================================

  useEffect(() => {
    loadDashboardData();
  }, [loadDashboardData]);


  // =========================================================
  // REFRESH DASHBOARD AFTER CHANGES
  // =========================================================

  useEffect(() => {
    const handleRefresh = () => {
      loadDashboardData();
    };

    window.addEventListener(
      "learnsphere:refresh",
      handleRefresh
    );

    return () => {
      window.removeEventListener(
        "learnsphere:refresh",
        handleRefresh
      );
    };
  }, [loadDashboardData]);


  // =========================================================
  // ASSIGNMENT TABLE COLUMNS
  // =========================================================

  const assignmentColumns: DataTableColumn<any>[] = [
    {
      key: "assignment",
      header: "Assignment",

      render: (assignment) => (
        <span className="font-semibold">
          {assignment.title}
        </span>
      ),
    },

    {
      key: "due",
      header: "Due",

      render: (assignment) => (
        <span className="text-slate-500">
          {assignment.due_date
            ? new Date(
              assignment.due_date
            ).toLocaleDateString()
            : "Flexible"}
        </span>
      ),
    },

    {
      key: "marks",
      header: "Marks",

      render: (assignment) => (
        <span className="text-slate-600">
          {assignment.max_marks ?? 100} pts
        </span>
      ),
    },

    {
      key: "status",
      header: "Status",

      render: () => (
        <StatusBadge status="Active" />
      ),
    },
  ];


  // =========================================================
  // LOADING
  // =========================================================

  if (loading) {
    return <DashboardSkeleton />;
  }


  // =========================================================
  // DASHBOARD UI
  // =========================================================

  return (
    <>
      <InlineError message={error} className="mb-4" />
      {/* =====================================================
          STAT CARDS
      ====================================================== */}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {stats.map((stat) => (
          <StatCard
            key={stat.label}
            {...stat}
            href={role === "teacher" && stat.label === "Total Students" ? "/teacher/enrollments" : undefined}
          />
        ))}
      </div>


      {/* =====================================================
          COURSES + UPCOMING SESSIONS
      ====================================================== */}

      <div className="mt-5 grid gap-5 xl:grid-cols-[1.5fr_.8fr]">
        {/* ===================================================
            COURSES
        ==================================================== */}

        <section className="card p-5">
          <SectionTitle
            title={
              role === "student"
                ? "Continue learning"
                : "Course activity"
            }
          />

          <div className="space-y-3">
            {courses
              .slice(0, 4)
              .map((course, index) => {
                const progress =
                  course.overall_progress_percentage
                    ? Math.round(
                      Number(
                        course.overall_progress_percentage
                      )
                    )
                    : 0;

                const teacherName =
                  course.teachers &&
                    course.teachers.length > 0
                    ? course.teachers.map((teacher: any) => teacher.name || `Teacher ${teacher.teacher_id}`).join(", ")
                    : "Assigned Instructor";

                return (
                  <Link
                    key={course.course_id}
                    href={`/${role}/courses/${course.course_id}`}
                    prefetch
                    className="group flex flex-col gap-4 rounded-2xl border border-(--border) p-4 transition hover:border-indigo-200 hover:bg-slate-50 sm:flex-row sm:items-center"
                  >
                    {/* COURSE ICON */}

                    <div
                      className={`grid h-14 w-14 shrink-0 place-items-center rounded-2xl ${index === 0
                          ? "bg-indigo-100 text-indigo-700"
                          : index === 1
                            ? "bg-amber-100 text-amber-700"
                            : "bg-emerald-100 text-emerald-700"
                        }`}
                    >
                      <BookOpen size={22} />
                    </div>


                    {/* COURSE INFO */}

                    <div className="min-w-0 flex-1">
                      <div className="flex items-center justify-between gap-2">
                        <div>
                          <div className="font-semibold group-hover:text-(--brand)">
                            {course.course_name}
                          </div>

                          <div className="mt-1 text-xs text-slate-500">
                            {course.category ||
                              "CRS"}{" "}
                            • {teacherName}
                          </div>
                        </div>

                        {role === "student" ? (
                          <span className="text-sm font-bold">{progress}%</span>
                        ) : (
                          <span className="shrink-0 text-xs font-semibold text-slate-500">
                            {course.module_count ?? course.modules?.length ?? 0} modules · {course.lesson_count ?? 0} lessons
                          </span>
                        )}
                      </div>

                      {role === "student" && (
                        <div className="mt-3"><ProgressBar value={progress} /></div>
                      )}
                    </div>


                    <ChevronRight
                      size={18}
                      className="text-slate-400 transition group-hover:translate-x-0.5"
                    />
                  </Link>
                );
              })}


            {/* NO COURSES */}

            {courses.length === 0 && (
              <div className="p-8 text-center text-sm text-slate-500">
                {role === "student"
                  ? "You are not enrolled in any courses yet."
                  : "No courses available at this time."}
              </div>
            )}
          </div>
        </section>


        {/* ===================================================
            UPCOMING SESSIONS
        ==================================================== */}

        <section className="card p-5">
          <SectionTitle title="Upcoming sessions" />

          <div className="space-y-2">
            {sessions
              .slice(0, 4)
              .map((session) => (
                <Link
                  key={session.session_id}
                  href={`/${role}/sessions`}
                  prefetch
                  className="flex gap-3 rounded-xl p-2 transition hover:bg-slate-50"
                >
                  <div className="grid h-11 w-11 shrink-0 place-items-center rounded-xl bg-(--brand-soft) text-(--brand)">
                    <CalendarDays
                      size={19}
                    />
                  </div>

                  <div className="min-w-0">
                    <div className="truncate text-sm font-semibold">
                      {session.topic ||
                        session.course_name ||
                        "Session"}
                    </div>

                    <div className="mt-1 text-xs text-slate-500">
                      {session.session_date}

                      {session.start_time
                        ? ` • ${session.start_time}`
                        : ""}
                    </div>

                    {session.meeting_link && (
                      <div className="mt-1 max-w-xs truncate text-xs font-medium text-(--brand)">
                        {
                          session.meeting_link
                        }
                      </div>
                    )}
                  </div>
                </Link>
              ))}


            {/* NO SESSIONS */}

            {sessions.length === 0 && (
              <div className="p-8 text-center text-sm text-slate-500">
                {role === "student"
                  ? courses.length === 0
                    ? "No sessions available because you are not enrolled in any course."
                    : "No scheduled sessions found for your courses."
                  : "No scheduled sessions found."}
              </div>
            )}
          </div>
        </section>
      </div>

      {/* =====================================================
          ASSIGNMENTS
      ====================================================== */}

      <section className="card mt-5 overflow-hidden">
        <div className="px-5 pt-5">
          <SectionTitle
            title={
              role === "student"
                ? "Assignment deadlines"
                : "Recent assignments"
            }
          />
        </div>

        {assignments.length > 0 ? (
          <DataTable
            rows={assignments.slice(0, 5)}
            columns={assignmentColumns}
            rowKey={(assignment) =>
              String(
                assignment.assignment_id ||
                assignment.title
              )
            }
            onRowClick={() => {
              router.push(
                `/${role}/assignments`
              );
            }}
          />
        ) : (
          <div className="p-8 text-center text-sm text-slate-500">
            {role === "student"
              ? courses.length === 0
                ? "No assignments available because you are not enrolled in any course."
                : "No assignments found for your courses."
              : "No assignments recorded yet."}
          </div>
        )}
      </section>
    </>
  );
}
