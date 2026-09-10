import type { Role } from "@/types/role";

export type NavItem = {
  label: string;
  href: string;
  icon: string;
};

export const roleLabels: Record<Role, string> = {
  admin: "Administrator",
  teacher: "Teacher",
  student: "Student",
};

export const navigation: Record<Role, NavItem[]> = {
  admin: [
    { label: "Dashboard", href: "/admin/dashboard", icon: "LayoutDashboard" },
    { label: "Courses", href: "/admin/courses", icon: "BookOpen" },
    { label: "Teachers", href: "/admin/teachers", icon: "Presentation" },
    { label: "Students", href: "/admin/students", icon: "GraduationCap" },
    { label: "Student Reports", href: "/admin/reports", icon: "ChartNoAxesCombined" },
    { label: "Enrollments", href: "/admin/enrollments", icon: "UserRoundCheck" },
    { label: "Assignments", href: "/admin/assignments", icon: "ClipboardList" },
    { label: "Quizzes", href: "/admin/quizzes", icon: "CircleHelp" },
    { label: "Class Sessions", href: "/admin/sessions", icon: "Video" },
    { label: "Announcements", href: "/admin/announcements", icon: "Megaphone" },
    { label: "Notifications", href: "/admin/notifications", icon: "Bell" },
    { label: "Audit Logs", href: "/admin/audit-logs", icon: "ScrollText" },
  ],
  teacher: [
    { label: "Dashboard", href: "/teacher/dashboard", icon: "LayoutDashboard" },
    { label: "My Courses", href: "/teacher/courses", icon: "BookOpen" },
    { label: "Enrolled Students", href: "/teacher/enrollments", icon: "UserRoundCheck" },
    { label: "Modules & Lessons", href: "/teacher/content", icon: "LibraryBig" },
    { label: "Assignments", href: "/teacher/assignments", icon: "ClipboardList" },
    { label: "Submissions", href: "/teacher/submissions", icon: "Files" },
    { label: "Quizzes", href: "/teacher/quizzes", icon: "CircleHelp" },
    { label: "Class Sessions", href: "/teacher/sessions", icon: "Video" },
    { label: "Announcements", href: "/teacher/announcements", icon: "Megaphone" },
    { label: "Discussions", href: "/teacher/discussions", icon: "MessagesSquare" },
    { label: "Notifications", href: "/teacher/notifications", icon: "Bell" },
  ],
  student: [
    { label: "Dashboard", href: "/student/dashboard", icon: "LayoutDashboard" },
    { label: "My Courses", href: "/student/courses", icon: "BookOpen" },
    { label: "Learning", href: "/student/learning", icon: "LibraryBig" },
    { label: "Assignments", href: "/student/assignments", icon: "ClipboardList" },
    { label: "Quizzes", href: "/student/quizzes", icon: "CircleHelp" },
    { label: "Class Sessions", href: "/student/sessions", icon: "Video" },
    { label: "Progress", href: "/student/progress", icon: "ChartNoAxesCombined" },
    { label: "Discussions", href: "/student/discussions", icon: "MessagesSquare" },
    { label: "Notifications", href: "/student/notifications", icon: "Bell" },
  ],
};
