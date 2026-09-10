import { AlertCircle } from "lucide-react";

export function InlineError({ message, className = "" }: { message?: string; className?: string }) {
  if (!message) return null;
  return (
    <div role="alert" className={`flex items-start gap-2 rounded-xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm leading-5 text-rose-700 ${className}`}>
      <AlertCircle className="mt-0.5 shrink-0" size={17} />
      <span>{message}</span>
    </div>
  );
}
