import type { ReactNode } from "react";

export function PageHeader({
  actions,
}: {
  title: string;
  description?: string;
  actions?: ReactNode;
}) {
  if (!actions) return null;

  return (
    <div className="mb-3 flex flex-wrap items-center justify-end gap-2">
      {actions}
    </div>
  );
}
