"use client";

import { useCallback, useEffect, useMemo, useState } from "react";
import { Loader2, X } from "lucide-react";
import { api } from "@/lib/api";
import {
  DataTable,
  InlineError,
  StatusBadge,
  TableToolbar,
} from "@/components/ui";
import type { DataTableColumn } from "@/components/ui";
import { TableSkeleton } from "@/components/ui/Skeleton";

export function PeopleTable({ kind }: { kind: "teachers" | "students" }) {
  const [data, setData] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("all");
  const [secondaryFilter, setSecondaryFilter] = useState("all");
  const [selectedPerson, setSelectedPerson] = useState<any | null>(null);
  const [error, setError] = useState("");
  const [page, setPage] = useState(1);
  const [total, setTotal] = useState(0);
  const pageSize = 6;

  const fetchPeople = useCallback(async () => {
    try {
      setError("");
      const result = kind === "teachers"
        ? await api.teachers.getPage(page, pageSize, search)
        : await api.students.getPage(page, pageSize, search);
      setData(Array.isArray(result.items) ? result.items : []);
      setTotal(Number(result.total || 0));
    } catch (err) {
      console.error(`Failed to load ${kind}:`, err);
      setData([]);
      setError(`Unable to load ${kind}. Please try again.`);
    } finally {
      setLoading(false);
    }
  }, [kind, page, search]);

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    setSearch(params.get("q") ?? "");
    fetchPeople();
  }, [fetchPeople]);

  useEffect(() => {
    const handleRefresh = (event: Event) => {
      const detail = (event as CustomEvent<{ action?: string }>).detail;
      if (
        !detail?.action ||
        detail.action.includes("teacher") ||
        detail.action.includes("student") ||
        detail.action.includes("person")
      ) {
        fetchPeople();
      }
    };

    window.addEventListener("learnsphere:refresh", handleRefresh);
    return () => window.removeEventListener("learnsphere:refresh", handleRefresh);
  }, [fetchPeople]);

  const secondaryOptions = useMemo(() => {
    if (kind === "teachers") {
      return Array.from(
        new Set(
          data.map((t) => t.specialization).filter(Boolean)
        )
      );
    }
    return [];
  }, [data, kind]);

  const filteredPeople = useMemo(() => {
    const query = search.trim().toLowerCase();

    return data.filter((person) => {
      const name = person.name || "";
      const email = person.email || "";
      const uid = person.uid || "";
      const matchesSearch =
        !query ||
        [name, email, uid, person.specialization || ""].some((val) =>
          String(val).toLowerCase().includes(query)
        );

      const matchesSecondary =
        secondaryFilter === "all" ||
        person.specialization === secondaryFilter;

      return matchesSearch && matchesSecondary;
    });
  }, [data, search, secondaryFilter]);

  const columns: DataTableColumn<any>[] = useMemo(() => {
    if (kind === "teachers") {
      return [
        {
          key: "name",
          header: "Teacher Name",
          render: (t) => (
            <div>
              <div className="font-semibold text-slate-900">{t.name}</div>
              <div className="text-xs text-slate-400">{t.email || `UID: ${t.uid}`}</div>
            </div>
          ),
        },
        {
          key: "specialization",
          header: "Specialization",
          render: (t) => <span className="text-slate-600">{t.specialization || "General"}</span>,
        },
        {
          key: "qualification",
          header: "Qualification",
          render: (t) => <span className="text-slate-500">{t.qualification || "M.Tech"}</span>,
        },
        {
          key: "experience",
          header: "Experience",
          render: (t) => <span className="text-slate-500">{t.experience ? `${t.experience} yrs` : "N/A"}</span>,
        },
        {
          key: "status",
          header: "Course Assignment",
          render: (t) => (
            <StatusBadge
              status={t.is_invitation ? t.invitation_status : (t.assignment_status || "Awaiting Course Assignment")}
            />
          ),
        },
      ];
    }

    return [
      {
        key: "name",
        header: "Student Name",
        render: (s) => (
          <div>
            <div className="font-semibold text-slate-900">{s.name}</div>
            <div className="text-xs text-slate-400">{s.email || `ID: ${s.student_id}`}</div>
          </div>
        ),
      },
      {
        key: "id",
        header: "Student ID",
        render: (s) => <span className="text-slate-500">STD-{String(s.student_id).padStart(3, "0")}</span>,
      },
      {
        key: "phone",
        header: "Phone",
        render: (s) => <span className="text-slate-500">{s.phone_number || "Not provided"}</span>,
      },
      {
        key: "gender",
        header: "Gender",
        render: (s) => <span className="text-slate-500">{s.gender || "Unspecified"}</span>,
      },
      {
        key: "status",
        header: "Status",
        render: () => <StatusBadge status="Active" />,
      },
    ];
  }, [kind]);

  if (loading) {
    return <TableSkeleton />;
  }

  return (
    <>
      <InlineError message={error} className="mb-4" />
      <div className="card overflow-hidden">
        <TableToolbar
          placeholder={`Search ${kind} by name or email...`}
          value={search}
          onChange={(value) => { setPage(1); setSearch(value); }}
        />

        {filteredPeople.length > 0 ? (
          <DataTable
            rows={filteredPeople}
            columns={columns}
            rowKey={(p) => String(p.teacher_id || p.student_id || p.uid)}
            onRowClick={(person) => setSelectedPerson(person)}
            page={page}
            pageSize={pageSize}
            totalRows={total}
            onPageChange={setPage}
          />
        ) : (
          <div className="p-12 text-center text-sm text-slate-500">
            No {kind} found matching your query.
          </div>
        )}
      </div>

      {selectedPerson && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4 backdrop-blur-sm">
          <button
            type="button"
            className="absolute inset-0"
            onClick={() => setSelectedPerson(null)}
            aria-label="Close details"
          />

          <div className="card relative z-10 w-full max-w-lg p-6 shadow-2xl">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold">{selectedPerson.name}</h2>
                <p className="mt-1 text-xs text-slate-500">{selectedPerson.email || selectedPerson.uid}</p>
              </div>

              <button
                type="button"
                className="icon-button"
                onClick={() => setSelectedPerson(null)}
                aria-label="Close details"
              >
                <X size={17} />
              </button>
            </div>

            <div className="mt-5 space-y-3 rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">
              <div className="flex justify-between">
                <span className="text-slate-400">ID:</span>
                <span className="font-semibold">
                  {selectedPerson.teacher_id
                    ? `TCH-${selectedPerson.teacher_id}`
                    : `STD-${String(selectedPerson.student_id).padStart(3, "0")}`}
                </span>
              </div>
              <div className="flex justify-between gap-4">
                <span className="text-slate-400">Account UID:</span>
                <span className="max-w-[65%] truncate font-mono text-xs" title={selectedPerson.uid}>
                  {selectedPerson.uid || "Unavailable"}
                </span>
              </div>
              {selectedPerson.specialization && (
                <div className="flex justify-between">
                  <span className="text-slate-400">Specialization:</span>
                  <span>{selectedPerson.specialization}</span>
                </div>
              )}
              {selectedPerson.qualification && (
                <div className="flex justify-between">
                  <span className="text-slate-400">Qualification:</span>
                  <span>{selectedPerson.qualification}</span>
                </div>
              )}
              {selectedPerson.phone_number && (
                <div className="flex justify-between">
                  <span className="text-slate-400">Phone:</span>
                  <span>{selectedPerson.phone_number}</span>
                </div>
              )}
            </div>

          </div>
        </div>
      )}
    </>
  );
}
