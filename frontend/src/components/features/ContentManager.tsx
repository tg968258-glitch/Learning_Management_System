"use client";

import { useCallback, useEffect, useState } from "react";
import { CheckCircle2, ExternalLink, FileText, Loader2, PlayCircle, Video, X } from "lucide-react";
import { api } from "@/lib/api";
import { showSuccess } from "@/context/FeedbackContext";
import { ActionDialogButton, InlineError, SectionTitle } from "@/components/ui";
import type { Role } from "@/types/role";
import { PageSkeleton } from "@/components/ui/Skeleton";

export function ContentManager({ role }: { role: Role }) {
  const [courses, setCourses] = useState<any[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState<number | null>(null);
  const [modules, setModules] = useState<any[]>([]);
  const [selectedModuleIndex, setSelectedModuleIndex] = useState(0);
  const [lessons, setLessons] = useState<any[]>([]);
  const [selectedLesson, setSelectedLesson] = useState<any | null>(null);
  const [loading, setLoading] = useState(true);
  const [loadingLessons, setLoadingLessons] = useState(false);
  const [error, setError] = useState("");

  const fetchCoursesAndModules = useCallback(async () => {
    try {
      setError("");
      const courseList = role === "admin" ? await api.courses.getAll() : await api.courses.getMyCourses();
      if (Array.isArray(courseList) && courseList.length > 0) {
        setCourses(courseList);
        const activeCourse = selectedCourseId || courseList[0].course_id;
        setSelectedCourseId(activeCourse);

        const moduleList = await api.modules.getByCourse(activeCourse);
        setModules(Array.isArray(moduleList) ? moduleList : []);
      } else {
        setCourses([]);
        setModules([]);
      }
    } catch (err) {
      console.error("Failed to load modules:", err);
      setError("Unable to load course content. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [role, selectedCourseId]);

  useEffect(() => {
    fetchCoursesAndModules();
  }, [fetchCoursesAndModules]);

  const activeModule = modules[selectedModuleIndex];

  const fetchLessons = useCallback(async () => {
    if (!activeModule) {
      setLessons([]);
      return;
    }
    setLoadingLessons(true);
    try {
      setError("");
      const lessonList = await api.lessons.getByModule(activeModule.module_id);
      const availableLessons = Array.isArray(lessonList) ? lessonList : [];
      if (role === "student") {
        const progressResults = await Promise.allSettled(
          availableLessons.map((lesson: any) => api.progress.getLessonProgress(lesson.lesson_id))
        );
        setLessons(availableLessons.map((lesson: any, index: number) => ({
          ...lesson,
          progress: progressResults[index].status === "fulfilled"
            ? progressResults[index].value
            : { completed: false, progress_percentage: 0 },
        })));
      } else {
        setLessons(availableLessons);
      }
    } catch (err) {
      console.error("Failed to load lessons:", err);
      setLessons([]);
      setError("Unable to load lessons. Please try again.");
    } finally {
      setLoadingLessons(false);
    }
  }, [activeModule, role]);

  useEffect(() => {
    fetchLessons();
  }, [fetchLessons]);

  useEffect(() => {
    const handleRefresh = (event: Event) => {
      const detail = (event as CustomEvent<{ action?: string }>).detail;
      if (
        !detail?.action ||
        detail.action.includes("module") ||
        detail.action.includes("lesson") ||
        detail.action.includes("course")
      ) {
        fetchCoursesAndModules();
      }
    };

    window.addEventListener("learnsphere:refresh", handleRefresh);
    return () => window.removeEventListener("learnsphere:refresh", handleRefresh);
  }, [fetchCoursesAndModules]);

  const handleCompleteLesson = async (lessonId: number) => {
    try {
      setError("");
      await api.progress.recordLessonProgress(lessonId, {
        progress_percentage: 100,
        completed: true,
      });
      showSuccess("Lesson completed!");
      setSelectedLesson(null);
      fetchLessons();
    } catch (err: any) {
      setError(err.message || "Unable to update lesson progress.");
    }
  };

  const openLesson = async (lesson: any) => {
    setSelectedLesson(lesson);
    setError("");
    try {
      const detail = await api.lessons.getById(lesson.lesson_id);
      setSelectedLesson({ ...detail, progress: lesson.progress });
    } catch (err: any) {
      setError(err.message || "Unable to load lesson materials.");
    }
  };

  const resourceUrl = (url: string) =>
    url.startsWith("/uploads/") ? api.files.getViewUrl(url) : url;

  const refreshOpenLesson = async () => {
    if (!selectedLesson?.lesson_id) return;
    const detail = await api.lessons.getById(selectedLesson.lesson_id);
    setSelectedLesson(detail);
    await fetchLessons();
  };

  const videoEmbedUrl = (url: string) => {
    const youtubeMatch = url.match(/(?:youtube\.com\/watch\?v=|youtu\.be\/)([^?&/]+)/);
    return youtubeMatch ? `https://www.youtube.com/embed/${youtubeMatch[1]}` : null;
  };

  if (loading) {
    return <PageSkeleton variant="detail" />;
  }

  return (
    <>
      {!selectedLesson && <InlineError message={error} className="mb-4" />}
      {courses.length > 1 && (
        <div className="mb-5 flex items-center gap-3">
          <span className="text-xs font-bold uppercase tracking-wider text-slate-400">Course:</span>
          <select
            value={selectedCourseId || ""}
            onChange={(e) => {
              setSelectedCourseId(Number(e.target.value));
              setSelectedModuleIndex(0);
            }}
            className="rounded-xl border border-(--border) bg-white px-3 py-2 text-sm font-semibold text-slate-800 outline-none focus:border-indigo-300"
          >
            {courses.map((c) => (
              <option key={c.course_id} value={c.course_id}>
                {c.course_name}
              </option>
            ))}
          </select>
        </div>
      )}

      <div className="grid gap-5 xl:grid-cols-[.85fr_1.15fr]">
        <section className="card p-5">
          <SectionTitle
            title="Course modules"
            action={
              role === "student" ? (
                `${modules.length} modules`
              ) : (
                <ActionDialogButton
                  action="add-module"
                  label="Add module"
                  variant="secondary"
                  compact
                  initialValues={{ courseId: String(selectedCourseId || 1) }}
                  onSuccess={fetchCoursesAndModules}
                />
              )
            }
          />

          {modules.length > 0 ? (
            <div className="space-y-2">
              {modules.map((module, index) => (
                <button
                  key={module.module_id || index}
                  type="button"
                  onClick={() => setSelectedModuleIndex(index)}
                  className={`w-full rounded-xl p-3.5 text-left transition ${
                    index === selectedModuleIndex
                      ? "bg-(--brand-soft) text-(--brand)"
                      : "bg-slate-50 text-slate-700 hover:bg-slate-100"
                  }`}
                >
                  <div className="text-xs font-bold uppercase tracking-wide opacity-60">
                    Module {index + 1}
                  </div>
                  <div className="mt-1 font-semibold">{module.module_title}</div>
                </button>
              ))}
            </div>
          ) : (
            <div className="rounded-2xl border border-dashed border-(--border) p-8 text-center text-sm text-slate-500">
              No modules found. {role !== "student" && "Add your first module to get started."}
            </div>
          )}
        </section>

        <section className="card p-5">
          <SectionTitle
            title={activeModule?.module_title ?? "Module Lessons"}
            action={
              role === "student" ? (
                `${lessons.length} lessons`
              ) : (
                activeModule && (
                  <ActionDialogButton
                    action="add-lesson"
                    label="Add lesson"
                    variant="secondary"
                    compact
                    initialValues={{ moduleId: String(activeModule.module_id) }}
                    onSuccess={fetchLessons}
                  />
                )
              )
            }
          />

          {loadingLessons ? (
            <div className="space-y-3 p-4" role="status" aria-label="Loading lessons">
              {Array.from({ length: 4 }, (_, index) => (
                <div key={index} className="h-14 animate-pulse rounded-xl bg-slate-100" />
              ))}
            </div>
          ) : (
            <div className="space-y-3">
              {lessons.map((lesson, index) => (
                <button
                  key={lesson.lesson_id || index}
                  type="button"
                  onClick={() => openLesson(lesson)}
                  className="flex w-full items-center gap-4 rounded-2xl border border-(--border) p-4 text-left transition hover:bg-slate-50"
                >
                  <span className="grid h-10 w-10 shrink-0 place-items-center rounded-xl bg-indigo-50 text-indigo-600">
                    <PlayCircle size={19} />
                  </span>
                  <span className="flex-1">
                    <span className="block font-semibold">{lesson.lesson_title}</span>
                    <span className={`mt-1 block text-xs ${lesson.progress?.completed ? "font-semibold text-emerald-600" : "text-slate-500"}`}>
                      {lesson.progress?.completed ? "Completed" : `Lesson #${lesson.sequence_order || index + 1}`}
                    </span>
                  </span>
                  {lesson.progress?.completed && <CheckCircle2 size={20} className="text-emerald-600" />}
                </button>
              ))}

              {lessons.length === 0 && (
                <div className="rounded-2xl border border-dashed border-(--border) p-8 text-center text-sm text-slate-500">
                  No lessons in this module yet.
                </div>
              )}
            </div>
          )}
        </section>
      </div>

      {selectedLesson && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4 backdrop-blur-sm">
          <button
            type="button"
            className="absolute inset-0"
            onClick={() => setSelectedLesson(null)}
            aria-label="Close lesson viewer"
          />
          <div className="card relative z-10 max-h-[90vh] w-full max-w-2xl overflow-y-auto p-6 shadow-2xl">
            <InlineError message={error} className="mb-4" />
            <div className="flex items-center justify-between gap-4">
              <h2 className="text-xl font-bold">{selectedLesson.lesson_title}</h2>
              <button
                type="button"
                className="icon-button"
                onClick={() => setSelectedLesson(null)}
                aria-label="Close lesson viewer"
              >
                <X size={17} />
              </button>
            </div>

            <div className="mt-5 space-y-4">
              {selectedLesson.contents?.length > 0 ? selectedLesson.contents.map((content: any) => {
                const embedUrl = content.content_type === "video" ? videoEmbedUrl(content.content) : null;
                return (
                  <div key={content.content_id} className="rounded-2xl bg-slate-50 p-5 text-sm leading-6 text-slate-700">
                    <div className="flex items-center justify-between gap-3">
                      <p className="flex items-center gap-2 font-semibold text-slate-900">
                        {content.content_type === "video" ? <Video size={16} /> : <FileText size={16} />}
                        {content.content_type === "video" ? "Video lesson" : `${content.content_type || "text"} content`}
                      </p>
                      {role !== "student" && (
                        <ActionDialogButton action="edit-lesson-content" label="Edit" variant="secondary" compact initialValues={{
                          contentId: String(content.content_id), contentType: content.content_type || "text",
                          content: content.content || "", sequenceNumber: String(content.sequence_number || 1),
                        }} onSuccess={refreshOpenLesson} />
                      )}
                    </div>
                    {embedUrl ? (
                      <iframe className="mt-3 aspect-video w-full rounded-xl" src={embedUrl} title={selectedLesson.lesson_title} allowFullScreen />
                    ) : content.content_type === "video" ? (
                      <a className="mt-2 inline-flex items-center gap-1 text-(--brand) hover:underline" href={content.content} target="_blank" rel="noreferrer">
                        Watch video <ExternalLink size={14} />
                      </a>
                    ) : content.content_type === "audio" ? (
                      <audio className="mt-3 w-full" controls src={resourceUrl(content.content)} />
                    ) : ["pdf", "slide"].includes(content.content_type) ? (
                      <a className="mt-2 inline-flex items-center gap-1 text-(--brand) hover:underline" href={resourceUrl(content.content)} target="_blank" rel="noreferrer">
                        Open {content.content_type} <ExternalLink size={14} />
                      </a>
                    ) : content.content_type === "code" ? (
                      <pre className="mt-2 overflow-x-auto whitespace-pre-wrap rounded-xl bg-slate-900 p-4 font-mono text-xs text-slate-100">{content.content}</pre>
                    ) : (
                      <p className="mt-2 whitespace-pre-wrap text-slate-600">{content.content}</p>
                    )}
                  </div>
                );
              }) : (
                <div className="rounded-2xl bg-slate-50 p-5 text-sm leading-6 text-slate-600">
                  Engage with the lesson materials, review associated readings, and complete accompanying tasks.
                </div>
              )}

              {selectedLesson.resources?.length > 0 && (
                <div className="rounded-2xl border border-(--border) p-5">
                  <p className="font-semibold text-slate-900">Learning resources</p>
                  <div className="mt-3 space-y-2">
                    {selectedLesson.resources.map((resource: any) => (
                      <div key={resource.resource_id} className="flex items-center gap-2 rounded-xl bg-slate-50 px-3 py-2.5">
                        {resource.is_available !== false ? (
                          <a href={resourceUrl(resource.resource_url)} target="_blank" rel="noreferrer" className="flex min-w-0 flex-1 items-center justify-between gap-3 text-sm font-medium text-(--brand) hover:underline">
                            <span className="flex min-w-0 items-center gap-2"><FileText size={16} /><span className="truncate">{resource.resource_name}</span></span>
                            <ExternalLink size={15} />
                          </a>
                        ) : (
                          <span className="flex min-w-0 flex-1 items-center gap-2 text-sm text-amber-700"><FileText size={16} /><span className="truncate">{resource.resource_name} — file unavailable</span></span>
                        )}
                        {role !== "student" && (
                          <ActionDialogButton action="edit-resource" label="Edit" variant="secondary" compact initialValues={{
                            resourceId: String(resource.resource_id), resourceName: resource.resource_name || "",
                            resourceType: resource.resource_type || "link",
                            resourceUrl: resource.resource_url?.startsWith("/uploads/") ? "" : resource.resource_url || "",
                          }} onSuccess={refreshOpenLesson} />
                        )}
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>

            <div className="mt-5 flex justify-end gap-2 border-t border-(--border) pt-4">
              <button
                type="button"
                onClick={() => setSelectedLesson(null)}
                className="secondary-button"
              >
                Close
              </button>

              {role !== "student" && (
                <ActionDialogButton action="edit-lesson" label="Edit lesson" variant="primary" initialValues={{
                  lessonId: String(selectedLesson.lesson_id), title: selectedLesson.lesson_title,
                  publication: selectedLesson.is_published ? "Published" : "Draft",
                }} onSuccess={refreshOpenLesson} />
              )}

              {role === "student" && (
                <button
                  type="button"
                  onClick={() => handleCompleteLesson(selectedLesson.lesson_id)}
                  disabled={Boolean(selectedLesson.progress?.completed)}
                  className="primary-button"
                >
                  <CheckCircle2 size={16} />
                  {selectedLesson.progress?.completed ? "Completed" : "Mark Completed"}
                </button>
              )}
            </div>
          </div>
        </div>
      )}
    </>
  );
}
