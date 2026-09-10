"use client";

import { useEffect, useMemo, useState, type ReactNode } from "react";
import { ChevronLeft, ChevronRight } from "lucide-react";

export type DataTableColumn<T> = {
  key: string;
  header: string;
  className?: string;
  render: (row: T) => ReactNode;
};

export function DataTable<T>({
  rows,
  columns,
  rowKey,
  onRowClick,
  emptyMessage = "No records found.",
  pageSize = 6,
  page: controlledPage,
  totalRows,
  onPageChange,
}: {
  rows: T[];
  columns: DataTableColumn<T>[];
  rowKey: (row: T) => string;
  onRowClick?: (row: T) => void;
  emptyMessage?: string;
  pageSize?: number;
  page?: number;
  totalRows?: number;
  onPageChange?: (page: number) => void;
}) {
  const [localPage, setLocalPage] = useState(1);
  const serverMode = controlledPage !== undefined && totalRows !== undefined && Boolean(onPageChange);
  const page = controlledPage ?? localPage;
  const count = totalRows ?? rows.length;
  const totalPages = Math.max(1, Math.ceil(count / pageSize));
  const setPage = (next: number | ((current: number) => number)) => {
    const value = typeof next === "function" ? next(page) : next;
    if (serverMode) onPageChange?.(value);
    else setLocalPage(value);
  };

  useEffect(() => {
    if (!serverMode) setLocalPage(1);
  }, [rows.length, serverMode]);

  useEffect(() => {
    if (page > totalPages) {
      setPage(totalPages);
    }
  }, [page, totalPages]);

  const visibleRows = useMemo(() => {
    if (serverMode) return rows;
    const start = (page - 1) * pageSize;
    return rows.slice(start, start + pageSize);
  }, [page, pageSize, rows, serverMode]);

  return (
    <>
      <div className="overflow-x-auto">
        <table className="w-full text-left text-sm">
          <thead className="bg-slate-50 text-xs uppercase tracking-wide text-slate-400">
            <tr>
              {columns.map((column) => (
                <th
                  key={column.key}
                  className={`px-5 py-3 ${column.className ?? ""}`}
                >
                  {column.header}
                </th>
              ))}
            </tr>
          </thead>

          <tbody>
            {visibleRows.map((row) => (
              <tr
                key={rowKey(row)}
                onClick={() => onRowClick?.(row)}
                className={`border-t border-(--border) ${
                  onRowClick
                    ? "cursor-pointer transition hover:bg-slate-50/80"
                    : ""
                }`}
              >
                {columns.map((column) => (
                  <td
                    key={column.key}
                    className={`px-5 py-4 ${column.className ?? ""}`}
                  >
                    {column.render(row)}
                  </td>
                ))}
              </tr>
            ))}
          </tbody>
        </table>

        {rows.length === 0 && (
          <div className="px-5 py-10 text-center text-sm text-slate-500">
            {emptyMessage}
          </div>
        )}
      </div>

      {count > pageSize && (
        <div className="flex items-center justify-between border-t border-(--border) px-5 py-3">
          <span className="text-xs text-slate-500">
            Showing {(page - 1) * pageSize + 1}-{Math.min(page * pageSize, count)} of {count}
          </span>

          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => setPage((current) => Math.max(1, current - 1))}
              disabled={page === 1}
              className="icon-button disabled:cursor-not-allowed disabled:opacity-40"
              aria-label="Previous page"
            >
              <ChevronLeft size={16} />
            </button>

            <span className="min-w-16 text-center text-xs font-semibold text-slate-600">
              {page} / {totalPages}
            </span>

            <button
              type="button"
              onClick={() => setPage((current) => Math.min(totalPages, current + 1))}
              disabled={page === totalPages}
              className="icon-button disabled:cursor-not-allowed disabled:opacity-40"
              aria-label="Next page"
            >
              <ChevronRight size={16} />
            </button>
          </div>
        </div>
      )}
    </>
  );
}
