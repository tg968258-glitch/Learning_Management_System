"use client";

import { useEffect, useMemo, useState } from "react";
import {
  BookPlus,
  CalendarPlus,
  MailPlus,
  Pencil,
  Plus,
  AlertCircle,
  X,
} from "lucide-react";
import { api, getStoredSession } from "@/lib/api";
import { showSuccess } from "@/context/FeedbackContext";
import { getUserFacingErrorMessage } from "@/lib/userFacingError";
import { Button } from "./Button";

export type ActionKey =
  | "create-course"
  | "edit-course"
  | "invite-teacher"
  | "new-assignment"
  | "create-quiz"
  | "edit-quiz"
  | "schedule-session"
  | "new-announcement"
  | "new-discussion"
  | "add-module"
  | "add-lesson"
  | "edit-lesson"
  | "edit-lesson-content"
  | "edit-resource"
  | "edit-student"
  | "edit-teacher"
  | "edit-assignment"
  | "edit-session"
  | "grade-submission";

type Field = {
  name: string;
  label: string;
  type?: "text" | "email" | "number" | "date" | "time" | "url" | "textarea" | "select" | "file";
  placeholder?: string;
  options?: string[];
  required?: boolean;
  readOnly?: boolean;
};

type RelationOption = { value: string; label: string };

const qualifications = [
  "B.Tech",
  "B.E.",
  "B.Sc",
  "BCA",
  "B.Ed",
  "B.Com",
  "B.A.",
  "M.Tech",
  "M.E.",
  "M.Sc",
  "MCA",
  "MBA",
  "M.Ed",
  "M.Com",
  "M.A.",
  "M.Phil",
  "Ph.D.",
];

const configs: Record<
  ActionKey,
  {
    title: string;
    submit: string;
    successMessage: string;
    errorMessage: string;
    fields: Field[];
  }
