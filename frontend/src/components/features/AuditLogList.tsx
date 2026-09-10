"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { CalendarDays, ChevronLeft, ChevronRight, Loader2 } from "lucide-react";
import { api } from "@/lib/api";
import { TableSkeleton } from "@/components/ui/Skeleton";

type DateFilters = { fromDate: string; toDate: string };

const toDateInput = (date: Date) => {
  const year = date.getFullYear();
  const month = String(date.getMonth() + 1).padStart(2, "0");
  const day = String(date.getDate()).padStart(2, "0");
  return `${year}-${month}-${day}`;
};

export function AuditLogList() {
  const [logs, setLogs] = useState<any[]>([]);
  const [draft, setDraft] = useState<DateFilters>({ fromDate: "", toDate: "" });
  const [filters, setFilters] = useState<DateFilters>({ fromDate: "", toDate: "" });
  const [page, setPage] = useState(1);
  const [pageSize, setPageSize] = useState(20);
  const [total, setTotal] = useState(0);
  const [totalPages, setTotalPages] = useState(0);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState("");

  const fetchLogs = useCallback(async () => {
    try {
      setRefreshing(true);
      setError("");
      const data = await api.auditLogs.getPage({ page, pageSize, ...filters });
      setLogs(Array.isArray(data.items) ? data.items : []);
      setTotal(data.total || 0);
      setTotalPages(data.total_pages || 0);
    } catch (err) {
      console.error("Failed to load audit logs:", err);
      setLogs([]);
      setError("Unable to load audit activity. Please try again.");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [filters, page, pageSize]);

  useEffect(() => { fetchLogs(); }, [fetchLogs]);

  const applyFilters = (event: FormEvent) => {
    event.preventDefault();
    if (draft.fromDate && draft.toDate && draft.fromDate > draft.toDate) {
      setError("From Date cannot be later than To Date.");
      return;
    }
    setPage(1);
    setFilters(draft);
  };

  const applyPreset = (months: number, days: number) => {
    const to = new Date();
    const from = new Date(to);
    if (months) from.setMonth(from.getMonth() - months);
    if (days) from.setDate(from.getDate() - (days - 1));
    const next = { fromDate: toDateInput(from), toDate: toDateInput(to) };
    setDraft(next);
    setPage(1);
    setFilters(next);
  };

  const clearFilters = () => {
    const empty = { fromDate: "", toDate: "" };
    setDraft(empty);
    setPage(1);
    setFilters(empty);
  };

  const formatTime = (value?: string) => value
    ? new Date(value).toLocaleString("en-IN", {
        day: "2-digit", month: "short", year: "numeric", hour: "numeric", minute: "2-digit",
      })
    : "—";

  const formatAction = (action?: string) => ({
    created: "CREATE", updated: "UPDATE", deleted: "DELETE", submitted: "SUBMIT",
    invited: "INVITE", logged_in: "LOGIN",
  }[action || ""] || String(action || "ACTION").replaceAll("_", " ").toUpperCase());

  return (
    <div className="space-y-4">
      <form onSubmit={applyFilters} className="card p-4">
        <div className="flex flex-wrap items-end gap-3">
          <label className="min-w-44 flex-1 text-sm font-semibold text-slate-700">
            From Date
            <input type="date" value={draft.fromDate} max={draft.toDate || undefined}
              onChange={(event) => setDraft((value) => ({ ...value, fromDate: event.target.value }))}
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 font-normal outline-none focus:border-indigo-500" />
          </label>
          <label className="min-w-44 flex-1 text-sm font-semibold text-slate-700">
            To Date
            <input type="date" value={draft.toDate} min={draft.fromDate || undefined}
              onChange={(event) => setDraft((value) => ({ ...value, toDate: event.target.value }))}
              className="mt-1.5 w-full rounded-xl border border-slate-200 bg-white px-3 py-2.5 font-normal outline-none focus:border-indigo-500" />
          </label>
          <button type="button" onClick={() => applyPreset(0, 15)} className="secondary-button">
            <CalendarDays size={16} /> Last 15 Days
          </button>
          <button type="button" onClick={() => applyPreset(1, 0)} className="secondary-button">
            <CalendarDays size={16} /> Last 1 Month
          </button>
          <button type="submit" className="primary-button">Apply</button>
          {(filters.fromDate || filters.toDate) && (
            <button type="button" onClick={clearFilters} className="text-sm font-semibold text-slate-500 hover:text-slate-800">Clear</button>
          )}
        </div>
      </form>

      {loading ? <TableSkeleton /> : (
        <div className="card overflow-hidden">
          {error && <div className="bg-rose-50 px-5 py-3 text-sm text-rose-700">{error}</div>}
          {logs.length > 0 ? (
            <div className={`overflow-x-auto transition-opacity ${refreshing ? "opacity-60" : ""}`}>
              <table className="w-full min-w-[760px] text-left text-sm">
                <thead className="border-b border-(--border) bg-slate-50 text-xs uppercase tracking-wide text-slate-500">
                  <tr>
                    {["Timestamp", "User", "Role", "Action", "Resource", "Status"].map((heading) => (
                      <th key={heading} className="px-4 py-3 font-bold">{heading}</th>
                    ))}
                  </tr>
                </thead>
                <tbody className="divide-y divide-(--border)">
                  {logs.map((log, index) => (
                    <tr key={log.audit_id || index} className="hover:bg-slate-50/70">
                      <td className="whitespace-nowrap px-4 py-4 text-slate-500">{formatTime(log.created_at)}</td>
                      <td className="px-4 py-4 font-semibold text-slate-900">{log.user_name || "System"}</td>
                      <td className="px-4 py-4 capitalize text-slate-600">{log.role || "system"}</td>
                      <td className="px-4 py-4 font-bold text-indigo-700">{formatAction(log.action)}</td>
                      <td className="px-4 py-4 capitalize text-slate-700">
                        {String(log.entity_type || "resource").replaceAll("_", " ")}
                        {log.entity_id ? <span className="ml-1 text-slate-400">#{log.entity_id}</span> : null}
                      </td>
                      <td className="px-4 py-4">
                        <span className="rounded-full bg-emerald-50 px-2.5 py-1 text-xs font-bold capitalize text-emerald-700">{log.status || "success"}</span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="p-12 text-center text-sm text-slate-500">{refreshing ? "Loading audit activity…" : "No audit log entries match these filters."}</div>
          )}

          <div className="flex flex-wrap items-center justify-between gap-3 border-t border-(--border) px-4 py-3 text-sm text-slate-600">
            <div>{total.toLocaleString()} {total === 1 ? "entry" : "entries"}</div>
            <div className="flex items-center gap-3">
              <label>Rows
                <select value={pageSize} onChange={(event) => { setPage(1); setPageSize(Number(event.target.value)); }}
                  className="ml-2 rounded-lg border border-slate-200 bg-white px-2 py-1.5">
                  {[10, 20, 50, 100].map((size) => <option key={size}>{size}</option>)}
                </select>
              </label>
              <span>Page {totalPages ? page : 0} of {totalPages}</span>
              <button type="button" aria-label="Previous page" disabled={page <= 1 || refreshing}
                onClick={() => setPage((value) => value - 1)}
                className="rounded-lg border border-slate-200 p-2 disabled:opacity-40"><ChevronLeft size={16} /></button>
              <button type="button" aria-label="Next page" disabled={page >= totalPages || refreshing}
                onClick={() => setPage((value) => value + 1)}
                className="rounded-lg border border-slate-200 p-2 disabled:opacity-40">
                {refreshing ? <Loader2 size={16} className="animate-spin" /> : <ChevronRight size={16} />}
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
