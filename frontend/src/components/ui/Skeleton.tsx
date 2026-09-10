import type { ReactNode } from "react";

function Bone({ className = "" }: { className?: string }) {
  return <div className={`animate-pulse rounded-lg bg-slate-200/80 ${className}`} />;
}

function SkeletonRegion({ label, children }: { label: string; children: ReactNode }) {
  return (
    <div role="status" aria-label={label} aria-busy="true">
      {children}
      <span className="sr-only">{label}</span>
    </div>
  );
}

export function CardGridSkeleton({ cards = 4 }: { cards?: number }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {Array.from({ length: cards }, (_, index) => (
        <div key={index} className="card p-5">
          <div className="flex items-center justify-between">
            <Bone className="h-10 w-10 rounded-xl" />
            <Bone className="h-4 w-14" />
          </div>
          <Bone className="mt-5 h-7 w-20" />
          <Bone className="mt-2 h-4 w-28" />
        </div>
      ))}
    </div>
  );
}

export function TableSkeleton({ rows = 6 }: { rows?: number }) {
  return (
    <div className="card overflow-hidden">
      <div className="flex items-center justify-between border-b border-(--border) p-5">
        <Bone className="h-6 w-40" />
        <Bone className="h-10 w-28 rounded-xl" />
      </div>
      <div className="grid grid-cols-4 gap-4 bg-slate-50 px-5 py-3">
        {Array.from({ length: 4 }, (_, index) => <Bone key={index} className="h-3 w-20" />)}
      </div>
      {Array.from({ length: rows }, (_, row) => (
        <div key={row} className="grid grid-cols-4 gap-4 border-t border-(--border) px-5 py-4">
          <Bone className="h-4 w-4/5" />
          <Bone className="h-4 w-3/5" />
          <Bone className="h-4 w-2/3" />
          <Bone className="h-6 w-16 rounded-full" />
        </div>
      ))}
    </div>
  );
}

export function GridSkeleton({ cards = 6 }: { cards?: number }) {
  return (
    <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
      {Array.from({ length: cards }, (_, index) => (
        <div key={index} className="card p-5">
          <div className="flex gap-3">
            <Bone className="h-12 w-12 shrink-0 rounded-xl" />
            <div className="flex-1">
              <Bone className="h-5 w-3/4" />
              <Bone className="mt-2 h-3 w-1/2" />
            </div>
          </div>
          <Bone className="mt-5 h-3 w-full" />
          <Bone className="mt-2 h-3 w-5/6" />
          <div className="mt-5 flex justify-between">
            <Bone className="h-7 w-20 rounded-full" />
            <Bone className="h-9 w-24 rounded-xl" />
          </div>
        </div>
      ))}
    </div>
  );
}

export function DashboardSkeleton() {
  return (
    <SkeletonRegion label="Loading dashboard">
      <CardGridSkeleton />
      <div className="mt-5 grid gap-5 xl:grid-cols-[1.5fr_.8fr]">
        <div className="card p-5"><Bone className="h-6 w-36" /><div className="mt-5"><GridSkeleton cards={2} /></div></div>
        <div className="card p-5"><Bone className="h-6 w-40" />{Array.from({ length: 4 }, (_, i) => <Bone key={i} className="mt-4 h-12 w-full" />)}</div>
      </div>
      <div className="mt-5"><TableSkeleton rows={4} /></div>
    </SkeletonRegion>
  );
}

export function PageSkeleton({ variant = "table" }: { variant?: "table" | "grid" | "detail" | "profile" }) {
  return (
    <SkeletonRegion label="Loading page content">
      <div className="mb-6 flex items-center justify-between gap-4">
        <div><Bone className="h-8 w-52" /><Bone className="mt-2 h-4 w-72 max-w-[70vw]" /></div>
        <Bone className="h-10 w-32 rounded-xl" />
      </div>
      {variant === "table" && <TableSkeleton />}
      {variant === "grid" && <GridSkeleton />}
      {variant === "detail" && (
        <div className="grid gap-5 xl:grid-cols-[1.4fr_.8fr]">
          <div className="card p-6"><Bone className="h-8 w-2/3" /><Bone className="mt-4 h-4 w-full" /><Bone className="mt-2 h-4 w-4/5" /><Bone className="mt-7 h-40 w-full" /></div>
          <div className="card p-6"><Bone className="h-6 w-1/2" />{Array.from({ length: 5 }, (_, i) => <Bone key={i} className="mt-4 h-10 w-full" />)}</div>
        </div>
      )}
      {variant === "profile" && (
        <div className="card p-6"><div className="flex gap-5"><Bone className="h-20 w-20 rounded-full" /><div className="flex-1"><Bone className="h-7 w-48" /><Bone className="mt-3 h-4 w-64" /></div></div><div className="mt-8 grid gap-5 sm:grid-cols-2">{Array.from({ length: 6 }, (_, i) => <Bone key={i} className="h-12 w-full" />)}</div></div>
      )}
    </SkeletonRegion>
  );
}
