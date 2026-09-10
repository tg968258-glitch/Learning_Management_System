export type FrontendActionDetail = {
  action: string;
  values: Record<string, string>;
  persisted?: boolean;
};

export const FRONTEND_ACTION_EVENT = "learnsphere:frontend-action";
export const PERSISTENT_STATE_EVENT = "learnsphere:local-state";

export function emitFrontendAction(
  action: string,
  values: Record<string, string>,
  persisted = false,
) {
  window.dispatchEvent(
    new CustomEvent<FrontendActionDetail>(FRONTEND_ACTION_EVENT, {
      detail: { action, values, persisted },
    }),
  );
}

export function readFrontendState<T>(key: string, fallback: T): T {
  try {
    const saved = window.localStorage.getItem(key);
    return saved ? (JSON.parse(saved) as T) : fallback;
  } catch {
    return fallback;
  }
}

export function writeFrontendState<T>(key: string, value: T) {
  try {
    window.localStorage.setItem(key, JSON.stringify(value));
    window.dispatchEvent(
      new CustomEvent(PERSISTENT_STATE_EVENT, {
        detail: { key, value },
      }),
    );
  } catch {
    // Keep the UI usable even when browser storage is unavailable.
  }
}
