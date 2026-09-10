"use client";

import { useCallback, useEffect, useState } from "react";
import { PERSISTENT_STATE_EVENT } from "./frontendEvents";

type LocalStateDetail<T> = {
  key: string;
  value: T;
};

export function usePersistentState<T>(key: string, initialValue: T) {
  const [value, setValueState] = useState<T>(initialValue);

  useEffect(() => {
    try {
      const saved = window.localStorage.getItem(key);
      if (saved) {
        setValueState(JSON.parse(saved) as T);
      }
    } catch {
      // Keep mock data if browser storage is unavailable.
    }
  }, [key]);

  useEffect(() => {
    const sync = (event: Event) => {
      const detail = (event as CustomEvent<LocalStateDetail<T>>).detail;
      if (detail.key === key) {
        setValueState(detail.value);
      }
    };

    window.addEventListener(PERSISTENT_STATE_EVENT, sync);
    return () => window.removeEventListener(PERSISTENT_STATE_EVENT, sync);
  }, [key]);

  const setValue = useCallback(
    (next: T | ((current: T) => T)) => {
      setValueState((current) => {
        const resolved =
          typeof next === "function"
            ? (next as (current: T) => T)(current)
            : next;

        queueMicrotask(() => {
          try {
            window.localStorage.setItem(key, JSON.stringify(resolved));
            window.dispatchEvent(
              new CustomEvent<LocalStateDetail<T>>(PERSISTENT_STATE_EVENT, {
                detail: { key, value: resolved },
              }),
            );
          } catch {
            // UI still updates in memory.
          }
        });

        return resolved;
      });
    },
    [key],
  );

  return [value, setValue] as const;
}
