"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";
import { Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { InlineError, ProgressBar } from "@/components/ui";
import { GridSkeleton } from "@/components/ui/Skeleton";

export function ProgressGrid() {
  const [courses, setCourses] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const fetchProgress = useCallback(async () => {
    try {
      setError("");
      const data = await api.courses.getMyCourses();
      setCourses(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load progress:", err);
      setCourses([]);
      setError("Unable to load course progress. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchProgress();
  }, [fetchProgress]);

  if (loading) {
    return <GridSkeleton cards={4} />;
  }

  return (
    <>
      <InlineError message={error} className="mb-4" />
      {courses.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2">
          {courses.map((course) => {
            const progress = course.overall_progress_percentage ? Math.round(Number(course.overall_progress_percentage)) : 0;
            const lessons = course.lesson_count ?? 0;

            return (
              <Link
                key={course.course_id}
                href={`/student/courses/${course.course_id}`}
                prefetch
                className="card p-5 transition hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-lg"
              >
                <div className="flex justify-between gap-4">
                  <div>
                    <h3 className="font-bold text-slate-900">{course.course_name}</h3>
                    <p className="mt-1 text-sm text-slate-500">{lessons} lessons</p>
                  </div>

                  <div className="text-2xl font-bold text-(--brand)">{progress}%</div>
                </div>

                <div className="mt-5">
                  <ProgressBar value={progress} />
                </div>

                <div className="mt-4 flex justify-between text-xs text-slate-400">
                  <span>{Math.round((lessons * progress) / 100)} lessons completed</span>
                  <span>{lessons} total</span>
                </div>
              </Link>
            );
          })}
        </div>
      ) : (
        <div className="card p-12 text-center text-sm text-slate-500">
          No course enrollments or progress records found.
        </div>
      )}
    </>
  );
}
