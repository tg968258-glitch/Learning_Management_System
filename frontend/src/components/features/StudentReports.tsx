"use client";

import { FormEvent, useEffect, useState } from "react";
import { Loader2, Search, UserRound } from "lucide-react";
import { api } from "@/lib/api";
import { ProgressBar, StatusBadge } from "@/components/ui";

type StudentOption = { student_id: number; student_name: string };

const asPercent = (value: number | null | undefined) =>
  value === null || value === undefined ? "Not graded" : `${Math.round(value)}%`;

export function StudentReports() {
  const [query, setQuery] = useState("");
  const [options, setOptions] = useState<StudentOption[]>([]);
  const [selected, setSelected] = useState<StudentOption | null>(null);
  const [report, setReport] = useState<any | null>(null);
  const [searching, setSearching] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [error, setError] = useState("");

  useEffect(() => {
    const term = query.trim();
    if (!term || (selected && term === selected.student_name)) {
      setOptions([]);
      setSearching(false);
      return;
    }

    let active = true;
    const timer = window.setTimeout(async () => {
      setSearching(true);
      try {
        const matches = await api.reports.searchStudents(term);
        if (active) setOptions(Array.isArray(matches) ? matches : []);
      } catch {
        if (active) {
          setOptions([]);
          setError("Unable to search students right now. Please try again.");
        }
      } finally {
        if (active) setSearching(false);
      }
    }, 300);

    return () => {
      active = false;
      window.clearTimeout(timer);
    };
  }, [query, selected]);

  const chooseStudent = (student: StudentOption) => {
    setSelected(student);
    setQuery(student.student_name);
    setOptions([]);
    setReport(null);
    setError("");
  };

  const generateReport = async (event: FormEvent) => {
    event.preventDefault();
    if (!selected) {
      setError("Search for and select a student before generating the report.");
      return;
    }

    setGenerating(true);
    setReport(null);
    setError("");
    try {
      setReport(await api.reports.generateStudent(selected.student_id));
    } catch (err: any) {
      setError(err?.message || "Unable to generate this student report. Please try again.");
    } finally {
      setGenerating(false);
    }
  };

  return (
    <div className="space-y-5">
      <form onSubmit={generateReport} className="card p-5">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end">
          <label className="relative min-w-0 flex-1 text-sm font-semibold text-slate-700">
            Search student by name or ID
            <div className="relative mt-1.5">
              <Search className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" size={18} />
              <input
                value={query}
                onChange={(event) => {
                  setQuery(event.target.value);
                  setSelected(null);
                  setReport(null);
                  setError("");
                }}
                placeholder="Start typing a student name or ID"
                autoComplete="off"
                className="w-full rounded-xl border border-slate-200 bg-white py-2.5 pl-10 pr-10 font-normal outline-none focus:border-indigo-500"
              />
              {searching && <Loader2 className="absolute right-3 top-1/2 -translate-y-1/2 animate-spin text-indigo-600" size={18} />}
            </div>

            {query.trim() && !selected && !searching && (
              <div className="absolute z-20 mt-1 max-h-64 w-full overflow-y-auto rounded-xl border border-slate-200 bg-white p-1 shadow-lg">
                {options.length ? options.map((student) => (
                  <button
                    key={student.student_id}
                    type="button"
                    onClick={() => chooseStudent(student)}
                    className="flex w-full items-center gap-3 rounded-lg px-3 py-2.5 text-left hover:bg-indigo-50"
                  >
                    <UserRound size={17} className="text-indigo-600" />
                    <span className="min-w-0 flex-1 truncate font-medium text-slate-800">{student.student_name}</span>
                    <span className="text-xs font-semibold text-slate-400">ID {student.student_id}</span>
                  </button>
                )) : (
                  <div className="px-3 py-3 font-normal text-slate-500">No matching students found.</div>
                )}
              </div>
            )}
          </label>

          <button type="submit" disabled={!selected || generating} className="primary-button justify-center disabled:cursor-not-allowed disabled:opacity-50">
            {generating && <Loader2 size={17} className="animate-spin" />}
            {generating ? "Generating…" : "Generate Report"}
          </button>
        </div>

        {selected && (
          <p className="mt-3 text-xs text-slate-500">
            Selected: <strong className="text-slate-700">{selected.student_name}</strong> · Student ID {selected.student_id}
          </p>
        )}
        {error && (
          <div role="alert" className="mt-4 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">
            {error}
          </div>
        )}
      </form>

      {generating && <ReportSkeleton />}

      {!generating && report && (
        <section className="space-y-4">
          <div className="card flex flex-wrap items-center justify-between gap-3 p-5">
            <div>
              <div className="font-bold text-slate-900">{report.student_name}</div>
              <div className="mt-1 text-xs text-slate-500">Student ID {report.student_id}</div>
            </div>
            <span className="rounded-full bg-indigo-50 px-3 py-1.5 text-xs font-semibold text-indigo-700">
              {report.courses.length} enrolled {report.courses.length === 1 ? "course" : "courses"}
            </span>
          </div>

          {report.courses.map((course: any) => (
            <article key={course.course_id} className="card p-5">
              <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <h3 className="font-bold text-slate-900">{course.course_name}</h3>
                  <p className="mt-1 text-xs text-slate-500">
                    Enrollment: {course.enrollment_status} · {course.lessons_completed}/{course.lesson_count} lessons completed
                  </p>
                </div>
                <div className="grid grid-cols-2 gap-5 text-left text-sm sm:text-right">
                  <div><div className="text-xs text-slate-500">Progress</div><strong className="text-(--brand)">{Math.round(course.progress_percentage)}%</strong></div>
                  <div><div className="text-xs text-slate-500">Performance</div><strong>{asPercent(course.performance_percentage)}</strong></div>
                </div>
              </div>
              <div className="mt-4"><ProgressBar value={course.progress_percentage} /></div>
              <div className="mt-5 grid gap-5 lg:grid-cols-2">
                <ResultList title="Assignments" items={course.assignments} type="assignment" />
                <ResultList title="Quizzes" items={course.quizzes} type="quiz" />
              </div>
            </article>
          ))}

          {!report.courses.length && (
            <div className="card p-8 text-center text-sm text-slate-500">No enrollments found for this student.</div>
          )}
        </section>
      )}

      {!generating && !report && (
        <div className="card border-dashed p-10 text-center text-sm text-slate-500">
          Select a student and generate a report to view academic performance.
        </div>
      )}
    </div>
  );
}

