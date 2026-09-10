"use client";

import { FormEvent, useEffect, useState } from "react";
import { Plus, Trash2, X } from "lucide-react";
import { api } from "@/lib/api";
import { showSuccess } from "@/context/FeedbackContext";
import { InlineError } from "@/components/ui";

type QuestionDraft = {
  id: number;
  question: string;
  options: string[];
  answerIndex: number;
};

const emptyQuestion = (id: number): QuestionDraft => ({
  id,
  question: "",
  options: ["", "", "", ""],
  answerIndex: 0,
});

export function QuizBuilderButton() {
  const [courses, setCourses] = useState<any[]>([]);
  const [selectedCourseId, setSelectedCourseId] = useState("");
  const [open, setOpen] = useState(false);
  const [saving, setSaving] = useState(false);
  const [questions, setQuestions] = useState<QuestionDraft[]>([emptyQuestion(1)]);
  const [error, setError] = useState("");

  useEffect(() => {
    if (open) {
      api.courses.getAll().then((courseData) => {
        const courses = Array.isArray(courseData) ? courseData : [];
        setCourses(courses);
        setSelectedCourseId((current) => current || String(courses[0]?.course_id ?? ""));
      }).catch((err) => {
        console.error("Could not fetch courses for quiz builder:", err);
        setCourses([]);
        setError("Unable to load courses for the quiz builder. Please try again.");
      });
    }
  }, [open]);

  const close = () => {
    if (saving) return;
    setOpen(false);
    setQuestions([emptyQuestion(1)]);
    setSelectedCourseId("");
    setError("");
  };

  const updateQuestion = (
    questionId: number,
    updater: (question: QuestionDraft) => QuestionDraft
  ) => {
    setQuestions((current) =>
      current.map((question) =>
        question.id === questionId ? updater(question) : question
      )
    );
  };

  const submit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    const form = new FormData(event.currentTarget);

    const title = String(form.get("title") ?? "").trim();
    if (!title || title.length < 2) {
      setError("Quiz title must be at least 2 characters.");
      return;
    }

    const invalidQuestion = questions.some(
      (question) =>
        !question.question.trim() ||
        question.options.some((option) => !option.trim())
    );

    if (invalidQuestion) {
      setError("Complete the question and all four options before creating the quiz.");
      return;
    }

    setSaving(true);
    setError("");
    try {
      const courseId = Number(form.get("courseId"));
      if (!Number.isInteger(courseId) || courseId <= 0) {
        setError("Please choose a course for this quiz.");
        return;
      }
      const description = String(form.get("description") ?? "").trim();
      const duration = Number(form.get("duration")) || 15;
      const maxMarks = Number(form.get("maxMarks")) || questions.length * 5;
      const passingMarks = Number(form.get("passingMarks"));

      if (!Number.isFinite(passingMarks) || passingMarks < 0 || passingMarks > maxMarks) {
        setError("Passing marks must be between 0 and the maximum marks.");
        return;
      }

      const newQuiz = await api.quizzes.create({
        course_id: courseId,
        title,
        description,
        duration_minutes: duration,
        max_marks: maxMarks,
        passing_marks: passingMarks,
        is_published: true,
      });

      const quizId = newQuiz.quiz_id;

      // Add each question
      for (const q of questions) {
        await api.quizzes.addQuestion(quizId, {
          question_text: q.question.trim(),
          question_type: "multiple_choice",
          marks: Math.max(1, Number((maxMarks / questions.length).toFixed(2))),
          options: q.options.map((opt, idx) => ({
            option_text: opt.trim(),
            is_correct: idx === q.answerIndex,
          })),
        });
      }

      showSuccess("Quiz created successfully.");
      setOpen(false);
      setQuestions([emptyQuestion(1)]);

      if (typeof window !== "undefined") {
        window.dispatchEvent(new CustomEvent("learnsphere:refresh", { detail: { action: "create-quiz" } }));
      }
    } catch (err: any) {
      console.error("Failed to build quiz:", err);
      setError(err.message || "Unable to create quiz. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  return (
    <>
      <button
        type="button"
        onClick={() => { setError(""); setOpen(true); }}
        className="primary-button"
      >
        <Plus size={17} />
        Quiz Builder
      </button>

      {open && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4 backdrop-blur-sm">
          <button
            type="button"
            className="absolute inset-0"
            onClick={close}
            aria-label="Close Quiz Builder"
          />

          <div className="card relative z-10 max-h-[92vh] w-full max-w-3xl overflow-y-auto p-6 shadow-2xl">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold">Quiz Builder</h2>
                <p className="mt-1 text-sm text-slate-500">
                  Create a quiz and attach questions directly to a course.
                </p>
              </div>

              <button
                type="button"
                className="icon-button"
                onClick={close}
                disabled={saving}
                aria-label="Close Quiz Builder"
              >
                <X size={17} />
              </button>
            </div>

            <form onSubmit={submit} className="mt-6 space-y-6">
              <InlineError message={error} />
              <div className="grid gap-4 sm:grid-cols-2">
                <label className="block sm:col-span-2">
                  <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                    Quiz Title
                  </span>
                  <input
                    name="title"
                    required
                    minLength={2}
                    maxLength={150}
                    placeholder="Enter quiz title"
                    className="w-full rounded-xl border border-(--border) bg-white px-3 py-2.5 text-sm outline-none focus:border-indigo-300"
                  />
                </label>

                <label className="block">
                  <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                    Course
                  </span>
                  <select
                    name="courseId"
                    required
                    value={selectedCourseId}
                    onChange={(event) => setSelectedCourseId(event.target.value)}
                    disabled={courses.length === 0}
                    className="w-full rounded-xl border border-(--border) bg-white px-3 py-2.5 text-sm outline-none focus:border-indigo-300"
                  >
                    {courses.map((course) => (
                      <option key={course.course_id} value={course.course_id}>
                        {course.course_name} - {course.course_id}
                      </option>
                    ))}
                    {courses.length === 0 && <option value="">No courses available</option>}
                  </select>
                </label>

                <label className="block">
                  <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                    Duration (Minutes)
                  </span>
                  <input
                    name="duration"
                    type="number"
                    defaultValue={15}
                    min={1}
                    className="w-full rounded-xl border border-(--border) bg-white px-3 py-2.5 text-sm outline-none focus:border-indigo-300"
                  />
                </label>

                <label className="block">
                  <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                    Maximum Marks
                  </span>
                  <input
                    name="maxMarks"
                    type="number"
                    defaultValue={questions.length * 5}
                    min={1}
                    className="w-full rounded-xl border border-(--border) bg-white px-3 py-2.5 text-sm outline-none focus:border-indigo-300"
                  />
                </label>

                <label className="block">
                  <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                    Passing Marks
                  </span>
                  <input
                    name="passingMarks"
                    type="number"
                    defaultValue={Math.ceil(questions.length * 3)}
                    min={0}
                    className="w-full rounded-xl border border-(--border) bg-white px-3 py-2.5 text-sm outline-none focus:border-indigo-300"
                  />
                </label>
              </div>

              <div className="space-y-4 border-t border-(--border) pt-6">
                <div className="flex items-center justify-between">
                  <h3 className="font-bold">Questions ({questions.length})</h3>

                  <button
                    type="button"
                    onClick={() =>
                      setQuestions((current) => [
                        ...current,
                        emptyQuestion(Math.max(0, ...current.map((q) => q.id)) + 1),
                      ])
                    }
                    className="secondary-button text-xs"
                  >
                    <Plus size={15} />
                    Add Question
                  </button>
                </div>

                {questions.map((question, qIndex) => (
                  <div
                    key={question.id}
                    className="rounded-2xl border border-(--border) p-4 space-y-3"
                  >
                    <div className="flex items-center justify-between gap-3">
                      <span className="text-xs font-bold uppercase tracking-wider text-slate-400">
                        Question {qIndex + 1}
                      </span>

                      {questions.length > 1 && (
                        <button
                          type="button"
                          onClick={() =>
                            setQuestions((current) =>
                              current.filter((item) => item.id !== question.id)
                            )
                          }
                          className="text-rose-500 hover:text-rose-700 transition"
                          aria-label="Remove question"
                        >
                          <Trash2 size={16} />
                        </button>
                      )}
                    </div>

                    <input
                      value={question.question}
                      maxLength={1000}
                      onChange={(e) =>
                        updateQuestion(question.id, (q) => ({
                          ...q,
                          question: e.target.value,
                        }))
                      }
                      placeholder="Enter question text..."
                      required
                      className="w-full rounded-xl border border-(--border) bg-white px-3 py-2 text-sm outline-none focus:border-indigo-300"
                    />

                    <div className="grid gap-2 sm:grid-cols-2 pt-2">
                      {question.options.map((opt, optIndex) => (
                        <label
                          key={optIndex}
                          className="flex items-center gap-2 rounded-xl border border-(--border) bg-slate-50 px-3 py-2 text-xs"
                        >
                          <input
                            type="radio"
                            name={`answer-${question.id}`}
                            checked={question.answerIndex === optIndex}
                            onChange={() =>
                              updateQuestion(question.id, (q) => ({
                                ...q,
                                answerIndex: optIndex,
                              }))
                            }
                            className="accent-indigo-600"
                          />
                          <input
                            value={opt}
                            maxLength={500}
                            onChange={(e) =>
                              updateQuestion(question.id, (q) => {
                                const next = [...q.options];
                                next[optIndex] = e.target.value;
                                return { ...q, options: next };
                              })
                            }
                            placeholder={`Option ${optIndex + 1}`}
                            required
                            className="w-full bg-transparent outline-none text-xs"
                          />
                        </label>
                      ))}
                    </div>
                  </div>
                ))}
              </div>

              <div className="flex justify-end gap-2 border-t border-(--border) pt-4">
                <button
                  type="button"
                  onClick={close}
                  disabled={saving}
                  className="secondary-button"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={saving || courses.length === 0}
                  className="primary-button"
                >
                  {saving ? "Creating Quiz..." : "Create Quiz"}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </>
  );
}
