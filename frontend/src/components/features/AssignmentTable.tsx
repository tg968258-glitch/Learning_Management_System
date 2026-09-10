"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { ExternalLink, FileUp, Loader2, Send, Trash2, X } from "lucide-react";
import { api } from "@/lib/api";
import { showSuccess } from "@/context/FeedbackContext";
import {
  ActionDialogButton,
  DataTable,
  InlineError,
  StatusBadge,
  TableToolbar,
} from "@/components/ui";
import type { DataTableColumn } from "@/components/ui";
import type { Role } from "@/types/role";
import { PageSkeleton } from "@/components/ui/Skeleton";

export function AssignmentTable({
  role,
  submissions = false,
}: {
  role: Role;
  submissions?: boolean;
}) {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("all");
  const [selectedAssignment, setSelectedAssignment] = useState<any | null>(null);
  const [submissionFile, setSubmissionFile] = useState<File | null>(null);
  const [submissionText, setSubmissionText] = useState("");
  const [submitting, setSubmitting] = useState(false);
  const [studentSubmissions, setStudentSubmissions] = useState<Record<number, any>>({});
  const [submissionsList, setSubmissionsList] = useState<any[]>([]);
  const [loadingSubmissions, setLoadingSubmissions] = useState(false);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 6;

  const fetchAssignments = useCallback(async () => {
    try {
      setError("");
      const data = await api.assignments.getPage(page, pageSize, search);
      setItems(Array.isArray(data.items) ? data.items : []);
      setTotal(Number(data.total || 0));
    } catch (err) {
      console.error("Failed to load assignments:", err);
      setItems([]);
      setError("Unable to load assignments. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [page, search]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setSearch(params.get("q") ?? "");
    fetchAssignments();
  }, [fetchAssignments]);

  useEffect(() => {
    const handleRefresh = (event: Event) => {
      const detail = (event as CustomEvent<{ action?: string }>).detail;
      if (!detail?.action || detail.action.includes("assignment") || detail.action.includes("submission")) {
        fetchAssignments();
      }
    };

    window.addEventListener("learnsphere:refresh", handleRefresh);
    return () => window.removeEventListener("learnsphere:refresh", handleRefresh);
  }, [fetchAssignments]);

  const loadSubmissions = async (assignmentId: number) => {
    setLoadingSubmissions(true);
    try {
      const subs = await api.assignments.getSubmissions(assignmentId);
      setSubmissionsList(Array.isArray(subs) ? subs : []);
    } catch (err) {
      console.error("Failed to load submissions:", err);
      setSubmissionsList([]);
      setError("Unable to load submissions. Please try again.");
    } finally {
      setLoadingSubmissions(false);
    }
  };

  const handleSelectAssignment = (assignment: any) => {
    setError("");
    setSelectedAssignment(assignment);
    setSubmissionFile(null);
    setSubmissionText("");
    if (role === "student") {
      api.assignments.getMySubmission(assignment.assignment_id)
        .then((submission) => {
          setStudentSubmissions((current) => ({ ...current, [assignment.assignment_id]: submission }));
          setSubmissionText(submission.submission_text || "");
        })
        .catch(() => undefined);
    } else if (submissions) {
      loadSubmissions(assignment.assignment_id);
    }
  };

  const handleDeleteAssignment = async () => {
    if (!selectedAssignment || !window.confirm("Delete this assignment?")) return;
    try {
      setError("");
      await api.assignments.delete(selectedAssignment.assignment_id);
      showSuccess("Assignment deleted successfully.");
      setSelectedAssignment(null);
      await fetchAssignments();
    } catch (err: any) {
      setError(err.message || "Unable to delete assignment.");
    }
  };

  const handleSubmitAssignment = async (e: React.FormEvent) => {
    e.preventDefault();
    const text = submissionText.trim();
    if (!text && !submissionFile) {
      setError("Enter a text submission or choose a file.");
      return;
    }

    setSubmitting(true);
    setError("");
    try {
      const submission = submissionFile
        ? await api.assignments.submitFile(selectedAssignment.assignment_id, submissionFile, text || undefined)
        : await api.assignments.submitText(selectedAssignment.assignment_id, text);
      setStudentSubmissions((current) => ({
        ...current,
        [selectedAssignment.assignment_id]: submission,
      }));
      showSuccess(studentSubmissions[selectedAssignment.assignment_id] ? "Assignment resubmitted successfully." : "Assignment submitted successfully.");
      await fetchAssignments();
    } catch (err: any) {
      setError(err.message || "Unable to submit assignment. Please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  const columns: DataTableColumn<any>[] = [
    {
      key: "title",
      header: "Assignment Title",
      render: (a) => (
        <div>
          <span className="font-semibold text-slate-900">{a.title}</span>
          {a.description && <span className="block text-xs text-slate-400 line-clamp-1">{a.description}</span>}
        </div>
      ),
    },
    {
      key: "course",
      header: "Course",
      render: (a) => (
        <div>
          <span className="font-medium text-slate-700">{a.course_name}</span>
          <span className="block text-xs text-slate-400">Course {a.course_id}</span>
        </div>
      ),
    },
    {
      key: "due",
      header: "Due Date",
      render: (a) => (
        <span className="text-slate-500">
          {a.due_date ? new Date(a.due_date).toLocaleDateString() : "Flexible"}
        </span>
      ),
    },
    {
      key: "marks",
      header: "Max Marks",
      render: (a) => <span className="text-slate-600 font-medium">{a.max_marks ?? 100} pts</span>,
    },
    {
      key: "status",
      header: "Status",
      render: (assignment) => (
        <StatusBadge status={studentSubmissions[assignment.assignment_id]?.status || "Active"} />
      ),
    },
  ];

  if (loading) {
    return <PageSkeleton variant="table" />;
  }

  return (
    <>
      {!selectedAssignment && <InlineError message={error} className="mb-4" />}
      <div className="card overflow-hidden">
        <TableToolbar
          placeholder="Search assignments by title or course..."
          value={search}
          onChange={(value) => { setPage(1); setSearch(value); }}
        />

        {items.length > 0 ? (
          <DataTable
            rows={items}
            columns={columns}
            rowKey={(a) => String(a.assignment_id || a.title)}
            onRowClick={handleSelectAssignment}
            page={page}
            pageSize={pageSize}
            totalRows={total}
            onPageChange={setPage}
          />
        ) : (
          <div className="p-12 text-center text-sm text-slate-500">
            {role === "student"
              ? "No assignments available. You will see assignments after you are actively enrolled in a course."
              : "No assignments recorded yet."}
          </div>
        )}
      </div>

      {selectedAssignment && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4 backdrop-blur-sm">
          <button
            type="button"
            className="absolute inset-0"
            onClick={() => !submitting && setSelectedAssignment(null)}
            aria-label="Close dialog"
          />

          <div className="card relative z-10 max-h-[90vh] w-full max-w-xl overflow-y-auto p-6 shadow-2xl">
            <InlineError message={error} className="mb-4" />
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold">{selectedAssignment.title}</h2>
                <p className="mt-1 text-xs text-slate-500">
                  {selectedAssignment.course_name} · Course {selectedAssignment.course_id} · Due: {selectedAssignment.due_date ? new Date(selectedAssignment.due_date).toLocaleDateString() : "Flexible"} · Max marks: {selectedAssignment.max_marks ?? 100}
                </p>
              </div>

              <button
                type="button"
                className="icon-button"
                onClick={() => setSelectedAssignment(null)}
                disabled={submitting}
                aria-label="Close dialog"
              >
                <X size={17} />
              </button>
            </div>

            {selectedAssignment.description && (
              <div className="mt-4 rounded-xl bg-slate-50 p-4 text-sm text-slate-700 leading-6">
                {selectedAssignment.description}
              </div>
            )}

            {role === "student" ? (() => {
              const submission = studentSubmissions[selectedAssignment.assignment_id];
              const deadlinePassed = Boolean(selectedAssignment.due_date && new Date(selectedAssignment.due_date) < new Date());
              const canResubmit = submission && submission.status !== "graded" && !deadlinePassed;
              const fileUrl = submission?.submission_file?.startsWith("/")
                ? `${api.baseUrl().replace(/\/+$/, "")}${submission.submission_file}`
                : submission?.submission_file;
              return (
              <>
              {submission && (
                <div className="mt-5 rounded-xl border border-(--border) bg-slate-50 p-4 text-sm">
                  <div className="flex items-center justify-between gap-3"><span className="font-semibold">Your submission</span><StatusBadge status={submission.status} /></div>
                  <p className="mt-2 text-xs text-slate-500">Submitted: {submission.submission_date ? new Date(submission.submission_date).toLocaleString() : "—"}</p>
                  {submission.submission_text && <p className="mt-3 whitespace-pre-wrap text-slate-700">{submission.submission_text}</p>}
                  {fileUrl && <a href={fileUrl} target="_blank" rel="noreferrer" className="mt-3 inline-flex items-center gap-1 text-sm font-medium text-(--brand) hover:underline">View submitted file <ExternalLink size={14} /></a>}
                  {submission.marks !== null && submission.marks !== undefined && <p className="mt-3 font-semibold text-emerald-700">Marks: {submission.marks} / {selectedAssignment.max_marks}</p>}
                  {submission.feedback && <p className="mt-2 rounded-lg bg-white p-3 text-slate-700"><span className="font-semibold">Teacher feedback:</span> {submission.feedback}</p>}
                </div>
              )}
              <form onSubmit={handleSubmitAssignment} className="mt-5 space-y-4 border-t border-(--border) pt-4">
                <div className="font-semibold text-sm text-slate-900">{submission ? "Update / Resubmit" : "Submit Your Work"}</div>
                {submission && !canResubmit && <p className="rounded-lg bg-amber-50 p-3 text-xs text-amber-800">This submission can no longer be updated because it is graded or the deadline has passed.</p>}
                <label className="block">
                  <span className="mb-1.5 block text-xs font-semibold text-slate-500">Text Submission/Remarks</span>
                  <textarea
                    value={submissionText}
                    onChange={(e) => setSubmissionText(e.target.value)}
                    rows={4}
                    placeholder="Enter your answer or add remarks for your instructor..."
                    disabled={submitting || Boolean(submission && !canResubmit)}
                    className="w-full rounded-xl border border-(--border) bg-white px-3 py-2 text-sm outline-none focus:border-indigo-300"
                  />
                </label>

                <label className="block">
                  <span className="mb-1.5 block text-xs font-semibold text-slate-500">Choose File</span>
                  <input
                    type="file"
                    onChange={(e) => setSubmissionFile(e.target.files?.[0] || null)}
                    disabled={submitting || Boolean(submission && !canResubmit)}
                    className="w-full text-sm text-slate-500 file:mr-4 file:py-2 file:px-4 file:rounded-xl file:border-0 file:text-xs file:font-semibold file:bg-indigo-50 file:text-indigo-700 hover:file:bg-indigo-100"
                  />
                  <span className="mt-1.5 block text-xs text-slate-400">Submit text, a file, or both.</span>
                </label>

                <div className="flex justify-end gap-2 pt-2">
                  <button
                    type="button"
                    onClick={() => setSelectedAssignment(null)}
                    className="secondary-button"
                    disabled={submitting}
                  >
                    Cancel
                  </button>
                  <button
                    type="submit"
                    disabled={submitting || Boolean(submission && !canResubmit)}
                    className="primary-button"
                  >
                    {submitting ? <Loader2 size={15} className="animate-spin" /> : <Send size={15} />}
                    {submitting ? "Submitting..." : submission ? "Update Submission" : deadlinePassed ? "Submit Late" : "Submit Assignment"}
                  </button>
                </div>
              </form>
              </>
              );
            })() : submissions ? (
              <div className="mt-5 border-t border-(--border) pt-4">
                <div className="font-semibold text-sm text-slate-900 mb-3">Student Submissions</div>
                {loadingSubmissions ? (
                  <div className="space-y-3 p-4" role="status" aria-label="Loading submissions">
                    {Array.from({ length: 3 }, (_, index) => (
                      <div key={index} className="h-12 animate-pulse rounded-xl bg-slate-100" />
                    ))}
                  </div>
                ) : submissionsList.length > 0 ? (
                  <div className="space-y-2">
                    {submissionsList.map((sub: any) => (
                      <div key={sub.submission_id} className="rounded-xl bg-slate-50 p-3 text-sm flex items-center justify-between">
                        <div>
                          <div className="font-semibold">{sub.student_name || "Student"}</div>
                          <div className="text-xs font-medium text-slate-600">{selectedAssignment.title}</div>
                          <div className="text-xs text-slate-400">
                            Submitted: {sub.submission_date ? new Date(sub.submission_date).toLocaleString() : "Recent"}
                          </div>
                          {sub.submission_text && <p className="mt-2 max-w-md whitespace-pre-wrap text-xs text-slate-600">{sub.submission_text}</p>}
                          {sub.submission_file && <a href={sub.submission_file.startsWith("/") ? `${api.baseUrl().replace(/\/+$/, "")}${sub.submission_file}` : sub.submission_file} target="_blank" rel="noreferrer" className="mt-2 inline-flex items-center gap-1 text-xs font-medium text-(--brand) hover:underline">Open submitted file <ExternalLink size={13} /></a>}
                          <div className="mt-2"><StatusBadge status={sub.status} /></div>
                          {sub.marks !== null && sub.marks !== undefined && (
                            <div className="text-xs text-emerald-600 font-medium">Grade: {sub.marks} pts</div>
                          )}
                        </div>

                        <ActionDialogButton
                          action="grade-submission"
                          label="Grade"
                          variant="secondary"
                          compact
                          initialValues={{
                            submissionId: String(sub.submission_id),
                            marks: String(sub.marks ?? ""),
                            feedback: sub.feedback || "",
                          }}
                          onSuccess={() => loadSubmissions(selectedAssignment.assignment_id)}
                        />
                      </div>
                    ))}
                  </div>
                ) : (
                  <div className="rounded-xl border border-dashed border-(--border) p-6 text-center text-xs text-slate-400">
                    No submissions received for this assignment yet.
                  </div>
                )}
              </div>
            ) : (
              <div className="mt-5 border-t border-(--border) pt-4">
                <p className="text-sm text-slate-600">Manage this assignment’s details and deadline here. Student work is reviewed on the Submissions page.</p>
                <div className="mt-4 flex justify-end">
                  <ActionDialogButton action="edit-assignment" label="Edit assignment" variant="secondary" compact initialValues={{ assignmentId: String(selectedAssignment.assignment_id), title: selectedAssignment.title, description: selectedAssignment.description || "", dueDate: selectedAssignment.due_date ? new Date(selectedAssignment.due_date).toISOString().slice(0, 10) : "", maxMarks: String(selectedAssignment.max_marks ?? "") }} onSuccess={() => { setSelectedAssignment(null); fetchAssignments(); }} />
                </div>
              </div>
            )}
            {role !== "student" && submissions && (
              <div className="mt-5 flex justify-end gap-2 border-t border-(--border) pt-4">
                <button type="button" onClick={handleDeleteAssignment} className="secondary-button text-rose-600">
                  <Trash2 size={15} /> Delete
                </button>
                <ActionDialogButton
                  action="edit-assignment"
                  label="Edit assignment"
                  variant="secondary"
                  compact
                  initialValues={{
                    assignmentId: String(selectedAssignment.assignment_id),
                    title: selectedAssignment.title,
                    description: selectedAssignment.description || "",
                    dueDate: selectedAssignment.due_date ? new Date(selectedAssignment.due_date).toISOString().slice(0, 10) : "",
                    maxMarks: String(selectedAssignment.max_marks ?? ""),
                  }}
                  onSuccess={() => { setSelectedAssignment(null); fetchAssignments(); }}
                />
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
