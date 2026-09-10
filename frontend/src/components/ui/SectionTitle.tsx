import type { ReactNode } from "react";

export function SectionTitle({
  title,
  action,
}: {
  title: string;
  action?: ReactNode;
}) {
  return (
    <div className="mb-4 flex items-center justify-between gap-3">
      <h2 className="font-bold text-slate-900">
        {title}
      </h2>

      {action && (
        <div className="text-sm font-semibold text-(--brand)">
          {action}
        </div>
      )}
    </div>
  );
}