function ReportSkeleton() {
  return (
    <div className="card animate-pulse space-y-4 p-5" aria-label="Generating student report">
      <div className="h-5 w-48 rounded bg-slate-200" />
      <div className="h-3 w-72 max-w-full rounded bg-slate-100" />
      <div className="h-2 rounded bg-slate-100" />
      <div className="grid gap-4 lg:grid-cols-2">
        <div className="h-32 rounded-xl bg-slate-100" />
        <div className="h-32 rounded-xl bg-slate-100" />
      </div>
    </div>
  );
}

function ResultList({ title, items, type }: { title: string; items: any[]; type: "assignment" | "quiz" }) {
  return <div><h4 className="mb-2 text-sm font-bold text-slate-800">{title}</h4>{items.length ? <div className="overflow-x-auto rounded-xl border border-(--border)"><table className="w-full text-left text-xs"><thead className="bg-slate-50 text-slate-500"><tr><th className="px-3 py-2">Item</th><th className="px-3 py-2">Status</th><th className="px-3 py-2 text-right">Result</th></tr></thead><tbody>{items.map((item) => <tr key={type === "assignment" ? item.assignment_id : item.quiz_id} className="border-t border-(--border)"><td className="px-3 py-2.5 font-medium text-slate-700">{item.title}</td><td className="px-3 py-2.5"><StatusBadge status={type === "assignment" ? item.submission_status : item.status} /></td><td className="px-3 py-2.5 text-right text-slate-600">{item.marks === null || item.marks === undefined ? "—" : `${item.marks} / ${item.max_marks}`}</td></tr>)}</tbody></table></div> : <p className="rounded-xl border border-dashed border-slate-200 p-4 text-xs text-slate-500">No {title.toLowerCase()} in this course.</p>}</div>;
}
