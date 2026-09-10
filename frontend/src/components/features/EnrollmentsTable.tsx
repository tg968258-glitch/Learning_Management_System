"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Loader2, X } from "lucide-react";
import { api } from "@/lib/api";
import { showSuccess } from "@/context/FeedbackContext";
import { DataTable, InlineError, StatusBadge, TableToolbar } from "@/components/ui";
import type { DataTableColumn } from "@/components/ui";
import { TableSkeleton } from "@/components/ui/Skeleton";

export function EnrollmentsTable({ canRemove = true }: { canRemove?: boolean }) {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("all");
  const [courseFilter, setCourseFilter] = useState("all");
  const [selectedEnrollment, setSelectedEnrollment] = useState<any | null>(null);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 6;

  const fetchEnrollments = useCallback(async () => {
    try {
      setError("");
      const data = await api.enrollments.getPage(page, pageSize, search);
      setItems(Array.isArray(data.items) ? data.items : []);
      setTotal(Number(data.total || 0));
    } catch (err) {
      console.error("Failed to load enrollments:", err);
      setItems([]);
      setError("Unable to load enrollments. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [page, search]);

  useEffect(() => {
    fetchEnrollments();
  }, [fetchEnrollments]);

  useEffect(() => {
    const handleRefresh = (event: Event) => {
      const detail = (event as CustomEvent<{ action?: string }>).detail;
      if (!detail?.action || detail.action.includes("enrollment")) {
        fetchEnrollments();
      }
    };

    window.addEventListener("learnsphere:refresh", handleRefresh);
    return () => window.removeEventListener("learnsphere:refresh", handleRefresh);
  }, [fetchEnrollments]);

  const handleUnenroll = async (enrollmentId: number) => {
    try {
      setError("");
      await api.enrollments.unenroll(enrollmentId);
      showSuccess("Enrollment removed successfully.");
      setSelectedEnrollment(null);
      fetchEnrollments();
    } catch (err: any) {
      setError(err.message || "Unable to remove enrollment.");
    }
  };

  const columns: DataTableColumn<any>[] = [
    {
      key: "student",
      header: "Student",
      render: (e) => (
        <div>
          <span className="font-semibold text-slate-900">{e.student_name || `Student #${e.student_id}`}</span>
          <span className="block text-xs text-slate-400">{e.student_email || e.student_uid || `ID: STD-${String(e.student_id).padStart(3, "0")}`}</span>
        </div>
      ),
    },
    {
      key: "course",
      header: "Course",
      render: (e) => (
        <span className="text-slate-600 font-medium">{e.course_name || `Course #${e.course_id}`}</span>
      ),
    },
    {
      key: "date",
      header: "Enrollment Date",
      render: (e) => (
        <span className="text-slate-500">
          {e.enrollment_date ? new Date(e.enrollment_date).toLocaleDateString() : "Active"}
        </span>
      ),
    },
    {
      key: "status",
      header: "Status",
      render: (e) => <StatusBadge status={e.status || "Active"} />,
    },
  ];

  if (loading) {
    return <TableSkeleton />;
  }

  return (
    <>
      {!selectedEnrollment && <InlineError message={error} className="mb-4" />}
      <div className="card overflow-hidden">
        <TableToolbar
          placeholder="Search enrollments by student or course..."
          value={search}
          onChange={(value) => { setPage(1); setSearch(value); }}
        />

        {items.length > 0 ? (
          <DataTable
            rows={items}
            columns={columns}
            rowKey={(e) => String(e.enrollment_id || `${e.student_id}-${e.course_id}`)}
            onRowClick={(e) => setSelectedEnrollment(e)}
            page={page}
            pageSize={pageSize}
            totalRows={total}
            onPageChange={setPage}
          />
        ) : (
          <div className="p-12 text-center text-sm text-slate-500">
            No enrollments found matching the criteria.
          </div>
        )}
      </div>

      {selectedEnrollment && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4 backdrop-blur-sm">
          <button
            type="button"
            className="absolute inset-0"
            onClick={() => setSelectedEnrollment(null)}
            aria-label="Close dialog"
          />

          <div className="card relative z-10 w-full max-w-lg p-6 shadow-2xl">
            <InlineError message={error} className="mb-4" />
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-xl font-bold">Enrollment Details</h2>
              <button
                type="button"
                className="icon-button"
                onClick={() => setSelectedEnrollment(null)}
                aria-label="Close dialog"
              >
                <X size={17} />
              </button>
            </div>

            <div className="mt-5 space-y-3 rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">
              <div className="flex justify-between">
                <span className="text-slate-400">Student:</span>
                <span className="font-semibold">{selectedEnrollment.student_name || `Student ${selectedEnrollment.student_id}`}</span>
              </div>
              <div className="flex justify-between gap-4">
                <span className="text-slate-400">Student account:</span>
                <span className="text-right">{selectedEnrollment.student_email || selectedEnrollment.student_uid || `STD-${selectedEnrollment.student_id}`}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Course:</span>
                <span>{selectedEnrollment.course_name || `Course ${selectedEnrollment.course_id}`}</span>
              </div>
              <div className="flex justify-between">
                <span className="text-slate-400">Status:</span>
                <span className="capitalize">{selectedEnrollment.status || "Active"}</span>
              </div>
            </div>

            <div className="mt-5 flex justify-end gap-2 border-t border-(--border) pt-4">
              <button
                type="button"
                onClick={() => setSelectedEnrollment(null)}
                className="secondary-button"
              >
                Close
              </button>
              {canRemove && (
                <button
                  type="button"
                  onClick={() => handleUnenroll(selectedEnrollment.enrollment_id)}
                  className="rounded-xl bg-rose-50 px-4 py-2 text-sm font-semibold text-rose-600 hover:bg-rose-100"
                >
                  Remove Enrollment
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
