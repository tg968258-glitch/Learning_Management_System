"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { ArrowLeft, BookOpen, Loader2, Trash2, UsersRound, X } from "lucide-react";
import { api } from "@/lib/api";
import { showSuccess } from "@/context/FeedbackContext";
import {
  ActionDialogButton,
  InlineError,
  PageHeader,
  ProgressBar,
  StatusBadge,
} from "@/components/ui";
import type { Role } from "@/types/role";
import { PageSkeleton } from "@/components/ui/Skeleton";

interface Teacher {
  teacher_id: number;
  name?: string | null;
  specialization?: string | null;
}

export function CourseDetail({
  role,
  courseId,
}: {
  role: Role;
  courseId: number;
}) {
  const [course, setCourse] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [teachers, setTeachers] = useState<Teacher[]>([]);
  const [selectedTeacherId, setSelectedTeacherId] = useState("");
  const [loadingTeachers, setLoadingTeachers] = useState(false);
  const [assigning, setAssigning] = useState(false);
  const [removingTeacherId, setRemovingTeacherId] = useState<number | null>(null);
  const [teacherToRemove, setTeacherToRemove] = useState<Teacher | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [error, setError] = useState("");

  const fetchCourse = useCallback(async () => {
    try {
      setError("");
      const data = await api.courses.getById(courseId);
      setCourse(data);
    } catch (err) {
      console.error("Failed to load course:", err);
      setCourse(null);
      setError("Unable to load this course. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [courseId]);

  useEffect(() => {
    fetchCourse();
  }, [fetchCourse]);

  const openTeacherModal = async () => {
    setLoadingTeachers(true);
    setError("");
    try {
      const data = await api.teachers.getAll();
      setTeachers(data);
      setSelectedTeacherId("");
      setShowModal(true);
    } catch (err: any) {
      setError(err.message || "Unable to load teachers. Please try again.");
    } finally {
      setLoadingTeachers(false);
    }
  };

  const handleAssignTeacher = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    if (!selectedTeacherId) {
      setError("Please select a teacher.");
      return;
    }

    setAssigning(true);
    setError("");
    try {
      await api.courses.assignTeacher(courseId, Number(selectedTeacherId));
      showSuccess("Teacher added to the course successfully.");
      setShowModal(false);
      await fetchCourse();
    } catch (err: any) {
      setError(err.message || "Unable to assign teacher. Please try again.");
    } finally {
      setAssigning(false);
    }
  };

  const handleRemoveTeacher = async () => {
    if (!teacherToRemove) return;
    const teacherId = teacherToRemove.teacher_id;
    setRemovingTeacherId(teacherId);
    setError("");
    try {
      await api.courses.removeTeacher(courseId, teacherId);
      showSuccess("Teacher removed from the course.");
      setTeacherToRemove(null);
      await fetchCourse();
    } catch (err: any) {
      setError(err.message || "Unable to remove teacher.");
    } finally {
      setRemovingTeacherId(null);
    }
  };

  useEffect(() => {
    const handleRefresh = (event: Event) => {
      const detail = (event as CustomEvent<{ action?: string }>).detail;
      if (!detail?.action || detail.action.includes("course") || detail.action.includes("module") || detail.action.includes("lesson")) {
        fetchCourse();
      }
    };

    window.addEventListener("learnsphere:refresh", handleRefresh);
    return () => window.removeEventListener("learnsphere:refresh", handleRefresh);
  }, [fetchCourse]);

  if (loading) {
    return <PageSkeleton variant="detail" />;
  }

  if (!course) {
    return (
      <div className="card p-8 text-center">
        <div className="font-bold text-slate-800">Course not found</div>
        <p className="text-sm text-slate-500 mt-1">
          The requested course could not be retrieved from the database.
        </p>
        <Link href={`/${role}/courses`} className="secondary-button mt-4">
          Back to courses
        </Link>
      </div>
    );
  }

  const availableTeachers = teachers.filter(
    (teacher) => !course.teachers?.some((assigned: Teacher) => assigned.teacher_id === teacher.teacher_id)
  );

  const totalLessons =
    course.lesson_count ??
    (course.modules?.reduce((acc: number, m: any) => acc + (m.lessons?.length || 0), 0) || 0);

  const totalStudents = course.enrollment_count ?? 0;
  const totalModules = Number(course.module_count ?? course.modules?.length ?? 0);
  const showStudentProgress = role === "student" && course.is_enrolled === true;
  const progress = showStudentProgress
    ? Math.round(Number(course.overall_progress_percentage ?? 0))
    : null;

  return (
    <>
      {!showModal && !teacherToRemove && <InlineError message={error} className="mb-4" />}
      <div className="mb-3">
        <Link
          href={`/${role}/courses`}
          prefetch
          className="inline-flex items-center gap-2 text-sm font-semibold text-slate-500 hover:text-slate-900"
        >
          <ArrowLeft size={16} />
          Back to courses
        </Link>
      </div>

      <PageHeader
        title={course.course_name}
        actions={
          role === "admin" ? (
            <ActionDialogButton
              action="edit-course"
              label="Edit course"
              variant="secondary"
              initialValues={{
                courseId: String(course.course_id),
                courseDisplayId: `CRS-${String(course.course_id).padStart(3, "0")}`,
                courseName: course.course_name,
                description: course.description || "",
                status: course.status === "active" ? "Active" : "Inactive",
              }}
              onSuccess={fetchCourse}
            />
          ) : role === "teacher" ? (
            <Link
              href="/teacher/content"
              prefetch
              className="primary-button"
            >
              Manage content
            </Link>
          ) : (
            <Link
              href="/student/learning"
              prefetch
              className="primary-button"
            >
              Continue learning
            </Link>
          )
        }
      />

      <div className="grid gap-4 xl:grid-cols-[1.2fr_.8fr]">
        <section className="card p-5">
          <div className="flex items-start justify-between gap-4">
            <div>
              <div className="text-sm font-semibold text-(--brand)">
                {course.category || "General"}
              </div>

              <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-600">
                {course.description || "Course details are managed through the LMS portal."}
              </p>
            </div>

            <StatusBadge status={course.status || "draft"} />
          </div>

          <div className="mt-4 flex flex-wrap gap-2 text-xs">
            <span className="rounded-full bg-indigo-50 px-3 py-1.5 font-semibold text-indigo-700">
              {course.category || "General"}
            </span>
            <span className="rounded-full bg-slate-100 px-3 py-1.5 font-semibold text-slate-600">
              {totalLessons} lessons
            </span>
          </div>

          <div className="mt-5 grid gap-3 sm:grid-cols-3">
            <div className="rounded-2xl bg-slate-50 p-4">
              <BookOpen size={18} className="text-(--brand)" />
              <div className="mt-3 text-2xl font-bold">{totalModules}</div>
              <div className="text-xs text-slate-500">Modules</div>
            </div>

            <div className="rounded-2xl bg-slate-50 p-4">
              <BookOpen size={18} className="text-(--brand)" />
              <div className="mt-3 text-2xl font-bold">{totalLessons}</div>
              <div className="text-xs text-slate-500">Lessons</div>
            </div>

            <div className="rounded-2xl bg-slate-50 p-4">
              {showStudentProgress ? (
                <>
                  <div className="text-2xl font-bold text-(--brand)">{progress}%</div>
                  <div className="mt-3"><ProgressBar value={progress ?? 0} /></div>
                  <div className="mt-2 text-xs text-slate-500">Your progress</div>
                </>
              ) : (
                <>
                  <UsersRound size={18} className="text-(--brand)" />
                  <div className="mt-3 text-2xl font-bold">{totalStudents}</div>
                  <div className="text-xs text-slate-500">Enrolled students</div>
                </>
              )}
            </div>
          </div>
        </section>

        <section className="card p-5">
          <div className="font-bold">Instructors</div>

          <div className="mt-4 space-y-2 rounded-2xl bg-slate-50 p-4">
            {course.teachers?.length ? course.teachers.map((teacher: Teacher) => (
              <div key={teacher.teacher_id} className="flex items-center justify-between gap-3 rounded-xl bg-white px-3 py-2">
                <div><div className="font-semibold">{teacher.name || `Teacher ${teacher.teacher_id}`}</div><div className="text-xs text-slate-500">{teacher.specialization || "Instructor"}</div></div>
                {role === "admin" && (
                  <button type="button" className="icon-button text-rose-500" onClick={() => setTeacherToRemove(teacher)} disabled={removingTeacherId === teacher.teacher_id} aria-label={`Remove ${teacher.name || "teacher"}`}>
                    {removingTeacherId === teacher.teacher_id ? <Loader2 size={15} className="animate-spin" /> : <Trash2 size={15} />}
                  </button>
                )}
              </div>
            )) : <div className="text-sm text-slate-500">No instructors assigned.</div>}
            {role === "admin" && (
              <button
                type="button"
                className="secondary-button mt-4"
                onClick={openTeacherModal}
                disabled={loadingTeachers}
              >
                {loadingTeachers && <Loader2 size={15} className="animate-spin" />}
                {loadingTeachers
                  ? "Loading teachers..."
                  : "Add Teacher"}
              </button>
            )}
          </div>

          <div className="mt-5 font-bold">Course ID</div>

          <div className="mt-2 text-sm text-slate-500">
            CRS-{String(course.course_id).padStart(3, "0")}
          </div>
        </section>
      </div>

      {teacherToRemove && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4 backdrop-blur-sm">
          <button
            type="button"
            className="absolute inset-0"
            onClick={() => !removingTeacherId && setTeacherToRemove(null)}
            aria-label="Cancel teacher removal"
          />
          <div className="card relative z-10 w-full max-w-md p-6 shadow-2xl" role="dialog" aria-modal="true" aria-labelledby="remove-teacher-title">
            <InlineError message={error} className="mb-4" />
            <h2 id="remove-teacher-title" className="text-xl font-bold">Remove Teacher</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              Are you sure you want to remove this teacher from this course?
            </p>
            <p className="mt-2 text-sm font-semibold text-slate-900">
              {teacherToRemove.name || `Teacher ${teacherToRemove.teacher_id}`}
            </p>
            <div className="mt-6 flex justify-end gap-2 border-t border-(--border) pt-4">
              <button
                type="button"
                className="secondary-button"
                onClick={() => setTeacherToRemove(null)}
                disabled={removingTeacherId !== null}
              >
                Cancel
              </button>
              <button
                type="button"
                className="rounded-xl bg-rose-600 px-4 py-2 text-sm font-semibold text-white hover:bg-rose-700 disabled:opacity-60"
                onClick={handleRemoveTeacher}
                disabled={removingTeacherId !== null}
              >
                {removingTeacherId !== null && <Loader2 size={15} className="mr-2 inline animate-spin" />}
                {removingTeacherId !== null ? "Removing..." : "Remove"}
              </button>
            </div>
          </div>
        </div>
      )}

      {showModal && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4 backdrop-blur-sm">
          <button
            type="button"
            className="absolute inset-0"
            onClick={() => !assigning && setShowModal(false)}
            aria-label="Close dialog"
          />

          <div className="card relative z-10 w-full max-w-md p-6 shadow-2xl" role="dialog" aria-modal="true" aria-labelledby="teacher-dialog-title">
            <InlineError message={error} className="mb-4" />
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 id="teacher-dialog-title" className="text-xl font-bold">
                  Add Teacher
                </h2>
                <p className="mt-1 text-sm text-slate-500">Add another instructor to {course.course_name}.</p>
              </div>
              <button
                type="button"
                className="icon-button"
                onClick={() => setShowModal(false)}
                disabled={assigning}
                aria-label="Close dialog"
              >
                <X size={17} />
              </button>
            </div>

            <form onSubmit={handleAssignTeacher} className="mt-5 space-y-4">
              <label className="block">
                <span className="mb-1.5 block text-xs font-semibold text-slate-500">Teacher</span>
                <select
                  value={selectedTeacherId}
                  onChange={(event) => setSelectedTeacherId(event.target.value)}
                  className="w-full rounded-xl border border-(--border) bg-white px-3 py-2.5 text-sm outline-none focus:border-indigo-300"
                  disabled={assigning}
                  required
                >
                  <option value="">Select a teacher</option>
                  {availableTeachers.map((teacher) => (
                    <option key={teacher.teacher_id} value={teacher.teacher_id}>
                      {teacher.name || `Teacher ${teacher.teacher_id}`}
                      {teacher.specialization ? ` — ${teacher.specialization}` : ""}
                    </option>
                  ))}
                </select>
              </label>

              {availableTeachers.length === 0 && (
                <p className="rounded-xl bg-amber-50 p-3 text-sm text-amber-700">All available teachers are already assigned.</p>
              )}

              <div className="flex justify-end gap-2 pt-2">
                <button type="button" className="secondary-button" onClick={() => setShowModal(false)} disabled={assigning}>
                  Cancel
                </button>
                <button type="submit" className="primary-button" disabled={assigning || availableTeachers.length === 0}>
                  {assigning && <Loader2 size={15} className="animate-spin" />}
                  {assigning ? "Assigning..." : "Confirm Assignment"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
