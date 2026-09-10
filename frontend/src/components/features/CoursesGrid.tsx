"use client";

import Link from "next/link";
import { useCallback, useEffect, useMemo, useState } from "react";
import { BookOpen, Check, Loader2, X } from "lucide-react";
import { api } from "@/lib/api";
import { showSuccess } from "@/context/FeedbackContext";
import { InlineError, ProgressBar, StatusBadge } from "@/components/ui";
import type { Role } from "@/types/role";
import { GridSkeleton } from "@/components/ui/Skeleton";

export interface CourseViewItem {
  id: number;
  title: string;
  category: string;
  teacher: string;
  students: number;
  progress: number;
  status: string;
  lessons: number;
  modules: number;
  enrolled: boolean;
  hasAssignedTeacher: boolean;
}

export function CoursesGrid({ role }: { role: Role }) {
  const [courses, setCourses] = useState<CourseViewItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [query, setQuery] = useState("");
  const [enrollingCourseId, setEnrollingCourseId] = useState<number | null>(null);
  const [studentTab, setStudentTab] = useState<"my" | "browse">("my");
  const [error, setError] = useState("");

  const fetchCourses = useCallback(async () => {
    try {
      setError("");
      const [data, myEnrollments, myCourses] = role === "student"
        ? await Promise.all([
            api.courses.getAll(),
            api.enrollments.getMyEnrollments(),
            api.courses.getMyCourses(),
          ])
        : [role === "admin" ? await api.courses.getAll() : await api.courses.getMyCourses(), [], []];
      if (Array.isArray(data)) {
        const myCourseData = new Map(
          (Array.isArray(myCourses) ? myCourses : []).map((course: any) => [
            Number(course.course_id),
            course,
          ])
        );
        const enrolledCourseIds = new Set(
          (Array.isArray(myEnrollments) ? myEnrollments : [])
            .filter((e: any) => (e.status || "active") === "active")
            .map((e: any) => Number(e.course_id))
        );
        const mapped: CourseViewItem[] = data.map((catalogCourse: any) => {
          const c = myCourseData.get(Number(catalogCourse.course_id)) || catalogCourse;
          const hasAssignedTeacher = Array.isArray(c.teachers) && c.teachers.length > 0;
          const teacherName =
            hasAssignedTeacher
              ? c.teachers.map((teacher: any) => teacher.name || `Teacher ${teacher.teacher_id}`).join(", ")
              : "Teacher Not Assigned Yet";

          return {
            id: c.course_id,
            title: c.course_name,
            category: c.category || "General",
            teacher: teacherName,
            students: c.enrollment_count ?? 0,
            progress: c.overall_progress_percentage ? Math.round(Number(c.overall_progress_percentage)) : 0,
            status: c.status || "draft",
            lessons: Number(c.lesson_count ?? 0),
            modules: Number(c.module_count ?? c.modules?.length ?? 0),
            enrolled: enrolledCourseIds.has(Number(c.course_id)),
            hasAssignedTeacher,
          };
        });
        setCourses(mapped);
      } else {
        setCourses([]);
      }
    } catch (err) {
      console.error("Failed to load courses:", err);
      setCourses([]);
      setError("Unable to load courses. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [role]);

  const handleEnroll = async (courseId: number) => {
    setError("");
    setEnrollingCourseId(courseId);
    try {
      await api.enrollments.enroll(courseId);
      setCourses((current) => current.map((course) =>
        course.id === courseId ? { ...course, enrolled: true } : course
      ));
      showSuccess("You are enrolled and can access the course now.");
    } catch (err: any) {
      const message = String(err?.message || "");
      if (message.toLowerCase().includes("already enrolled")) {
        setCourses((current) => current.map((course) =>
          course.id === courseId ? { ...course, enrolled: true } : course
        ));
        showSuccess("You are already enrolled in this course.");
      } else {
        setError(message || "Unable to enroll in this course.");
      }
    } finally {
      setEnrollingCourseId(null);
    }
  };

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setQuery(params.get("q")?.trim().toLowerCase() ?? "");
    fetchCourses();
  }, [fetchCourses]);

  // Listen for refresh events triggered by mutations
  useEffect(() => {
    const handleRefresh = (event: Event) => {
      const detail = (event as CustomEvent<{ action?: string }>).detail;
      if (
        !detail?.action ||
        detail.action.includes("course") ||
        detail.action.includes("enrollment")
      ) {
        fetchCourses();
      }
    };

    window.addEventListener("learnsphere:refresh", handleRefresh);
    return () => window.removeEventListener("learnsphere:refresh", handleRefresh);
  }, [fetchCourses]);

  const filteredCourses = useMemo(() => {
    const coursesForTab = role === "student"
      ? courses.filter((course) => studentTab === "my" ? course.enrolled : !course.enrolled)
      : courses;

    return query
        ? coursesForTab.filter((course) =>
            [course.title, course.category, course.teacher].some((value) =>
              String(value).toLowerCase().includes(query)
            )
          )
        : coursesForTab;
  }, [courses, query, role, studentTab]);

  if (loading) {
    return <GridSkeleton />;
  }

  return (
    <>
      <InlineError message={error} className="mb-4" />
      {role === "student" && (
        <div className="mb-5 flex w-fit gap-1 rounded-xl bg-slate-100 p-1" role="tablist" aria-label="Student courses">
          <button
            type="button"
            role="tab"
            aria-selected={studentTab === "my"}
            onClick={() => setStudentTab("my")}
            className={`rounded-xl px-4 py-2 text-sm font-semibold transition ${studentTab === "my" ? "bg-white text-indigo-700 shadow-sm" : "text-slate-500 hover:text-slate-800"}`}
          >
            My Courses ({courses.filter((course) => course.enrolled).length})
          </button>
          <button
            type="button"
            role="tab"
            aria-selected={studentTab === "browse"}
            onClick={() => setStudentTab("browse")}
            className={`rounded-xl px-4 py-2 text-sm font-semibold transition ${studentTab === "browse" ? "bg-white text-indigo-700 shadow-sm" : "text-slate-500 hover:text-slate-800"}`}
          >
            Browse Courses ({courses.filter((course) => !course.enrolled).length})
          </button>
        </div>
      )}

      {query && (
        <div className="mb-4 flex items-center justify-between gap-3 rounded-2xl border border-indigo-100 bg-indigo-50 px-4 py-3 text-sm text-indigo-800">
          <span>Showing course results for “{query}”</span>
          <Link
            href={`/${role}/courses`}
            prefetch
            className="grid h-8 w-8 place-items-center rounded-lg transition hover:bg-white/70"
            aria-label="Clear course search"
          >
            <X size={16} />
          </Link>
        </div>
      )}

      {filteredCourses.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {filteredCourses.map((course, index) => (
            <article
              key={course.id}
              className="card group overflow-hidden transition hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-lg"
            >
              <Link href={`/${role}/courses/${course.id}`} prefetch>
              <div
                className={`h-24 p-5 text-white ${
                  index % 3 === 0
                    ? "bg-linear-to-br from-indigo-500 to-violet-700"
                    : index % 3 === 1
                    ? "bg-linear-to-br from-amber-400 to-orange-600"
                    : "bg-linear-to-br from-emerald-400 to-teal-700"
                }`}
              >
                <div className="text-xs font-semibold uppercase tracking-[0.16em] text-white/70">
                  {course.category}
                </div>
                <BookOpen className="mt-4" size={25} />
              </div>
              <div className="p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h3 className="font-bold group-hover:text-(--brand)">{course.title}</h3>
                    <p className="mt-1 text-xs text-slate-500">{course.teacher}</p>
                  </div>
                  <StatusBadge status={course.status} />
                </div>
                <div className="mt-4 grid grid-cols-3 gap-2 text-center">
                  <div className="rounded-xl bg-slate-50 p-2">
                    <div className="font-bold">{course.modules}</div>
                    <div className="text-[10px] text-slate-400">Modules</div>
                  </div>
                  <div className="rounded-xl bg-slate-50 p-2">
                    <div className="font-bold">{course.lessons}</div>
                    <div className="text-[10px] text-slate-400">Lessons</div>
                  </div>
                  <div className="rounded-xl bg-slate-50 p-2">
                    {role === "student" && studentTab === "my" && course.enrolled ? (
                      <>
                        <div className="font-bold">{course.progress}%</div>
                        <div className="text-[10px] text-slate-400">Your progress</div>
                      </>
                    ) : (
                      <>
                        <div className="font-bold">{course.students}</div>
                        <div className="text-[10px] text-slate-400">Students</div>
                      </>
                    )}
                  </div>
                </div>
                {role === "student" && studentTab === "my" && course.enrolled && (
                  <div className="mt-4"><ProgressBar value={course.progress} /></div>
                )}
              </div>
              </Link>
              {role === "student" && (
                <div className="border-t border-slate-100 p-4">
                  {course.enrolled ? (
                    <Link
                      href={`/student/courses/${course.id}`}
                      className="secondary-button w-full justify-center text-emerald-700"
                    >
                      <Check size={16} />
                      Enrolled
                    </Link>
                  ) : (
                    <button
                      type="button"
                      className="primary-button w-full justify-center disabled:cursor-not-allowed disabled:bg-slate-200 disabled:text-slate-500 disabled:opacity-100"
                      disabled={!course.hasAssignedTeacher || enrollingCourseId === course.id}
                      onClick={() => handleEnroll(course.id)}
                    >
                      {enrollingCourseId === course.id && <Loader2 size={16} className="animate-spin" />}
                      {!course.hasAssignedTeacher
                        ? "Coming Soon"
                        : enrollingCourseId === course.id
                          ? "Enrolling..."
                          : "Enroll"}
                    </button>
                  )}
                </div>
              )}
            </article>
          ))}
        </div>
      ) : (
        <div className="card p-12 text-center text-sm text-slate-500">
          {query
            ? `No courses match “${query}”.`
            : role === "student" && studentTab === "my"
              ? "You are not enrolled in any courses yet. Browse courses to get started."
              : role === "student"
                ? "You are enrolled in every available course."
                : "No courses available."}
        </div>
      )}
    </>
  );
}
