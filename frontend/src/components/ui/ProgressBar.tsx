export function ProgressBar({ value }: { value: number }) {
  return (
    <div className="h-2 overflow-hidden rounded-full bg-slate-100">
      <div
        className="h-full rounded-full bg-(--brand)"
        style={{ width: `${value}%` }}
      />
    </div>
  );
}