> = {
  "create-course": {
    title: "Create course",
    submit: "Create course",
    successMessage: "Course created successfully.",
    errorMessage: "Unable to create course. Please try again.",
    fields: [
      { name: "courseName", label: "Course name", placeholder: "Enter course name" },
      { name: "category", label: "Category / Code", placeholder: "e.g. CS101" },
      { name: "description", label: "Description", type: "textarea", placeholder: "Enter course description" },
    ],
  },
  "edit-course": {
    title: "Edit course",
    submit: "Save changes",
    successMessage: "Course updated successfully.",
    errorMessage: "Unable to update course. Please try again.",
    fields: [
      { name: "courseName", label: "Course name", placeholder: "Enter course name" },
      { name: "courseDisplayId", label: "Course ID", readOnly: true },
      { name: "description", label: "Description", type: "textarea", placeholder: "Enter course description" },
      { name: "status", label: "Status", type: "select", options: ["Active", "Inactive"] },
    ],
  },
  "invite-teacher": {
    title: "Invite teacher",
    submit: "Send invitation",
    successMessage: "Teacher invited successfully.",
    errorMessage: "Unable to send teacher invitation. Please try again.",
    fields: [
      { name: "email", label: "Teacher email", type: "email", placeholder: "Enter teacher email" },
    ],
  },
  "new-assignment": {
    title: "New assignment",
    submit: "Create assignment",
    successMessage: "Assignment created successfully.",
    errorMessage: "Unable to create assignment. Please try again.",
    fields: [
      { name: "courseId", label: "Course", type: "select", options: [] },
      { name: "moduleId", label: "Module", type: "select", options: [] },
      { name: "title", label: "Title", placeholder: "Enter assignment title" },
      { name: "description", label: "Description", type: "textarea", placeholder: "Enter instructions" },
      { name: "dueDate", label: "Due date", type: "date" },
      { name: "maxMarks", label: "Max marks", type: "number", placeholder: "Enter max marks (e.g. 100)" },
      { name: "passingMarks", label: "Passing marks", type: "number", placeholder: "Enter passing marks (e.g. 40)" },
    ],
  },
  "edit-assignment": {
    title: "Edit assignment",
    submit: "Save changes",
    successMessage: "Assignment updated successfully.",
    errorMessage: "Unable to update assignment. Please try again.",
    fields: [
      { name: "title", label: "Title", placeholder: "Enter title" },
      { name: "dueDate", label: "Due date", type: "date" },
      { name: "maxMarks", label: "Max marks", type: "number", placeholder: "Enter max marks" },
      { name: "description", label: "Description", type: "textarea", placeholder: "Enter description" },
    ],
  },
  "create-quiz": {
    title: "Create quiz",
    submit: "Create quiz",
    successMessage: "Quiz created successfully.",
    errorMessage: "Unable to create quiz. Please try again.",
    fields: [
      { name: "courseId", label: "Course", type: "select", options: [] },
      { name: "title", label: "Quiz title", placeholder: "Enter quiz title" },
      { name: "description", label: "Description", type: "textarea", placeholder: "Enter quiz instructions" },
      { name: "duration", label: "Duration (minutes)", type: "number", placeholder: "e.g. 15" },
      { name: "maxMarks", label: "Max marks", type: "number", placeholder: "e.g. 20" },
      { name: "passingMarks", label: "Passing marks", type: "number", placeholder: "e.g. 10" },
    ],
  },
  "edit-quiz": {
    title: "Edit quiz",
    submit: "Save changes",
    successMessage: "Quiz updated successfully.",
    errorMessage: "Unable to update quiz. Please try again.",
    fields: [
      { name: "title", label: "Quiz title", placeholder: "Enter quiz title" },
      { name: "duration", label: "Duration (minutes)", type: "number", placeholder: "Enter duration" },
      { name: "maxMarks", label: "Max marks", type: "number", placeholder: "Enter max marks" },
    ],
  },
  "schedule-session": {
    title: "Schedule session",
    submit: "Schedule session",
    successMessage: "Session scheduled successfully.",
    errorMessage: "Unable to schedule session. Please try again.",
    fields: [
      { name: "courseId", label: "Course", type: "select", options: [] },
      { name: "teacherId", label: "Teacher", type: "select", options: [] },
      { name: "topic", label: "Topic", placeholder: "Enter session topic" },
      { name: "sessionDate", label: "Session date", type: "date" },
      { name: "startTime", label: "Start time", type: "time" },
      { name: "endTime", label: "End time", type: "time" },
      { name: "meetingLink", label: "Meeting link", type: "url", placeholder: "https://meet.google.com/..." },
    ],
  },
  "edit-session": {
    title: "Edit session",
    submit: "Save changes",
    successMessage: "Session updated successfully.",
    errorMessage: "Unable to update session. Please try again.",
    fields: [
      { name: "topic", label: "Topic", placeholder: "Enter topic" },
      { name: "sessionDate", label: "Session date", type: "date" },
      { name: "startTime", label: "Start time", type: "time" },
      { name: "endTime", label: "End time", type: "time" },
      { name: "meetingLink", label: "Meeting link", type: "url", placeholder: "Enter meeting link" },
      { name: "status", label: "Status", type: "select", options: ["upcoming", "completed", "cancelled"] },
    ],
  },
  "new-announcement": {
    title: "New announcement",
    submit: "Publish announcement",
    successMessage: "Announcement created successfully.",
    errorMessage: "Unable to create announcement. Please try again.",
    fields: [
      { name: "courseId", label: "Student audience", type: "select", options: [], required: false },
      { name: "title", label: "Title", placeholder: "Enter announcement title" },
      { name: "message", label: "Message", type: "textarea", placeholder: "Enter announcement text" },
    ],
  },
  "new-discussion": {
    title: "New discussion",
    submit: "Create discussion",
    successMessage: "Discussion posted successfully.",
    errorMessage: "Unable to post discussion. Please try again.",
    fields: [
      { name: "courseId", label: "Course", type: "select", options: [] },
      { name: "title", label: "Discussion title", placeholder: "Enter discussion title" },
      { name: "message", label: "Message", type: "textarea", placeholder: "Enter discussion text" },
    ],
  },
  "add-module": {
    title: "Add module",
    submit: "Add module",
    successMessage: "Module created successfully.",
    errorMessage: "Unable to create module. Please try again.",
    fields: [
      { name: "courseId", label: "Course", type: "select", options: [] },
      { name: "title", label: "Module title", placeholder: "Enter module title" },
    ],
  },
  "add-lesson": {
    title: "Add lesson",
    submit: "Create lesson",
    successMessage: "Lesson and learning materials created successfully.",
    errorMessage: "Unable to create lesson. Please try again.",
    fields: [
      { name: "moduleId", label: "Module", type: "select", options: [] },
      { name: "title", label: "Lesson title", placeholder: "Enter lesson title" },
      { name: "materialType", label: "Learning material type", type: "select", options: ["Text", "Video", "PDF / document", "Link"] },
      { name: "content", label: "Text or video URL", type: "textarea", placeholder: "Write lesson notes, or paste a YouTube/video URL", required: false },
      { name: "resourceUrl", label: "Resource URL", type: "url", placeholder: "https://example.com/notes.pdf", required: false },
      { name: "resourceFile", label: "Upload resource", type: "file", placeholder: "PDF, video, audio, slides, or document", required: false },
    ],
  },
  "edit-lesson": {
    title: "Edit lesson",
    submit: "Save lesson",
    successMessage: "Lesson updated successfully.",
    errorMessage: "Unable to update lesson.",
    fields: [
      { name: "title", label: "Lesson title", placeholder: "Enter lesson title" },
      { name: "publication", label: "Visibility", type: "select", options: ["Published", "Draft"] },
    ],
  },
  "edit-lesson-content": {
    title: "Edit lesson content",
    submit: "Save content",
    successMessage: "Lesson content updated successfully.",
    errorMessage: "Unable to update lesson content.",
    fields: [
      { name: "contentType", label: "Content type", type: "select", options: ["text", "markdown", "code", "video", "audio", "pdf", "slide"] },
      { name: "content", label: "Content or URL", type: "textarea", placeholder: "Enter lesson text or media URL" },
      { name: "sequenceNumber", label: "Sequence", type: "number", placeholder: "1" },
    ],
  },
  "edit-resource": {
    title: "Edit learning resource",
    submit: "Save resource",
    successMessage: "Learning resource updated successfully.",
    errorMessage: "Unable to update learning resource.",
    fields: [
      { name: "resourceName", label: "Resource name", placeholder: "Enter resource name" },
      { name: "resourceType", label: "Resource type", type: "select", options: ["link", "pdf", "document", "slides", "video", "audio"] },
      { name: "resourceUrl", label: "External URL", type: "url", placeholder: "https://example.com/resource", required: false },
      { name: "resourceFile", label: "Replace uploaded file", type: "file", required: false },
    ],
  },
  "edit-student": {
    title: "Edit student profile",
    submit: "Save changes",
    successMessage: "Student profile updated successfully.",
    errorMessage: "Unable to update student profile. Please try again.",
    fields: [
      { name: "name", label: "Name", placeholder: "Enter student name" },
      { name: "phoneNumber", label: "Phone number", placeholder: "Enter phone number", required: false },
      { name: "dateOfBirth", label: "Date of birth", type: "date", required: false },
      { name: "gender", label: "Gender", type: "select", options: ["Not specified", "Female", "Male", "Other"], required: false },
    ],
  },
  "edit-teacher": {
    title: "Edit teacher profile",
    submit: "Save changes",
    successMessage: "Profile updated successfully.",
    errorMessage: "Unable to update profile. Please try again.",
    fields: [
      { name: "name", label: "Name", placeholder: "Enter name" },
      { name: "phoneNumber", label: "Phone number", placeholder: "Enter phone number" },
      { name: "specialization", label: "Specialization", placeholder: "Enter specialization" },
      { name: "qualification", label: "Qualification", type: "select", options: qualifications },
    ],
  },
  "grade-submission": {
    title: "Grade submission",
    submit: "Save grade",
    successMessage: "Assignment graded successfully.",
    errorMessage: "Unable to grade submission. Please try again.",
    fields: [
      { name: "marks", label: "Marks awarded", type: "number", placeholder: "Enter marks" },
      { name: "feedback", label: "Feedback", type: "textarea", placeholder: "Enter feedback" },
    ],
  },
};

