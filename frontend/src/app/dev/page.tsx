import Link from "next/link";
import {
  ArrowRight,
  BookOpenCheck,
  GraduationCap,
  Presentation,
  ShieldCheck,
} from "lucide-react";

const portals = [
  {
    title: "Admin Portal",
    role: "Administrator",
    text: "Manage courses, teachers, students, enrollments and platform activity.",
    href: "/admin/dashboard",
    icon: ShieldCheck,
  },
  {
    title: "Teacher Portal",
    role: "Teacher",
    text: "Manage course content, assignments, submissions, sessions and discussions.",
    href: "/teacher/dashboard",
    icon: Presentation,
  },
  {
    title: "Student Portal",
    role: "Student",
    text: "Access learning, assignments, quizzes, sessions, progress and notifications.",
    href: "/student/dashboard",
    icon: GraduationCap,
  },
];

export default function DevPreviewPage() {
  return (
    <main className="h-dvh overflow-hidden bg-(--background) p-4">
      <div className="mx-auto flex h-full max-w-5xl flex-col justify-center">
        <div className="flex items-center justify-between gap-4">
          <Link
            href="/login"
            prefetch
            className="flex items-center gap-3"
          >
            <span className="grid h-10 w-10 place-items-center rounded-xl bg-(--brand) text-white">
              <BookOpenCheck size={20} />
            </span>

            <div>
              <div className="font-bold">
                LearnSphere
              </div>

              <div className="text-xs text-slate-500">
                Developer preview
              </div>
            </div>
          </Link>

          <Link
            href="/login"
            prefetch
            className="secondary-button"
          >
            Back to sign in
          </Link>
        </div>

        <div className="mt-8 max-w-2xl">
          <h1 className="text-3xl font-bold tracking-tight text-slate-950">
            Choose a portal to review
          </h1>

          <p className="mt-2 text-sm text-slate-500">
            Use this temporary page to preview each role before authentication is connected.
          </p>
        </div>

        <div className="mt-6 grid gap-4 md:grid-cols-3">
          {portals.map(({ title, role, text, href, icon: PortalIcon }) => (
            <Link
              href={href}
              prefetch
              key={title}
              className="card group p-5 transition hover:-translate-y-1 hover:border-indigo-200 hover:shadow-[0_18px_50px_rgba(24,32,51,.08)]"
            >
              <div className="grid h-11 w-11 place-items-center rounded-xl bg-(--brand-soft) text-(--brand)">
                <PortalIcon size={21} />
              </div>

              <div className="mt-4 text-xs font-bold uppercase tracking-[.12em] text-slate-400">
                {role}
              </div>

              <h2 className="mt-1 text-lg font-bold">
                {title}
              </h2>

              <p className="mt-2 text-sm leading-5 text-slate-500">
                {text}
              </p>

              <div className="mt-4 flex items-center gap-2 text-sm font-semibold text-(--brand)">
                Open portal
                <ArrowRight
                  size={16}
                  className="transition group-hover:translate-x-1"
                />
              </div>
            </Link>
          ))}
        </div>
      </div>
    </main>
  );
}
