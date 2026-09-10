import { getUserFacingErrorMessage } from "@/lib/userFacingError";

const getBaseUrl = () => {
  if (typeof window !== "undefined") {
    return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
  }
  return process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
};

export interface AuthUser {
  uid: string;
  email: string;
  role: "admin" | "teacher" | "student" | string;
  name?: string;
}

export interface StoredSession {
  token: string;
  refreshToken?: string;
  sessionId?: string;
  user: AuthUser;
}

export interface AdminDashboardStats {
  total_courses: number;
  total_students: number;
  active_instructors: number;
  active_enrollments: number;
}

export interface TeacherDashboardStats {
  active_courses: number;
  total_students: number;
  assignments: number;
  live_sessions: number;
}

export interface StudentDashboardStats {
  enrolled_courses: number;
  completed_lessons: number;
  assignments: number;
  upcoming_sessions: number;
}

let refreshPromise: Promise<string | null> | null = null;

export function getStoredSession(): StoredSession | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = window.localStorage.getItem("learnsphere_auth_session");
    if (!raw) return null;
    return JSON.parse(raw);
  } catch {
    return null;
  }
}

export function setStoredSession(session: StoredSession) {
  if (typeof window === "undefined") return;
  window.localStorage.setItem("learnsphere_auth_session", JSON.stringify(session));
}

export function clearStoredSession() {
  if (typeof window === "undefined") return;
  window.localStorage.removeItem("learnsphere_auth_session");
}

function redirectToLogin() {
  clearStoredSession();
  if (typeof window !== "undefined" && window.location.pathname !== "/login") {
    window.location.replace("/login?reason=session-expired");
  }
}

async function refreshAccessToken(baseUrl: string, session: StoredSession): Promise<string | null> {
  if (!session.refreshToken) return null;

  if (!refreshPromise) {
    refreshPromise = fetch(`${baseUrl.replace(/\/+$/, "")}/auth/refresh`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ refresh_token: session.refreshToken }),
    })
      .then(async (response) => {
        if (!response.ok) return null;
        const data = await response.json();
        const token = data.access_token as string | undefined;
        if (!token) return null;
        setStoredSession({ ...session, token });
        return token;
      })
      .catch(() => null)
      .finally(() => {
        refreshPromise = null;
      });
  }

  return refreshPromise;
}

