import Link from "next/link";

export function StatCard({
  label,
  value,
  trend = "+100%",
  note = "Active in system",
  href,
}: {
  label: string;
  value: string | number;
  trend?: string;
  note?: string;
  href?: string;
}) {
  const content = (
    <>
      <div className="text-sm font-medium text-slate-500">
        {label}
      </div>

      <div className="mt-3 text-3xl font-bold tracking-tight text-slate-950">
        {value}
      </div>

      <div className="mt-3 flex items-center gap-2 text-xs">
        <span className="font-bold text-emerald-600">
          {trend}
        </span>

        <span className="text-slate-400">
          {note}
        </span>
      </div>
    </>
  );

  return href ? (
    <Link
      href={href}
      className="card block p-5 transition hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-lg focus:outline-none focus:ring-2 focus:ring-indigo-500"
      aria-label={`View ${label}`}
    >
      {content}
    </Link>
  ) : <div className="card p-5">{content}</div>;
}