function ActionIcon({ action }: { action: ActionKey }) {
  if (action === "create-course") return <BookPlus size={17} />;
  if (action === "edit-course") return <Pencil size={15} />;
  if (action === "invite-teacher") return <MailPlus size={17} />;
  if (action === "schedule-session") return <CalendarPlus size={17} />;
  if (action.startsWith("edit") || action === "grade-submission") return <Pencil size={15} />;
  return <Plus size={17} />;
}

export function ActionDialogButton({
  action,
  label,
  variant = "primary",
  compact = false,
  initialValues = {},
  onSuccess,
}: {
  action: ActionKey;
  label?: string;
  variant?: "primary" | "secondary";
  compact?: boolean;
  initialValues?: Record<string, string>;
  onSuccess?: () => void;
}) {
  const config = configs[action];
  const [open, setOpen] = useState(false);
  const [loading, setLoading] = useState(false);
  const [formError, setFormError] = useState("");
  const [errorField, setErrorField] = useState<string | null>(null);
  const [relationOptions, setRelationOptions] = useState<Record<string, RelationOption[]>>({});
  const [optionsLoading, setOptionsLoading] = useState(false);
  const defaultValues = useMemo(() => initialValues, [initialValues]);
  const isAdmin = getStoredSession()?.user?.role === "admin";

  const setDialogError = (message: unknown, field: string | null = null) => {
    setFormError(getUserFacingErrorMessage(message, config.errorMessage));
    setErrorField(field);
  };

  useEffect(() => {
    if (!open) return;
    const relationalNames = new Set(config.fields.map((field) => field.name));
    if (!["courseId", "moduleId", "lessonId", "teacherId"].some((name) => relationalNames.has(name))) return;

    let active = true;
    setOptionsLoading(true);
    (async () => {
      try {
        const courses = isAdmin ? await api.courses.getAll() : await api.courses.getMyCourses();
        const courseList = Array.isArray(courses) ? courses : [];
        const next: Record<string, RelationOption[]> = {
          courseId: courseList.map((course: any) => ({
            value: String(course.course_id),
            label: `${course.course_name} - Course ${course.course_id}`,
          })),
        };

        if (relationalNames.has("teacherId")) {
          const teachers = await api.teachers.getAll();
          next.teacherId = (Array.isArray(teachers) ? teachers : []).map((teacher: any) => ({
            value: String(teacher.teacher_id),
            label: `${teacher.name || "Teacher"} - Teacher ${teacher.teacher_id}`,
          }));
        }

        if (relationalNames.has("moduleId") || relationalNames.has("lessonId")) {
          const moduleGroups = await Promise.all(courseList.map(async (course: any) => ({
            course,
            modules: await api.modules.getByCourse(course.course_id),
          })));
          const modules = moduleGroups.flatMap(({ course, modules }) =>
            (Array.isArray(modules) ? modules : []).map((module: any) => ({ ...module, course }))
          );
          next.moduleId = modules.map((module: any) => ({
            value: String(module.module_id),
            label: `${module.module_name || module.module_title} (${module.course.course_name}) - Module ${module.module_id}`,
          }));

          if (relationalNames.has("lessonId")) {
            const lessonGroups = await Promise.all(modules.map(async (module: any) => ({
              module,
              lessons: await api.lessons.getByModule(module.module_id),
            })));
            next.lessonId = lessonGroups.flatMap(({ module, lessons }) =>
              (Array.isArray(lessons) ? lessons : []).map((lesson: any) => ({
                value: String(lesson.lesson_id),
                label: `${lesson.lesson_title} (${module.course.course_name}) - Lesson ${lesson.lesson_id}`,
              }))
            );
          }
        }
        if (active) setRelationOptions(next);
      } catch (error) {
        console.error("Unable to load form options:", error);
        if (active) {
          setRelationOptions({});
          setDialogError("Unable to load available selections. Please close the form and try again.");
        }
      } finally {
        if (active) setOptionsLoading(false);
      }
    })();
    return () => { active = false; };
  }, [config.fields, isAdmin, open]);

  const close = () => {
    if (loading) return;
    setFormError("");
    setErrorField(null);
    setOpen(false);
  };

  const handleSubmit = async (event: React.FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setFormError("");
    setErrorField(null);

    const form = new FormData(event.currentTarget);
    const uploadedResource = form.get("resourceFile");
    const values = Object.fromEntries(
      Array.from(form.entries())
        .filter(([key]) => key !== "resourceFile")
        .map(([key, val]) => [key, String(val).trim()])
    );

    const missingControl = Array.from(event.currentTarget.elements).find(
      (element): element is HTMLInputElement | HTMLSelectElement | HTMLTextAreaElement =>
        (element instanceof HTMLInputElement ||
          element instanceof HTMLSelectElement ||
          element instanceof HTMLTextAreaElement) &&
        element.required &&
        !element.value.trim()
    );
    if (missingControl) {
      const field = config.fields.find((item) => item.name === missingControl.name);
      const instruction = missingControl instanceof HTMLSelectElement ? "select" : "enter";
      setDialogError(`Please ${instruction} ${field?.label.toLowerCase() || "this required field"}.`, missingControl.name);
      missingControl.focus();
      return;
    }

    // ── Frontend Validations ──────────────────────────────────────────
    // 1. Email validation
    if (values.email) {
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (!emailRegex.test(values.email)) {
        setDialogError("Please enter a valid email address.", "email");
        return;
      }
    }

    // 2. Phone number validation (exactly 10 digits)
    const phoneVal = values.phone || values.phoneNumber;
    if (phoneVal) {
      if (!/^\d{10}$/.test(phoneVal)) {
        setDialogError("Phone number must contain exactly 10 digits.", values.phone ? "phone" : "phoneNumber");
        return;
      }
    }

    // 3. Name & Title validations
    if ("name" in values && (!values.name || values.name.length < 2)) {
      setDialogError("Name must be at least 2 characters.", "name");
      return;
    }
    if ("courseName" in values && (!values.courseName || values.courseName.length < 2)) {
      setDialogError("Course name must be at least 2 characters.", "courseName");
      return;
    }
    if ("title" in values && (!values.title || values.title.length < 2)) {
      setDialogError("Title must be at least 2 characters.", "title");
      return;
    }
    if ("topic" in values && (!values.topic || values.topic.length < 2)) {
      setDialogError("Topic must be at least 2 characters.", "topic");
      return;
    }

    // 4. Numeric ID validations
    const idFields = ["studentId", "courseId", "moduleId", "lessonId", "teacherId"];
    for (const idField of idFields) {
      if (idField in values && values[idField]) {
        const num = Number(values[idField]);
        if (Number.isNaN(num) || num <= 0) {
          setDialogError(`Please select a valid ${idField.replace("Id", "").toLowerCase()}.`, idField);
          return;
        }
      }
    }

    // 5. Experience validation
    if ("experience" in values && values.experience) {
      const exp = Number(values.experience);
      if (Number.isNaN(exp) || exp < 0 || exp > 60) {
        setDialogError("Experience must be between 0 and 60 years.", "experience");
        return;
      }
    }

    // 6. Marks validation
    if ("maxMarks" in values && values.maxMarks) {
      const marks = Number(values.maxMarks);
      if (Number.isNaN(marks) || marks <= 0) {
        setDialogError("Max marks must be greater than 0.", "maxMarks");
        return;
      }
    }
    if ("passingMarks" in values && values.passingMarks) {
      const passMarks = Number(values.passingMarks);
      const maxMarks = Number(values.maxMarks) || 100;
      if (Number.isNaN(passMarks) || passMarks < 0 || passMarks > maxMarks) {
        setDialogError("Passing marks must be between 0 and max marks.", "passingMarks");
        return;
      }
    }

    // 7. Duration validation
    if ("duration" in values && values.duration) {
      const dur = Number(values.duration);
      if (Number.isNaN(dur) || dur <= 0 || dur > 600) {
        setDialogError("Duration must be between 1 and 600 minutes.", "duration");
        return;
      }
    }

    // 8. Meeting link validation
    if (values.meetingLink) {
      try {
        const meetingUrl = new URL(values.meetingLink);
        const hostname = meetingUrl.hostname.toLowerCase();
        const allowed = meetingUrl.protocol === "https:" && (
          hostname === "meet.google.com" || hostname === "teams.microsoft.com" ||
          hostname === "zoom.us" || hostname.endsWith(".zoom.us")
        );
        if (!allowed) throw new Error("Unsupported meeting URL");
      } catch {
        setDialogError("Enter a valid HTTPS Google Meet, Zoom, or Microsoft Teams link.", "meetingLink");
        return;
      }
    }

    // 9. Time validation
    if (values.startTime && values.endTime && values.startTime >= values.endTime) {
      setDialogError("End time must be after start time.", "endTime");
      return;
    }

    setLoading(true);

    try {
      if (action === "create-course") {
        await api.courses.create({
          course_name: values.courseName,
          category: values.category || "General",
          description: values.description || values.courseName,
          status: "active",
        });
      } else if (action === "edit-course") {
        const id = Number(defaultValues.courseId);
        await api.courses.update(id, {
          course_name: values.courseName,
          description: values.description,
          status: (values.status || "Inactive").toLowerCase(),
        });
      } else if (action === "invite-teacher") {
        await api.auth.inviteTeacher(values.email);
      } else if (action === "new-assignment") {
        await api.assignments.create({
          course_id: Number(values.courseId),
          module_id: Number(values.moduleId),
          title: values.title,
          description: values.description || "",
          max_marks: Number(values.maxMarks) || 100,
          passing_marks: Number(values.passingMarks),
          due_date: `${values.dueDate}T23:59:59`,
        });
      } else if (action === "edit-assignment") {
        const id = Number(values.assignmentId || defaultValues.assignmentId || 1);
        await api.assignments.update(id, {
          title: values.title,
          description: values.description,
          max_marks: Number(values.maxMarks) || 100,
          due_date: values.dueDate ? `${values.dueDate}T23:59:59` : undefined,
        });
      } else if (action === "create-quiz") {
        await api.quizzes.create({
          course_id: Number(values.courseId),
          title: values.title,
          description: values.description || "",
          max_marks: Number(values.maxMarks) || 20,
          passing_marks: Number(values.passingMarks) || 10,
          duration_minutes: Number(values.duration) || 15,
          is_published: true,
        });
      } else if (action === "edit-quiz") {
        const id = Number(values.quizId || defaultValues.quizId || 1);
        await api.quizzes.update(id, {
          title: values.title,
          duration_minutes: Number(values.duration) || 15,
          max_marks: Number(values.maxMarks) || 20,
        });
      } else if (action === "schedule-session") {
        await api.sessions.create({
          course_id: Number(values.courseId) || 1,
          teacher_id: Number(values.teacherId) || 1,
          session_title: values.topic,
          session_date: values.sessionDate,
          start_time: values.startTime ? (values.startTime.length === 5 ? `${values.startTime}:00` : values.startTime) : "10:00:00",
          end_time: values.endTime ? (values.endTime.length === 5 ? `${values.endTime}:00` : values.endTime) : "11:00:00",
          meeting_link: values.meetingLink || "https://meet.google.com",
          status: "upcoming",
        });
      } else if (action === "edit-session") {
        const id = Number(values.sessionId || defaultValues.sessionId || 1);
        await api.sessions.update(id, {
          session_title: values.topic,
          session_date: values.sessionDate,
          start_time: values.startTime ? (values.startTime.length === 5 ? `${values.startTime}:00` : values.startTime) : undefined,
          end_time: values.endTime ? (values.endTime.length === 5 ? `${values.endTime}:00` : values.endTime) : undefined,
          meeting_link: values.meetingLink,
          status: values.status,
        });
      } else if (action === "new-announcement") {
        await api.announcements.create({
          course_id: values.courseId ? Number(values.courseId) : undefined,
          audience: values.courseId ? "course_students" : "students_only",
          title: values.title,
          message: values.message,
        });
      } else if (action === "new-discussion") {
        await api.discussions.create({
          course_id: Number(values.courseId) || 1,
          message: `${values.title}: ${values.message}`,
        });
      } else if (action === "add-module") {
        await api.modules.create({
          course_id: Number(values.courseId) || 1,
          module_name: values.title,
        });
      } else if (action === "add-lesson") {
        const lesson = await api.lessons.create({
          module_id: Number(values.moduleId) || 1,
          lesson_title: values.title,
          is_published: true,
        });
        const materialType = (values.materialType || "Text").toLowerCase();
        const resourceName = `${values.title} - ${values.materialType || "resource"}`;

        if (values.content) {
          await api.lessons.addContent(lesson.lesson_id, {
            content_type: materialType === "video" ? "video" : "text",
            content: values.content,
          });
        }
        if (values.resourceUrl) {
          await api.lessons.addResourceLink(lesson.lesson_id, {
            resource_name: resourceName,
            resource_type: materialType === "pdf / document" ? "pdf" : materialType,
            resource_url: values.resourceUrl,
          });
        }
        if (uploadedResource instanceof File && uploadedResource.size > 0) {
          const extension = uploadedResource.name.split(".").pop()?.toLowerCase() || "file";
          await api.lessons.uploadResource(lesson.lesson_id, uploadedResource, uploadedResource.name, extension);
        }
      } else if (action === "edit-lesson") {
        const id = Number(values.lessonId || defaultValues.lessonId);
        await api.lessons.update(id, {
          lesson_title: values.title,
          is_published: values.publication === "Published",
        });
      } else if (action === "edit-lesson-content") {
        const id = Number(values.contentId || defaultValues.contentId);
        await api.lessons.updateContent(id, {
          content_type: values.contentType,
          content: values.content,
          sequence_number: Number(values.sequenceNumber) || 1,
        });
      } else if (action === "edit-resource") {
        const id = Number(values.resourceId || defaultValues.resourceId);
        if (uploadedResource instanceof File && uploadedResource.size > 0) {
          await api.lessons.replaceResourceFile(id, uploadedResource, values.resourceName, values.resourceType);
        } else {
          await api.lessons.updateResource(id, {
            resource_name: values.resourceName,
            resource_type: values.resourceType,
            ...(values.resourceUrl ? { resource_url: values.resourceUrl } : {}),
          });
        }
      } else if (action === "edit-teacher") {
        const id = Number(values.personId || defaultValues.personId || 1);
        await api.teachers.update(id, {
          name: values.name,
          phone_number: values.phoneNumber,
          specialization: values.specialization,
          qualification: values.qualification,
        });
      } else if (action === "edit-student") {
        const id = Number(values.personId || defaultValues.personId || 1);
        await api.students.update(id, {
          name: values.name,
          phone_number: values.phoneNumber,
          date_of_birth: values.dateOfBirth || null,
          gender: values.gender === "Not specified" ? null : values.gender || null,
        });
      } else if (action === "grade-submission") {
        const subId = Number(values.submissionId || defaultValues.submissionId || 1);
        await api.assignments.gradeSubmission(subId, {
          marks: Number(values.marks) || 0,
          feedback: values.feedback || "Good effort",
        });
      }

      showSuccess(config.successMessage);
      setOpen(false);

      // Trigger global refresh event for any active page
      if (typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent("learnsphere:refresh", { detail: { action } }));
      }

      onSuccess?.();
    } catch (err: any) {
      console.error(`Error performing action ${action}:`, err);
      setDialogError(err?.message || config.errorMessage, action === "invite-teacher" ? "email" : null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <>
      <Button
        type="button"
        variant={variant}
        onClick={(event) => {
          event.stopPropagation();
          setFormError("");
          setErrorField(null);
          setOpen(true);
        }}
        className={compact ? "px-3 py-2 text-xs shadow-none" : ""}
      >
        <ActionIcon action={action} />
        {label ?? config.title}
      </Button>

      {open && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4 backdrop-blur-sm">
          <button
            type="button"
            className="absolute inset-0"
            onClick={close}
            aria-label={`Close ${config.title}`}
          />

          <div className="card relative z-10 max-h-[90vh] w-full max-w-xl overflow-y-auto p-6 shadow-2xl">
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-xl font-bold">{config.title}</h2>

              <button
                type="button"
                className="icon-button"
                onClick={close}
                disabled={loading}
                aria-label={`Close ${config.title}`}
              >
                <X size={17} />
              </button>
            </div>

            <form
              className="mt-5 space-y-4"
              onSubmit={handleSubmit}
              onChange={() => {
                if (formError) {
                  setFormError("");
                  setErrorField(null);
                }
              }}
              noValidate
            >
              {Object.entries(defaultValues)
                .filter(([key]) => !config.fields.some((field) => field.name === key))
                .map(([key, value]) => (
                  <input key={key} type="hidden" name={key} value={value} />
                ))}

              <div className="grid gap-4 sm:grid-cols-2">
                {config.fields.map((field) => {
                  const hasError = Boolean(formError && errorField === field.name);
                  return (
                  <label
                    key={field.name}
                    className={field.type === "textarea" ? "sm:col-span-2" : ""}
                  >
                    <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                      {field.label}
                    </span>

                    {field.type === "textarea" ? (
                      <textarea
                        name={field.name}
                        defaultValue={defaultValues[field.name]}
                        placeholder={field.placeholder}
                        rows={3}
                        maxLength={5000}
                        required={field.required !== false}
                        aria-invalid={hasError}
                        className={`w-full rounded-xl border bg-white px-3 py-2.5 text-sm outline-none ${hasError ? "border-red-400 bg-red-50/40 focus:border-red-500" : "border-(--border) focus:border-indigo-300"}`}
                      />
                    ) : relationOptions[field.name] ? (
                      <select
                        name={field.name}
                        defaultValue={defaultValues[field.name] || ""}
                        required={field.required !== false}
                        disabled={optionsLoading}
                        aria-invalid={hasError}
                        className={`w-full rounded-xl border bg-white px-3 py-2.5 text-sm outline-none ${hasError ? "border-red-400 bg-red-50/40 focus:border-red-500" : "border-(--border) focus:border-indigo-300"}`}
                      >
                        <option value="">
                          {field.name === "courseId" && field.required === false ? "All students" : optionsLoading ? "Loading..." : `Select ${field.label.toLowerCase()}`}
                        </option>
                        {relationOptions[field.name].map((option) => (
                          <option key={option.value} value={option.value}>{option.label}</option>
                        ))}
                      </select>
                    ) : field.type === "select" ? (
                      <select
                        name={field.name}
                        defaultValue={defaultValues[field.name] || field.options?.[0]}
                        aria-invalid={hasError}
                        className={`w-full rounded-xl border bg-white px-3 py-2.5 text-sm outline-none ${hasError ? "border-red-400 bg-red-50/40 focus:border-red-500" : "border-(--border) focus:border-indigo-300"}`}
                      >
                        {field.options?.map((option) => (
                          <option key={option} value={option}>
                            {option}
                          </option>
                        ))}
                      </select>
                    ) : field.type === "file" ? (
                      <input
                        name={field.name}
                        type="file"
                        accept=".pdf,.doc,.docx,.txt,.ppt,.pptx,.mp4,.webm,.mov,.mp3,.wav,.m4a"
                        aria-invalid={hasError}
                        className={`w-full rounded-xl border bg-white px-3 py-2 text-sm outline-none ${hasError ? "border-red-400 bg-red-50/40 focus:border-red-500" : "border-(--border) focus:border-indigo-300"}`}
                      />
                    ) : field.name === "phone" || field.name === "phoneNumber" ? (
                      <input
                        name={field.name}
                        type="tel"
                        inputMode="numeric"
                        maxLength={10}
                        pattern="[0-9]{10}"
                        title="Phone number must be exactly 10 digits"
                        defaultValue={defaultValues[field.name]}
                        placeholder={field.placeholder || "Enter 10-digit phone number"}
                        onInput={(e) => {
                          e.currentTarget.value = e.currentTarget.value.replace(/\D/g, "").slice(0, 10);
                        }}
                        aria-invalid={hasError}
                        className={`w-full rounded-xl border bg-white px-3 py-2.5 text-sm outline-none ${hasError ? "border-red-400 bg-red-50/40 focus:border-red-500" : "border-(--border) focus:border-indigo-300"}`}
                      />
                    ) : field.type === "email" || field.name === "email" ? (
                      <input
                        name={field.name}
                        type="email"
                        defaultValue={defaultValues[field.name]}
                        placeholder={field.placeholder || "Enter email address"}
                        required={field.required !== false}
                        aria-invalid={hasError}
                        className={`w-full rounded-xl border bg-white px-3 py-2.5 text-sm outline-none ${hasError ? "border-red-400 bg-red-50/40 focus:border-red-500" : "border-(--border) focus:border-indigo-300"}`}
                      />
                    ) : field.type === "number" ? (
                      <input
                        name={field.name}
                        type="number"
                        inputMode="numeric"
                        min={field.name === "experience" || field.name === "passingMarks" || field.name === "marks" ? 0 : 1}
                        max={field.name === "experience" ? 60 : undefined}
                        defaultValue={defaultValues[field.name]}
                        placeholder={field.placeholder}
                        required={field.required !== false}
                        aria-invalid={hasError}
                        className={`w-full rounded-xl border bg-white px-3 py-2.5 text-sm outline-none ${hasError ? "border-red-400 bg-red-50/40 focus:border-red-500" : "border-(--border) focus:border-indigo-300"}`}
                      />
                    ) : (
                      <input
                        name={field.name}
                        type={field.type ?? "text"}
                        defaultValue={defaultValues[field.name]}
                        placeholder={field.placeholder}
                        maxLength={field.name === "courseName" || field.name === "name" ? 100 : field.name === "title" || field.name === "topic" || field.name === "resourceName" ? 150 : 500}
                        readOnly={field.readOnly}
                        required={field.required ?? (field.name !== "description" && field.name !== "meetingLink")}
                        min={field.type === "date" && field.name !== "dateOfBirth" ? new Date().toISOString().slice(0, 10) : undefined}
                        max={field.name === "dateOfBirth" ? new Date().toISOString().slice(0, 10) : undefined}
                        aria-invalid={hasError}
                        className={`w-full rounded-xl border px-3 py-2.5 text-sm outline-none ${hasError ? "border-red-400 bg-red-50/40 focus:border-red-500" : "border-(--border) focus:border-indigo-300"} ${field.readOnly ? "cursor-not-allowed bg-slate-100 text-slate-500" : "bg-white"}`}
                      />
                    )}

                    {hasError && (
                      <span className="mt-2 flex items-start gap-2 rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs leading-5 text-red-700" role="alert">
                        <AlertCircle className="mt-0.5 shrink-0" size={15} />
                        <span>{formError}</span>
                      </span>
                    )}
                  </label>
                  );
                })}
              </div>

              {formError && !errorField && (
                <div className="flex items-start gap-2 rounded-xl border border-red-200 bg-red-50 px-3.5 py-3 text-sm leading-5 text-red-700" role="alert">
                  <AlertCircle className="mt-0.5 shrink-0" size={17} />
                  <span>{formError}</span>
                </div>
              )}

              <div className="flex justify-end gap-2 border-t border-(--border) pt-4">
                <button
                  type="button"
                  onClick={close}
                  disabled={loading}
                  className="secondary-button"
                >
                  Cancel
                </button>

                <button
                  type="submit"
                  disabled={loading}
                  className="primary-button"
                >
                  {loading ? "Processing..." : config.submit}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