async function request<T = any>(
  endpoint: string,
  options: RequestInit = {},
  retryAfterRefresh = true
): Promise<T> {
  const baseUrl = getBaseUrl();
  const session = getStoredSession();

  const headers: Record<string, string> = {
    ...(options.headers as Record<string, string>),
  };

  if (session?.token && !headers["Authorization"]) {
    headers["Authorization"] = `Bearer ${session.token}`;
  }

  if (!(options.body instanceof FormData) && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const url = `${baseUrl.replace(/\/+$/, "")}/${endpoint.replace(/^\/+/, "")}`;

  let response: Response;
  try {
    response = await fetch(url, {
      ...options,
      headers,
    });
  } catch (error) {
    // Do not emit the browser's raw TypeError through console.error: Next.js
    // treats it as an application error overlay even when callers handle it.
    // Keep only a concise diagnostic without exposing the stack to users.
    console.warn(`LMS request could not reach ${url}`);
    throw new Error(getUserFacingErrorMessage(error));
  }

  if (response.status === 401 && session?.token && retryAfterRefresh && !endpoint.startsWith("/auth/")) {
    const newToken = await refreshAccessToken(baseUrl, session);
    if (newToken) {
      return request<T>(endpoint, {
        ...options,
        headers: { ...headers, Authorization: `Bearer ${newToken}` },
      }, false);
    }
    redirectToLogin();
  }

  if (!response.ok) {
    let errorDetail = "An unexpected error occurred. Please try again.";
    try {
      const errorJson = await response.json();
      if (typeof errorJson.detail === "string") {
        errorDetail = errorJson.detail;
      } else if (Array.isArray(errorJson.detail)) {
        errorDetail = errorJson.detail
          .map((err: any) => (err.msg ? `${err.loc ? err.loc.slice(-1)[0] + ": " : ""}${err.msg}` : JSON.stringify(err)))
          .join(". ");
      } else if (errorJson.message) {
        errorDetail = errorJson.message;
      }
    } catch {
      if (response.status === 401) {
        errorDetail = "Invalid credentials or session expired. Please sign in again.";
      } else if (response.status === 403) {
        errorDetail = "You do not have permission to perform this action.";
      } else if (response.status === 404) {
        errorDetail = "The requested item was not found.";
      } else if (response.status >= 500) {
        errorDetail = "A server error occurred. Please try again later.";
      }
    }
    if (response.status !== 401) {
      console.error(`API Error [${response.status}] on ${url}:`, errorDetail);
    }
    throw new Error(getUserFacingErrorMessage(errorDetail, undefined, response.status));
  }

  if (response.status === 204) {
    return {} as T;
  }

  const contentType = response.headers.get("content-type");
  if (contentType && contentType.includes("application/json")) {
    return response.json();
  }

  return response.text() as unknown as T;
}

export const api = {
  baseUrl: getBaseUrl,

  auth: {
    login: async (credentials: { username?: string; email?: string; password: string }) => {
      const payload = {
        email: credentials.email || credentials.username,
        password: credentials.password,
      };
      const res = await request<any>("/auth/login", {
        method: "POST",
        body: JSON.stringify(payload),
      });

      const token = res.access_token || res.token;
      const user: AuthUser = {
        uid: res.uid || res.user?.uid || "",
        email: res.email || res.user?.email || payload.email || "",
        role: (res.role || res.user?.role || "student").toLowerCase(),
        name: res.name || res.user?.name,
      };

      const refreshToken = res.refresh_token;
      const sessionId = res.session_id;
      setStoredSession({ token, refreshToken, sessionId, user });
      return { token, refreshToken, sessionId, user };
    },

    register: async (data: { username: string; email: string; password: string; name: string; role?: string }) => {
      return request<any>("/auth/register", {
        method: "POST",
        body: JSON.stringify({
          username: data.username,
          email: data.email,
          password: data.password,
          name: data.name,
          role: (data.role || "student").toLowerCase(),
        }),
      });
    },

    forgotPassword: async (email: string) => {
      return request<any>("/auth/forgot-password", {
        method: "POST",
        body: JSON.stringify({ email }),
      });
    },

    resetPassword: async (data: { email: string; otp: string; new_password: string }) => {
      return request<any>("/auth/reset-password", {
        method: "POST",
        body: JSON.stringify(data),
      });
    },

    inviteTeacher: async (email: string) => {
      return request<any>("/admin/invite-teacher", {
        method: "POST",
        body: JSON.stringify({ email }),
      });
    },

    getInvitationDetails: async (token: string) => {
      return request<{ email: string; expires_at: string; is_valid: boolean }>(
        `/auth/invitation-details?token=${encodeURIComponent(token)}`
      );
    },

    acceptTeacherInvite: async (data: {
      token: string;
      password: string;
      name: string;
      phone_number?: string;
      username?: string;
      specialization?: string;
      qualification?: string;
      experience?: number;
    }) => {
      return request<any>("/auth/accept-teacher-invite", {
        method: "POST",
        body: JSON.stringify(data),
      });
    },
  },

  admin: {
    getTeacherInvitations: () => request<any[]>("/admin/teacher-invitations"),
    getDashboardStats: () => request<AdminDashboardStats>("/admin/dashboard/stats"),
  },

  dashboard: {
    getTeacherStats: () => request<TeacherDashboardStats>("/teacher/dashboard/stats"),
    getStudentStats: () => request<StudentDashboardStats>("/student/dashboard/stats"),
  },

  reports: {
    getAll: (studentId?: number) => request<any[]>(studentId ? `/reports/?student_id=${studentId}` : "/reports/"),
    getMine: () => request<any[]>("/reports/"),
    searchStudents: (query: string) =>
      request<Array<{ student_id: number; student_name: string }>>(
        `/reports/students/search?query=${encodeURIComponent(query)}&limit=10`
      ),
    generateStudent: (studentId: number) =>
      request<any>(`/reports/students/${studentId}`),
  },

  users: {
    getMe: () => request<any>("/auth/me"),
    updateMe: (data: any) => request<any>("/users/me", { method: "PUT", body: JSON.stringify(data) }),
    getAll: (role?: string) => request<any[]>(role ? `/users/?role=${encodeURIComponent(role)}` : "/users/"),
    create: (data: any) => request<any>("/users/", { method: "POST", body: JSON.stringify(data) }),
    update: (uid: string, data: any) => request<any>(`/users/${uid}`, { method: "PUT", body: JSON.stringify(data) }),
    delete: (uid: string) => request<any>(`/users/${uid}`, { method: "DELETE" }),
  },

  students: {
    getAll: () => request<any[]>("/students/"),
    getPage: (page = 1, pageSize = 6, search = "") =>
      request<any>(`/students/page?page=${page}&page_size=${pageSize}&search=${encodeURIComponent(search)}`),
    getMe: () => request<any>("/students/me"),
    getById: (id: number) => request<any>(`/students/${id}`),
    updateMe: (data: any) => request<any>("/students/me", { method: "PUT", body: JSON.stringify(data) }),
    update: (id: number, data: any) => request<any>(`/students/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    delete: (id: number) => request<any>(`/students/${id}`, { method: "DELETE" }),
  },

  teachers: {
    getAll: () => request<any[]>("/teachers/"),
    getPage: (page = 1, pageSize = 6, search = "", specialization = "") => {
      const params = new URLSearchParams({ page: String(page), page_size: String(pageSize), search });
      if (specialization) params.set("specialization", specialization);
      return request<any>(`/teachers/page?${params.toString()}`);
    },
    getMe: () => request<any>("/teachers/me"),
    getById: (id: number) => request<any>(`/teachers/${id}`),
    updateMe: (data: any) => request<any>("/teachers/me", { method: "PUT", body: JSON.stringify(data) }),
    update: (id: number, data: any) => request<any>(`/teachers/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    delete: (id: number) => request<any>(`/teachers/${id}`, { method: "DELETE" }),
  },

  courses: {
    getAll: () => request<any[]>("/courses/"),
    getMyCourses: () => request<any[]>("/courses/my-courses"),
    getById: (id: number) => request<any>(`/courses/${id}`),
    create: (data: { course_name: string; category?: string; description?: string; status?: string }) =>
      request<any>("/courses/", { method: "POST", body: JSON.stringify(data) }),
    update: (id: number, data: any) => request<any>(`/courses/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    delete: (id: number) => request<any>(`/courses/${id}`, { method: "DELETE" }),
    assignTeacher: (courseId: number, teacherId: number) =>
      request<any>(`/courses/${courseId}/teachers`, { method: "POST", body: JSON.stringify({ teacher_ids: [teacherId] }) }),
    removeTeacher: (courseId: number, teacherId: number) =>
      request<any>(`/courses/${courseId}/teachers/${teacherId}`, { method: "DELETE" }),
  },

  enrollments: {
    getAll: (courseId?: number) =>
      courseId ? request<any[]>(`/enrollments/course/${courseId}`) : request<any[]>("/enrollments/"),
    getPage: (page = 1, pageSize = 6, search = "", courseId?: number) => {
      const params = new URLSearchParams({ page: String(page), page_size: String(pageSize), search });
      if (courseId) params.set("course_id", String(courseId));
      return request<any>(`/enrollments/page?${params.toString()}`);
    },
    getMyEnrollments: () => request<any[]>("/enrollments/my-enrollments"),
    enroll: (courseId: number) =>
      request<any>("/enrollments/", { method: "POST", body: JSON.stringify({ course_id: courseId }) }),
    unenroll: (enrollmentId: number) => request<any>(`/enrollments/${enrollmentId}`, { method: "DELETE" }),
  },

  modules: {
    getByCourse: (courseId: number) => request<any[]>(`/modules/course/${courseId}`),
    create: (data: { course_id: number; module_name: string; description?: string; is_published?: boolean }) =>
      request<any>("/modules/", { method: "POST", body: JSON.stringify(data) }),
    update: (id: number, data: any) => request<any>(`/modules/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    delete: (id: number) => request<any>(`/modules/${id}`, { method: "DELETE" }),
  },

  lessons: {
    getByModule: (moduleId: number) => request<any[]>(`/lessons/module/${moduleId}`),
    getById: (id: number) => request<any>(`/lessons/${id}`),
    create: (data: { module_id: number; lesson_title: string; is_published?: boolean; sequence_order?: number }) =>
      request<any>("/lessons/", { method: "POST", body: JSON.stringify(data) }),
    update: (id: number, data: any) => request<any>(`/lessons/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    delete: (id: number) => request<any>(`/lessons/${id}`, { method: "DELETE" }),
    addContent: (lessonId: number, data: { content_type: string; content: string; sequence_number?: number }) =>
      request<any>("/lessons/contents/", {
        method: "POST",
        body: JSON.stringify({ lesson_id: lessonId, ...data }),
      }),
    updateContent: (contentId: number, data: { content_type?: string; content?: string; sequence_number?: number }) =>
      request<any>(`/lessons/contents/${contentId}`, { method: "PUT", body: JSON.stringify(data) }),
    deleteContent: (contentId: number) =>
      request<any>(`/lessons/contents/${contentId}`, { method: "DELETE" }),
    addResourceLink: (lessonId: number, data: { resource_name: string; resource_type: string; resource_url: string }) =>
      request<any>("/lessons/resources/", {
        method: "POST",
        body: JSON.stringify({ lesson_id: lessonId, ...data }),
      }),
    uploadResource: async (lessonId: number, file: File, resourceName: string, resourceType = "file") => {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("resource_name", resourceName);
      formData.append("resource_type", resourceType);
      return request<any>(`/lessons/${lessonId}/resources/upload`, {
        method: "POST",
        body: formData,
      });
    },
    updateResource: (resourceId: number, data: { resource_name?: string; resource_type?: string; resource_url?: string }) =>
      request<any>(`/lessons/resources/${resourceId}`, { method: "PUT", body: JSON.stringify(data) }),
    replaceResourceFile: (resourceId: number, file: File, resourceName?: string, resourceType?: string) => {
      const formData = new FormData();
      formData.append("file", file);
      if (resourceName) formData.append("resource_name", resourceName);
      if (resourceType) formData.append("resource_type", resourceType);
      return request<any>(`/lessons/resources/${resourceId}/file`, { method: "PUT", body: formData });
    },
    deleteResource: (resourceId: number) =>
      request<any>(`/lessons/resources/${resourceId}`, { method: "DELETE" }),
  },

  assignments: {
    getAll: (courseId?: number, moduleId?: number) => {
      const params = new URLSearchParams();
      if (courseId) params.append("course_id", String(courseId));
      if (moduleId) params.append("module_id", String(moduleId));
      const query = params.toString() ? `?${params.toString()}` : "";
      return request<any[]>(`/assignments/${query}`);
    },
    getPage: (page = 1, pageSize = 6, search = "") =>
      request<any>(`/assignments/page?page=${page}&page_size=${pageSize}&search=${encodeURIComponent(search)}`),
    getById: (id: number) => request<any>(`/assignments/${id}`),
    create: (data: {
      course_id: number;
      module_id: number;
      title: string;
      description?: string;
      max_marks: number;
      passing_marks: number;
      due_date: string;
    }) => request<any>("/assignments/", { method: "POST", body: JSON.stringify(data) }),
    update: (id: number, data: any) => request<any>(`/assignments/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    delete: (id: number) => request<any>(`/assignments/${id}`, { method: "DELETE" }),
    submitText: (assignmentId: number, submissionText: string) =>
      request<any>(`/assignments/${assignmentId}/submit`, {
        method: "POST",
        body: JSON.stringify({ submission_text: submissionText }),
      }),
    submitFile: async (assignmentId: number, file: File, submissionText?: string) => {
      const formData = new FormData();
      formData.append("file", file);
      if (submissionText) formData.append("submission_text", submissionText);
      return request<any>(`/assignments/${assignmentId}/submit-file`, {
        method: "POST",
        body: formData,
      });
    },
    getSubmissions: (assignmentId: number) => request<any[]>(`/assignments/${assignmentId}/submissions`),
    getMySubmission: (assignmentId: number) => request<any>(`/assignments/${assignmentId}/my-submission`),
    gradeSubmission: (submissionId: number, data: { marks: number; feedback?: string }) =>
      request<any>(`/assignments/submissions/${submissionId}/grade`, {
        method: "POST",
        body: JSON.stringify(data),
      }),
  },

  quizzes: {
    getByCourse: (courseId: number) => request<any[]>(`/quizzes/course/${courseId}`),
    getByLesson: (lessonId: number) => request<any[]>(`/quizzes/lesson/${lessonId}`),
    getById: (id: number) => request<any>(`/quizzes/${id}`),
    create: (data: {
      course_id: number;
      title: string;
      description?: string;
      max_marks?: number;
      passing_marks?: number;
      duration_minutes?: number;
      max_attempts?: number;
      is_published?: boolean;
    }) => request<any>("/quizzes/", { method: "POST", body: JSON.stringify(data) }),
    update: (id: number, data: any) => request<any>(`/quizzes/${id}`, { method: "PUT", body: JSON.stringify(data) }),
    delete: (id: number) => request<any>(`/quizzes/${id}`, { method: "DELETE" }),
    addQuestion: (
      quizId: number,
      data: {
        question_text: string;
        question_type?: string;
        marks?: number;
        options: Array<{ option_text: string; is_correct: boolean }>;
      }
    ) => request<any>(`/quizzes/${quizId}/questions`, { method: "POST", body: JSON.stringify(data) }),
    startAttempt: (quizId: number) => request<any>(`/quizzes/${quizId}/start`, { method: "POST" }),
    submitAttempt: (
      attemptId: number,
      answers: Array<{ question_id: number; selected_option_id: number }>
    ) =>
      request<any>(`/quizzes/attempts/${attemptId}/submit`, {
        method: "POST",
        body: JSON.stringify({ answers }),
      }),
    getMyAttempts: (quizId: number) => request<any[]>(`/quizzes/${quizId}/my-attempts`),
  },

  sessions: {
    getAll: (courseId?: number) =>
      request<any[]>(courseId ? `/sessions/?course_id=${courseId}` : "/sessions/"),
    getById: (id: number) => request<any>(`/sessions/${id}`),
    getByCourse: (courseId: number) => request<any[]>(`/sessions/course/${courseId}`),
    create: (data: {
      course_id: number;
      teacher_id?: number;
      topic?: string;
      session_title?: string;
      session_date: string;
      start_time?: string;
      end_time?: string;
      meeting_link?: string;
      status?: string;
    }) =>
      request<any>("/sessions/", {
        method: "POST",
        body: JSON.stringify({
          course_id: data.course_id,
          teacher_id: data.teacher_id,
          topic: data.topic || data.session_title,
          session_date: data.session_date,
          start_time: data.start_time,
          end_time: data.end_time,
          meeting_link: data.meeting_link,
        }),
      }),
    update: (id: number, data: any) =>
      request<any>(`/sessions/${id}`, {
        method: "PUT",
        body: JSON.stringify({
          ...data,
          topic: data.topic || data.session_title,
        }),
      }),
    delete: (id: number) => request<any>(`/sessions/${id}`, { method: "DELETE" }),
  },

  discussions: {
    getByCourse: (courseId: number) => request<any[]>(`/discussions/course/${courseId}`),
    create: (data: { course_id: number; message: string; parent_id?: number | null }) =>
      request<any>("/discussions/", { method: "POST", body: JSON.stringify(data) }),
    delete: (id: number) => request<any>(`/discussions/${id}`, { method: "DELETE" }),
  },

  announcements: {
    getAll: (courseId?: number) =>
      request<any[]>(courseId ? `/announcements/?course_id=${courseId}` : "/announcements/"),
    getById: (id: number) => request<any>(`/announcements/${id}`),
    create: (data: { course_id?: number; audience: "students_only" | "course_students"; title: string; message: string }) =>
      request<any>("/announcements/", { method: "POST", body: JSON.stringify(data) }),
    delete: (id: number) => request<any>(`/announcements/${id}`, { method: "DELETE" }),
  },

  notifications: {
    getAll: () => request<any[]>("/notifications/my-notifications"),
    getUnreadCount: () => request<{ count: number }>("/notifications/unread-count"),
    markAsRead: (id: number) => request<any>(`/notifications/${id}/read`, { method: "PUT" }),
    markAllAsRead: () => request<any>("/notifications/read-all", { method: "PUT" }),
    getUnread: () => request<any[]>("/notifications/my-notifications?unread_only=true"),
  },

  auditLogs: {
    getPage: (filters: {
      page?: number;
      pageSize?: number;
      fromDate?: string;
      toDate?: string;
    } = {}) => {
      const params = new URLSearchParams({
        page: String(filters.page ?? 1),
        page_size: String(filters.pageSize ?? 20),
      });
      if (filters.fromDate) params.set("from_date", filters.fromDate);
      if (filters.toDate) params.set("to_date", filters.toDate);
      return request<{
        items: any[];
        page: number;
        page_size: number;
        total: number;
        total_pages: number;
      }>(`/audit-logs/?${params.toString()}`);
    },
  },

  progress: {
    getMyProgress: () => request<any[]>("/progress/my-progress"),
    getCourseProgress: (courseId: number) => request<any>(`/progress/course/${courseId}`),
    getLessonProgress: (lessonId: number) => request<any>(`/progress/lesson/${lessonId}`),
    recordLessonProgress: (
      lessonId: number,
      data: { progress_percentage: number; completed: boolean }
    ) => request<any>(`/progress/lesson/${lessonId}`, { method: "PUT", body: JSON.stringify(data) }),
  },

  files: {
    getViewUrl: (filePath: string) => {
      const base = getBaseUrl();
      return `${base.replace(/\/+$/, "")}/files/view?resource_url=${encodeURIComponent(filePath)}`;
    },
    getDownloadUrl: (filePath: string) => {
      const base = getBaseUrl();
      return `${base.replace(/\/+$/, "")}/files/download?resource_url=${encodeURIComponent(filePath)}`;
    },
  },
};
