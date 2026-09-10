"use client";

import { useCallback, useEffect, useState } from "react";
import {
  CalendarDays,
  ExternalLink,
  Loader2,
  Trash2,
  Video,
  X,
} from "lucide-react";

import { api } from "@/lib/api";
import { showSuccess } from "@/context/FeedbackContext";
import { ActionDialogButton, InlineError, StatusBadge } from "@/components/ui";
import type { Role } from "@/types/role";
import { GridSkeleton } from "@/components/ui/Skeleton";

export function SessionsGrid({ role }: { role: Role }) {
  const [sessions, setSessions] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedSession, setSelectedSession] = useState<any | null>(null);
  const [error, setError] = useState("");

  // =========================================================
  // FETCH SESSIONS
  // =========================================================

  const fetchSessions = useCallback(async () => {
    try {
      setLoading(true);
      setError("");

      const data = await api.sessions.getAll();

      setSessions(Array.isArray(data) ? data : []);
    } catch (err) {
      console.error("Failed to load sessions:", err);
      setSessions([]);
      setError("Unable to load sessions. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  // =========================================================
  // INITIAL LOAD
  // =========================================================

  useEffect(() => {
    fetchSessions();
  }, [fetchSessions]);

  // =========================================================
  // REFRESH EVENT LISTENER
  // =========================================================

  useEffect(() => {
    const handleRefresh = (event: Event) => {
      const detail = (
        event as CustomEvent<{
          action?: string;
        }>
      ).detail;

      if (
        !detail?.action ||
        detail.action.includes("session")
      ) {
        fetchSessions();
      }
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
  }, [fetchSessions]);

  // =========================================================
  // DELETE SESSION
  // =========================================================

  const handleDelete = async (
    sessionId: number,
    e?: React.MouseEvent
  ) => {
    e?.stopPropagation();

    const confirmed = window.confirm(
      "Delete this session?"
    );

    if (!confirmed) {
      return;
    }

    try {
      setError("");
      await api.sessions.delete(sessionId);

      showSuccess(
        "Session deleted successfully."
      );

      setSelectedSession(null);

      await fetchSessions();
    } catch (err: any) {
      console.error(
        "Failed to delete session:",
        err
      );

      setError(
        err?.message ||
        "Unable to delete session."
      );
    }
  };

  // =========================================================
  // OPEN SESSION
  // =========================================================

  const handleOpenSession = (
    session: any
  ) => {
    setSelectedSession(session);
  };

  // =========================================================
  // LOADING STATE
  // =========================================================

  if (loading) {
    return <GridSkeleton />;
  }

  // =========================================================
  // MAIN UI
  // =========================================================

  return (
    <>
      {!selectedSession && <InlineError message={error} className="mb-4" />}
      {sessions.length > 0 ? (
        <div className="grid gap-4 xl:grid-cols-2">
          {sessions.map((session) => (
            <div
              key={session.session_id}
              role="button"
              tabIndex={0}
              onClick={() =>
                handleOpenSession(session)
              }
              onKeyDown={(e) => {
                if (
                  e.key === "Enter" ||
                  e.key === " "
                ) {
                  e.preventDefault();

                  handleOpenSession(session);
                }
              }}
              className="card cursor-pointer p-5 text-left transition hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-lg"
            >
              <div className="flex items-start gap-4">
                {/* SESSION ICON */}

                <div className="grid h-12 w-12 shrink-0 place-items-center rounded-2xl bg-indigo-50 text-(--brand)">
                  <Video size={22} />
                </div>

                {/* SESSION DETAILS */}

                <div className="min-w-0 flex-1">
                  <div className="flex items-start justify-between gap-4">
                    <div>
                      <h3 className="font-bold text-slate-900">
                        {session.topic ||
                          "Session"}
                      </h3>

                      <p className="mt-1 text-sm text-slate-500">
                        {session.course_name ||
                          `Course #${session.course_id}`}

                        {session.teacher_name
                          ? ` • ${session.teacher_name}`
                          : ""}
                      </p>
                    </div>

                    <StatusBadge
                      status={
                        session.status ||
                        "Upcoming"
                      }
                    />
                  </div>

                  <div className="mt-4 flex flex-wrap gap-4 text-xs text-slate-500">
                    <span className="flex items-center gap-1.5">
                      <CalendarDays
                        size={14}
                      />

                      {session.session_date}
                    </span>

                    {(session.start_time ||
                      session.end_time) && (
                        <span>
                          {session.start_time ||
                            "—"}
                          {" - "}
                          {session.end_time ||
                            "—"}
                        </span>
                      )}
                  </div>
                </div>

                {/* ADMIN / TEACHER ACTIONS */}

                {role !== "student" && (
                    <div
                      className="flex shrink-0 items-center gap-1"
                      onClick={(e) =>
                        e.stopPropagation()
                      }
                      onKeyDown={(e) =>
                        e.stopPropagation()
                      }
                    >
                      <ActionDialogButton
                        action="edit-session"
                        compact
                        variant="secondary"
                        label=""
                        initialValues={{
                          sessionId: String(
                            session.session_id
                          ),
                          topic:
                            session.topic || "",
                          sessionDate:
                            session.session_date ||
                            "",
                          startTime:
                            session.start_time ||
                            "",
                          endTime:
                            session.end_time || "",
                          meetingLink:
                            session.meeting_link ||
                            "",
                          status:
                            session.status ||
                            "upcoming",
                        }}
                      />

                      <button
                        type="button"
                        className="icon-button text-rose-500"
                        onClick={(e) =>
                          handleDelete(
                            session.session_id,
                            e
                          )
                        }
                        aria-label="Delete session"
                      >
                        <Trash2 size={15} />
                      </button>
                    </div>
                  )}
              </div>
            </div>
          ))}
        </div>
      ) : (
        <div className="card p-12 text-center text-sm text-slate-500">
          {role === "student"
            ? "No class sessions available. You will see sessions after you are actively enrolled in a course."
            : "No live sessions scheduled at this time."}
        </div>
      )}

      {/* =====================================================
          SESSION DETAILS MODAL
      ====================================================== */}

      {selectedSession && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4 backdrop-blur-sm">
          {/* BACKDROP */}

          <button
            type="button"
            className="absolute inset-0"
            onClick={() =>
              setSelectedSession(null)
            }
            aria-label="Close session details"
          />

          {/* MODAL */}

          <div className="card relative z-10 w-full max-w-lg p-6 shadow-2xl">
            <InlineError message={error} className="mb-4" />
            {/* HEADER */}

            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold">
                  {selectedSession.topic ||
                    "Session Details"}
                </h2>

                <p className="mt-1 text-xs text-slate-500">
                  {
                    selectedSession.session_date
                  }

                  {selectedSession.start_time
                    ? ` • ${selectedSession.start_time}`
                    : ""}

                  {selectedSession.end_time
                    ? ` – ${selectedSession.end_time}`
                    : ""}
                </p>
              </div>

              <button
                type="button"
                className="icon-button"
                onClick={() =>
                  setSelectedSession(null)
                }
                aria-label="Close session details"
              >
                <X size={17} />
              </button>
            </div>

            {/* SESSION INFORMATION */}

            <div className="mt-5 space-y-2 rounded-2xl bg-slate-50 p-4 text-sm text-slate-700">
              <div className="flex justify-between gap-4">
                <span className="text-slate-400">
                  Status:
                </span>

                <span className="font-semibold capitalize">
                  {selectedSession.status ||
                    "Upcoming"}
                </span>
              </div>

              <div className="flex justify-between gap-4">
                <span className="text-slate-400">
                  Course:
                </span>

                <span className="text-right">
                  {selectedSession.course_name ||
                    `ID: ${selectedSession.course_id}`}
                </span>
              </div>

              <div className="flex justify-between gap-4">
                <span className="text-slate-400">
                  Instructor:
                </span>

                <span className="text-right">
                  {selectedSession.teacher_name ||
                    (selectedSession.teacher_id
                      ? `ID: ${selectedSession.teacher_id}`
                      : "—")}
                </span>
              </div>

              {selectedSession.meeting_link && (
                <div className="flex items-center justify-between gap-2">
                  <span className="shrink-0 text-slate-400">
                    Link:
                  </span>

                  <a
                    href={
                      selectedSession.meeting_link
                    }
                    target="_blank"
                    rel="noopener noreferrer"
                    className="truncate text-xs text-(--brand)"
                    onClick={(e) =>
                      e.stopPropagation()
                    }
                  >
                    {
                      selectedSession.meeting_link
                    }
                  </a>
                </div>
              )}
            </div>

            {/* ACTIONS */}

            <div className="mt-5 flex flex-wrap justify-end gap-2 border-t border-(--border) pt-4">
              {role !== "student" && (
                  <button
                    type="button"
                    onClick={(e) =>
                      handleDelete(
                        selectedSession.session_id,
                        e
                      )
                    }
                    className="secondary-button text-rose-600"
                  >
                    <Trash2 size={15} />

                    Delete
                  </button>
                )}

              {selectedSession.meeting_link && (
                <a
                  href={
                    selectedSession.meeting_link
                  }
                  target="_blank"
                  rel="noopener noreferrer"
                  className="primary-button"
                >
                  <ExternalLink size={15} />

                  Join Meeting
                </a>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
