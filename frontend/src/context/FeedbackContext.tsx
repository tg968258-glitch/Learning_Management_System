"use client";

import React, { createContext, useCallback, useContext, useEffect, useState } from "react";
import { CheckCircle2, Info, X } from "lucide-react";
import { getUserFacingErrorMessage } from "@/lib/userFacingError";

export type ToastType = "success" | "error" | "info";

export interface ToastItem {
  id: string;
  type: ToastType;
  message: string;
}

interface FeedbackContextType {
  showSuccess: (message: string) => void;
  showError: (message: string) => void;
  showInfo: (message: string) => void;
}

const FeedbackContext = createContext<FeedbackContextType | undefined>(undefined);

const FEEDBACK_EVENT = "learnsphere:feedback-toast";

export function showToast(type: ToastType, message: string) {
  if (typeof window === "undefined") return;
  window.dispatchEvent(
    new CustomEvent(FEEDBACK_EVENT, {
      detail: { type, message },
    })
  );
}

export function showSuccess(message: string) {
  showToast("success", message);
}

export function showError(message: string) {
  // Errors must be rendered inline by the component that owns the failed action.
  console.warn(getUserFacingErrorMessage(message));
}

export function showInfo(message: string) {
  showToast("info", message);
}

export function FeedbackProvider({ children }: { children: React.ReactNode }) {
  const [toasts, setToasts] = useState<ToastItem[]>([]);

  const addToast = useCallback((type: ToastType, message: string) => {
    if (type === "error") return;
    const id = `${Date.now()}-${Math.random().toString(36).substring(2, 9)}`;
    const newToast: ToastItem = { id, type, message };

    setToasts((current) => [...current.slice(-2), newToast]);

    const duration = 4000;
    setTimeout(() => {
      setToasts((current) => current.filter((t) => t.id !== id));
    }, duration);
  }, []);

  const removeToast = useCallback((id: string) => {
    setToasts((current) => current.filter((t) => t.id !== id));
  }, []);

  useEffect(() => {
    const handleEvent = (event: Event) => {
      const { type, message } = (event as CustomEvent<{ type: ToastType; message: string }>).detail;
      if (message && type !== "error") {
        addToast(type || "info", message);
      }
    };

    window.addEventListener(FEEDBACK_EVENT, handleEvent);
    return () => window.removeEventListener(FEEDBACK_EVENT, handleEvent);
  }, [addToast]);

  const showSuccessHandler = useCallback((msg: string) => addToast("success", msg), [addToast]);
  const showErrorHandler = useCallback(
    (msg: string) => console.warn(getUserFacingErrorMessage(msg)),
    []
  );
  const showInfoHandler = useCallback((msg: string) => addToast("info", msg), [addToast]);

  return (
    <FeedbackContext.Provider
      value={{
        showSuccess: showSuccessHandler,
        showError: showErrorHandler,
        showInfo: showInfoHandler,
      }}
    >
      {children}

      {/* Toast Overlay Container */}
      <div
        className="pointer-events-none fixed inset-x-4 bottom-4 z-[100] flex flex-col items-end gap-3 sm:inset-x-auto sm:bottom-6 sm:right-6 sm:w-[min(28rem,calc(100vw-3rem))]"
        aria-live="polite"
        aria-atomic="false"
      >
        {toasts.map((toast) => (
          <div
            key={toast.id}
            role="status"
            className={`pointer-events-auto flex w-full items-start gap-3 rounded-2xl border p-4 shadow-2xl backdrop-blur-md transition-all duration-300 ${
              toast.type === "success"
                ? "bg-emerald-950/90 text-emerald-50 border-emerald-700/50 shadow-emerald-950/20"
                : "bg-slate-900/90 text-slate-50 border-slate-700/50 shadow-slate-950/20"
            }`}
          >
            <span className="shrink-0 mt-0.5">
              {toast.type === "success" && (
                <CheckCircle2 className="text-emerald-400" size={18} />
              )}
              {toast.type === "info" && (
                <Info className="text-indigo-400" size={18} />
              )}
            </span>

            <div className="min-w-0 flex-1">
              <p className="text-sm font-semibold leading-5">
                {toast.type === "success" ? "Success" : "Information"}
              </p>
              <p className="mt-0.5 break-words text-sm leading-5 text-white/90">{toast.message}</p>
            </div>

            <button
              type="button"
              onClick={() => removeToast(toast.id)}
              className="shrink-0 text-white/60 hover:text-white transition p-0.5"
              aria-label="Dismiss notification"
            >
              <X size={15} />
            </button>
          </div>
        ))}
      </div>
    </FeedbackContext.Provider>
  );
}

export function useFeedback() {
  const context = useContext(FeedbackContext);
  if (!context) {
    return {
      showSuccess,
      showError,
      showInfo,
    };
  }
  return context;
}
