"use client";

import { useCallback, useEffect, useState } from "react";
import { CheckCheck, Loader2, X } from "lucide-react";
import { api } from "@/lib/api";
import { showSuccess } from "@/context/FeedbackContext";
import { InlineError } from "@/components/ui";
import { TableSkeleton } from "@/components/ui/Skeleton";

export function NotificationList() {
  const [items, setItems] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedAnnouncement, setSelectedAnnouncement] = useState<any | null>(null);
  const [error, setError] = useState("");

  const fetchNotifications = useCallback(async () => {
    try {
      setError("");
      const data = await api.notifications.getAll();
      const notifications = Array.isArray(data) ? data : [];
      setItems(notifications);
      if (notifications.some((item) => !item.is_read)) {
        setItems(notifications.map((item) => ({ ...item, is_read: true })));
        void api.notifications.markAllAsRead()
          .then(() => window.dispatchEvent(new Event("learnsphere:notifications-read")))
          .catch((err) => {
            console.error("Failed to mark notifications as read:", err);
            setError("Notifications loaded, but their read status could not be updated.");
          });
      }
    } catch (err) {
      console.error("Failed to load notifications:", err);
      setItems([]);
      setError("Unable to load notifications. Please try again.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchNotifications();
  }, [fetchNotifications]);

  const unreadCount = items.filter((item) => !item.is_read).length;

  const markAsRead = async (id: number) => {
    try {
      setError("");
      await api.notifications.markAsRead(id);
      showSuccess("Notification marked as read.");
      fetchNotifications();
    } catch (err: any) {
      setError(err.message || "Unable to update notification.");
    }
  };

  const openNotification = async (notification: any) => {
    if (!notification.is_read) await markAsRead(notification.notification_id);
    if (notification.notification_type === "announcement" && notification.announcement_id) {
      try {
        setSelectedAnnouncement(await api.announcements.getById(notification.announcement_id));
      } catch {
        setError("This announcement is no longer available.");
      }
    }
  };

  const markAllAsRead = async () => {
    try {
      setError("");
      await api.notifications.markAllAsRead();
      showSuccess("All notifications marked as read.");
      fetchNotifications();
    } catch (err: any) {
      setError(err.message || "Unable to update notifications.");
    }
  };

  if (loading) {
    return <TableSkeleton rows={5} />;
  }

  return (
    <div className="card overflow-hidden">
      <InlineError message={error} className="m-4" />
      <div className="flex items-center justify-between gap-4 border-b border-(--border) px-5 py-4">
        <div>
          <div className="font-semibold text-slate-900">Recent notifications</div>
          <div className="mt-1 text-xs text-slate-500">
            {unreadCount === 0
              ? "You are all caught up"
              : `${unreadCount} unread notification${unreadCount === 1 ? "" : "s"}`}
          </div>
        </div>

        <button
          type="button"
          onClick={markAllAsRead}
          disabled={unreadCount === 0}
          className="secondary-button disabled:cursor-not-allowed disabled:opacity-50"
        >
          <CheckCheck size={16} />
          Mark all read
        </button>
      </div>

      {items.length > 0 ? (
        <div className="divide-y divide-(--border)">
          {items.map((notification) => (
            <button
              key={notification.notification_id}
              type="button"
              onClick={() => openNotification(notification)}
              className={`flex w-full gap-4 p-5 text-left transition hover:bg-slate-50 ${
                !notification.is_read ? "bg-indigo-50/25" : "bg-white"
              }`}
            >
              <span
                className={`mt-2 h-2.5 w-2.5 shrink-0 rounded-full ${
                  !notification.is_read ? "bg-(--brand)" : "bg-slate-200"
                }`}
              />

              <span className="flex-1">
                <span className="block font-semibold text-slate-900">{notification.title || "Notification"}</span>
                <span className="mt-1 block text-sm text-slate-600">
                  {notification.message}
                </span>
                <span className="mt-2 block text-xs text-slate-400">
                  {notification.created_at ? new Date(notification.created_at).toLocaleString() : "Recent"}
                  {!notification.is_read ? " • Click to mark as read" : " • Read"}
                </span>
              </span>
            </button>
          ))}
        </div>
      ) : (
        <div className="p-12 text-center text-sm text-slate-500">
          No notifications found.
        </div>
      )}

      {selectedAnnouncement && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4 backdrop-blur-sm">
          <button type="button" className="absolute inset-0" onClick={() => setSelectedAnnouncement(null)} aria-label="Close announcement" />
          <div className="card relative z-10 w-full max-w-lg p-6 shadow-2xl" role="dialog" aria-modal="true">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="text-xs font-semibold uppercase tracking-wide text-indigo-600">Announcement</div>
                <h2 className="mt-1 text-xl font-bold">{selectedAnnouncement.title}</h2>
              </div>
              <button type="button" className="icon-button" onClick={() => setSelectedAnnouncement(null)} aria-label="Close announcement"><X size={17} /></button>
            </div>
            <p className="mt-5 whitespace-pre-wrap rounded-2xl bg-slate-50 p-4 text-sm leading-7 text-slate-600">{selectedAnnouncement.message}</p>
          </div>
        </div>
      )}
    </div>
  );
}
