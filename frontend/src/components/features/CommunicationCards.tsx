"use client";

import { useCallback, useEffect, useState } from "react";
import { FileText, Loader2, MessageCircle, Trash2, X } from "lucide-react";
import { api, getStoredSession } from "@/lib/api";
import { showSuccess } from "@/context/FeedbackContext";
import { InlineError } from "@/components/ui";
import { GridSkeleton } from "@/components/ui/Skeleton";

export function CommunicationCards({ type }: { type: "announcements" | "discussions" }) {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedItem, setSelectedItem] = useState<any | null>(null);
  const [deleteTarget, setDeleteTarget] = useState<any | null>(null);
  const [deleting, setDeleting] = useState(false);
  const [error, setError] = useState("");
  const session = getStoredSession();
  const canDeleteAnnouncement = type === "announcements" && selectedItem && (
    session?.user?.role === "admin" || selectedItem.created_by === session?.user?.uid
  );

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    setDeleting(true);
    setError("");
    try {
      await api.announcements.delete(deleteTarget.announcement_id);
      setItems((current) => current.filter((item) => item.announcement_id !== deleteTarget.announcement_id));
      setSelectedItem(null);
      setDeleteTarget(null);
      showSuccess("Announcement deleted successfully.");
      window.dispatchEvent(new CustomEvent("learnsphere:refresh", { detail: { action: "delete-announcement" } }));
    } catch (err: any) {
      setError(err?.message || "Unable to delete announcement.");
    } finally {
      setDeleting(false);
    }
  };

  const fetchCommunications = useCallback(async () => {
    try {
      setError("");
      if (type === "announcements") {
        const data = await api.announcements.getAll();
        setItems(Array.isArray(data) ? data : []);
      } else {
        const courses = await api.courses.getAll();
        if (Array.isArray(courses)) {
          const discPromises = courses.map((c) =>
            api.discussions.getByCourse(c.course_id).catch(() => [])
          );
          const results = await Promise.all(discPromises);
          setItems(results.flat().filter(Boolean));
        } else {
          setItems([]);
        }
      }
    } catch (err) {
      console.error(`Failed to load ${type}:`, err);
      setItems([]);
      setError(`Unable to load ${type}. Please try again.`);
    } finally {
      setLoading(false);
    }
  }, [type]);

  useEffect(() => {
    fetchCommunications();
  }, [fetchCommunications]);

  useEffect(() => {
    const handleRefresh = (event: Event) => {
      const detail = (event as CustomEvent<{ action?: string }>).detail;
      if (
        !detail?.action ||
        detail.action.includes("announcement") ||
        detail.action.includes("discussion")
      ) {
        fetchCommunications();
      }
    };

    window.addEventListener("learnsphere:refresh", handleRefresh);
    return () => window.removeEventListener("learnsphere:refresh", handleRefresh);
  }, [fetchCommunications]);

  if (loading) {
    return <GridSkeleton cards={4} />;
  }

  return (
    <>
      {!selectedItem && !deleteTarget && <InlineError message={error} className="mb-4" />}
      {items.length > 0 ? (
        <div className="grid gap-4 lg:grid-cols-2">
          {items.map((item, index) => (
            <button
              key={item.announcement_id || item.discussion_id || index}
              type="button"
              onClick={() => setSelectedItem(item)}
              className="card p-5 text-left transition hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-lg"
            >
              <div className="flex items-start gap-3">
                <div className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-indigo-50 text-(--brand)">
                  {type === "discussions" ? <MessageCircle size={18} /> : <FileText size={18} />}
                </div>
                <div className="min-w-0 flex-1">
                  <h3 className="font-bold text-slate-900 truncate">{item.title || "Discussion Post"}</h3>
                  <p className="mt-2 line-clamp-2 text-sm leading-6 text-slate-500">{item.message}</p>
                  <div className="mt-3 text-xs font-medium text-slate-400">
                    Course ID: {item.course_id} • {item.created_at ? new Date(item.created_at).toLocaleDateString() : "Recent"}
                  </div>
                </div>
              </div>
            </button>
          ))}
        </div>
      ) : (
        <div className="card p-12 text-center text-sm text-slate-500">
          No {type} posted yet.
        </div>
      )}

      {selectedItem && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4 backdrop-blur-sm">
          <button
            type="button"
            className="absolute inset-0"
            onClick={() => setSelectedItem(null)}
            aria-label="Close details"
          />
          <div className="card relative z-10 w-full max-w-lg p-6 shadow-2xl">
            {!deleteTarget && <InlineError message={error} className="mb-4" />}
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold">{selectedItem.title || "Discussion Post"}</h2>
                <p className="mt-1 text-xs text-slate-500">
                  Course #{selectedItem.course_id} • {selectedItem.created_at ? new Date(selectedItem.created_at).toLocaleString() : "Recent"}
                </p>
              </div>
              <button
                type="button"
                className="icon-button"
                onClick={() => setSelectedItem(null)}
                aria-label="Close details"
              >
                <X size={17} />
              </button>
            </div>
            <p className="mt-5 text-sm leading-7 text-slate-600 rounded-2xl bg-slate-50 p-4">
              {selectedItem.message}
            </p>
            {canDeleteAnnouncement && (
              <div className="mt-5 flex justify-end border-t border-(--border) pt-4">
                <button type="button" className="rounded-xl bg-rose-50 px-4 py-2 text-sm font-semibold text-rose-600 hover:bg-rose-100" onClick={() => setDeleteTarget(selectedItem)}>
                  <Trash2 size={16} className="mr-2 inline" />Delete Announcement
                </button>
              </div>
            )}
          </div>
        </div>
      )}

      {deleteTarget && (
        <div className="fixed inset-0 z-60 grid place-items-center bg-slate-950/40 p-4 backdrop-blur-sm">
          <button type="button" className="absolute inset-0" onClick={() => !deleting && setDeleteTarget(null)} aria-label="Cancel deletion" />
          <div className="card relative z-10 w-full max-w-md p-6 shadow-2xl" role="dialog" aria-modal="true">
            <InlineError message={error} className="mb-4" />
            <h2 className="text-xl font-bold">Delete Announcement</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">Are you sure you want to delete this announcement? This action cannot be undone.</p>
            <div className="mt-6 flex justify-end gap-2 border-t border-(--border) pt-4">
              <button type="button" className="secondary-button" disabled={deleting} onClick={() => setDeleteTarget(null)}>Cancel</button>
              <button type="button" className="rounded-xl bg-rose-600 px-4 py-2 text-sm font-semibold text-white disabled:opacity-60" disabled={deleting} onClick={confirmDelete}>
                {deleting ? "Deleting..." : "Delete"}
              </button>
            </div>
          </div>
        </div>
      )}
    </>
  );
}
