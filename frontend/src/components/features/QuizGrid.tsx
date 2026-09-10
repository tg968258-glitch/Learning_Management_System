"use client";

import { useCallback, useEffect, useState } from "react";
import { CheckCircle2, Loader2, PlayCircle, Trash2, X } from "lucide-react";
import { api } from "@/lib/api";
import { showSuccess } from "@/context/FeedbackContext";
import { ActionDialogButton, InlineError, StatusBadge } from "@/components/ui";
import type { Role } from "@/types/role";
import { GridSkeleton } from "@/components/ui/Skeleton";

export function QuizGrid({ role }: { role: Role }) {
  const [quizzes, setQuizzes] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedQuiz, setSelectedQuiz] = useState<any | null>(null);
  const [currentAttempt, setCurrentAttempt] = useState<any | null>(null);
  const [selectedOptions, setSelectedOptions] = useState<Record<number, number>>({});
  const [attemptSubmitting, setAttemptSubmitting] = useState(false);
  const [attemptStarting, setAttemptStarting] = useState(false);
  const [attemptResult, setAttemptResult] = useState<any | null>(null);
  const [error, setError] = useState("");

  const fetchQuizzes = useCallback(async () => {
    try {
      setError("");
      const courses = role === "admin"
        ? await api.courses.getAll()
        : await api.courses.getMyCourses();
      if (Array.isArray(courses)) {
        const quizPromises = courses.map((c: any) =>
          api.quizzes.getByCourse(c.course_id).catch(() => [])
        );
        const results = await Promise.all(quizPromises);
        const flat = results.flatMap((courseQuizzes, index) =>
          (Array.isArray(courseQuizzes) ? courseQuizzes : []).map((quiz: any) => ({
            ...quiz,
            course_id: courses[index].course_id,
            course_name: courses[index].course_name,
          }))
        ).filter(Boolean);
        setQuizzes(flat);
      } else {
        setQuizzes([]);
      }
    } catch (err) {
      console.error("Failed to load quizzes:", err);
      setQuizzes([]);
      setError("Unable to load quizzes. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [role]);

  useEffect(() => {
    fetchQuizzes();
  }, [fetchQuizzes]);

  useEffect(() => {
    const handleRefresh = (event: Event) => {
      const detail = (event as CustomEvent<{ action?: string }>).detail;
      if (!detail?.action || detail.action.includes("quiz")) {
        fetchQuizzes();
      }
    };

    window.addEventListener("learnsphere:refresh", handleRefresh);
    return () => window.removeEventListener("learnsphere:refresh", handleRefresh);
  }, [fetchQuizzes]);

  const handleOpenQuiz = async (quiz: any) => {
    try {
      setError("");
      const detailed = await api.quizzes.getById(quiz.quiz_id);
      setSelectedQuiz({ ...(detailed || quiz), course_id: quiz.course_id, course_name: quiz.course_name });
      setSelectedOptions({});
      setCurrentAttempt(null);
      if (role === "student") {
        const attempts = await api.quizzes.getMyAttempts(quiz.quiz_id);
        const submittedAttempts = (Array.isArray(attempts) ? attempts : []).filter(
          (attempt: any) => Boolean(attempt.submitted_at) || attempt.status === "completed"
        );
        setAttemptResult(submittedAttempts.at(-1) ?? null);
      } else {
        setAttemptResult(null);
      }
    } catch (err: any) {
      setError(err.message || "Unable to open quiz.");
    }
  };

  const handleStartAttempt = async () => {
    if (!selectedQuiz) return;
    setAttemptStarting(true);
    setError("");
    try {
      const attempt = await api.quizzes.startAttempt(selectedQuiz.quiz_id);
      setCurrentAttempt(attempt);
      setSelectedOptions({});
    } catch (err: any) {
      setError(err.message || "Unable to start quiz attempt.");
    } finally {
      setAttemptStarting(false);
    }
  };

  const handleSubmitAttempt = async () => {
    if (!currentAttempt || !selectedQuiz) return;

    if (Object.keys(selectedOptions).length !== selectedQuiz.questions?.length) {
      setError("Answer every question before submitting the quiz.");
      return;
    }

    const formattedAnswers = Object.entries(selectedOptions).map(([qId, optId]) => ({
      question_id: Number(qId),
      selected_option_id: Number(optId),
    }));

    setAttemptSubmitting(true);
    setError("");
    try {
      const result = await api.quizzes.submitAttempt(currentAttempt.attempt_id, formattedAnswers);
      setAttemptResult(result);
      showSuccess("Quiz submitted successfully.");
    } catch (err: any) {
      setError(err.message || "Unable to submit quiz. Please try again.");
    } finally {
      setAttemptSubmitting(false);
    }
  };

  const closeQuiz = () => {
    setSelectedQuiz(null);
    setCurrentAttempt(null);
    setSelectedOptions({});
    setAttemptResult(null);
    setError("");
  };

  const handleDeleteQuiz = async () => {
    if (!selectedQuiz || !window.confirm("Delete this quiz?")) return;
    try {
      setError("");
      await api.quizzes.delete(selectedQuiz.quiz_id);
      showSuccess("Quiz deleted successfully.");
      closeQuiz();
      await fetchQuizzes();
    } catch (err: any) {
      setError(err.message || "Unable to delete quiz.");
    }
  };

  const renderQuestions = (interactive: boolean) => (
    <div className="space-y-4">
      {selectedQuiz?.questions?.length ? selectedQuiz.questions.map((question: any, index: number) => (
        <div key={question.question_id || index} className="rounded-2xl border border-(--border) p-4">
          <div className="flex items-start justify-between gap-3 text-sm font-semibold text-slate-900">
            <span>{index + 1}. {question.question_text}</span>
            <span className="shrink-0 text-xs font-medium text-slate-400">{question.marks} marks</span>
          </div>
          <div className="mt-3 space-y-2">
            {question.options?.map((option: any) => {
              const selected = interactive && selectedOptions[question.question_id] === option.option_id;
              return (
                <label
                  key={option.option_id}
                  className={`flex items-center gap-3 rounded-xl border p-3 text-sm ${
                    selected
                      ? "border-indigo-600 bg-indigo-50/50 font-medium text-indigo-950"
                      : !interactive && option.is_correct
                        ? "border-emerald-300 bg-emerald-50 text-emerald-900"
                        : "border-(--border) bg-white text-slate-700"
                  } ${interactive ? "cursor-pointer hover:bg-slate-50" : "cursor-default"}`}
                >
                  <input
                    type="radio"
                    name={`question-${question.question_id}`}
                    checked={interactive ? selected : Boolean(option.is_correct)}
                    disabled={!interactive}
                    onChange={() => interactive && setSelectedOptions((previous) => ({
                      ...previous,
                      [question.question_id]: option.option_id,
                    }))}
                    className="accent-indigo-600"
                  />
                  <span>{option.option_text}</span>
                  {!interactive && option.is_correct && (
                    <span className="ml-auto text-xs font-semibold text-emerald-700">Correct answer</span>
                  )}
                </label>
              );
            })}
          </div>
        </div>
      )) : (
        <div className="p-6 text-center text-sm text-slate-400">
          No questions have been configured for this quiz yet.
        </div>
      )}
    </div>
  );

  if (loading) {
    return <GridSkeleton />;
  }

  return (
    <>
      {!selectedQuiz && <InlineError message={error} className="mb-4" />}
      {quizzes.length > 0 ? (
        <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {quizzes.map((quiz, index) => (
            <button
              key={quiz.quiz_id || index}
              type="button"
              onClick={() => handleOpenQuiz(quiz)}
              className="card p-5 text-left transition hover:-translate-y-0.5 hover:border-indigo-200 hover:shadow-lg"
            >
              <div className="flex items-center justify-between">
                <div className="grid h-11 w-11 place-items-center rounded-xl bg-amber-50 font-bold text-amber-600">
                  Q{index + 1}
                </div>
                <StatusBadge status={quiz.is_published ? "Active" : "Draft"} />
              </div>

              <h3 className="mt-5 font-bold text-slate-900">{quiz.title}</h3>

              <p className="mt-1 text-xs text-slate-500 line-clamp-1">
                {quiz.description || "Course Assessment"}
              </p>
              <p className="mt-2 text-xs font-semibold text-indigo-600">
                {quiz.course_name} · Course {quiz.course_id}
              </p>

              <div className="mt-4 flex items-center justify-between text-xs text-slate-500 border-t border-(--border) pt-3">
                <span>{quiz.duration_minutes ?? 15} mins</span>
                <span className="font-semibold text-(--brand)">{quiz.max_marks ?? 20} pts</span>
              </div>
            </button>
          ))}
        </div>
      ) : (
        <div className="card p-12 text-center text-sm text-slate-500">
          No quizzes available yet.
        </div>
      )}

      {selectedQuiz && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4 backdrop-blur-sm">
          <button
            type="button"
            className="absolute inset-0"
            onClick={closeQuiz}
            aria-label="Close quiz modal"
          />

          <div className="card relative z-10 max-h-[90vh] w-full max-w-2xl overflow-y-auto p-6 shadow-2xl">
            <InlineError message={error} className="mb-4" />
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold">{selectedQuiz.title}</h2>
                <p className="mt-1 text-xs text-slate-500">
                  {selectedQuiz.course_name} · Course {selectedQuiz.course_id} · Duration: {selectedQuiz.duration_minutes ?? 15} min · Max Marks: {selectedQuiz.max_marks ?? 20}
                </p>
              </div>

              <button
                type="button"
                className="icon-button"
                onClick={closeQuiz}
                aria-label="Close quiz modal"
              >
                <X size={17} />
              </button>
            </div>

            {attemptResult ? (
              <div className="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-6 text-center">
                <CheckCircle2 size={36} className="mx-auto text-emerald-600" />
                <h3 className="mt-3 text-lg font-bold text-emerald-950">Quiz Completed</h3>
                <div className="mt-2 text-2xl font-bold text-emerald-700">
                  Score: {attemptResult.marks ?? 0} / {selectedQuiz.max_marks ?? 20}
                </div>
                <p className="mt-1 text-xs text-emerald-800">
                  {attemptResult.passed ? "Status: PASSED" : "Status: NOT PASSED"}
                </p>
                <button
                  type="button"
                  onClick={closeQuiz}
                  className="primary-button mt-5"
                >
                  Done
                </button>
              </div>
            ) : currentAttempt ? (
              <div className="mt-5 space-y-6">
                {renderQuestions(true)}

                <div className="flex justify-end gap-2 border-t border-(--border) pt-4">
                  <button type="button" onClick={closeQuiz} className="secondary-button">
                    Cancel
                  </button>
                  <button
                    type="button"
                    onClick={handleSubmitAttempt}
                    disabled={attemptSubmitting || !selectedQuiz.questions?.length}
                    className="primary-button"
                  >
                    {attemptSubmitting ? "Submitting..." : "Submit Answers"}
                  </button>
                </div>
              </div>
            ) : (
              <div className="mt-6 space-y-4">
                <p className="text-sm leading-6 text-slate-600">
                  {selectedQuiz.description || "This quiz evaluates your understanding of key course concepts."}
                </p>

                {role !== "student" && renderQuestions(false)}

                {role === "student" && (
                  <button
                    type="button"
                    onClick={handleStartAttempt}
                    disabled={attemptStarting}
                    className="primary-button w-full justify-center py-3"
                  >
                    {attemptStarting ? <Loader2 size={18} className="animate-spin" /> : <PlayCircle size={18} />}
                    {attemptStarting ? "Starting..." : "Start Quiz Attempt"}
                  </button>
                )}
              </div>
            )}
            {role !== "student" && (
              <div className="mt-5 flex justify-end gap-2 border-t border-(--border) pt-4">
                <button type="button" onClick={handleDeleteQuiz} className="secondary-button text-rose-600">
                  <Trash2 size={15} /> Delete
                </button>
                <ActionDialogButton
                  action="edit-quiz"
                  label="Edit quiz"
                  variant="secondary"
                  compact
                  initialValues={{
                    quizId: String(selectedQuiz.quiz_id),
                    title: selectedQuiz.title,
                    duration: String(selectedQuiz.duration_minutes ?? 15),
                    maxMarks: String(selectedQuiz.max_marks ?? 20),
                  }}
                  onSuccess={() => { closeQuiz(); fetchQuizzes(); }}
                />
              </div>
            )}
          </div>
        </div>
      )}
    </>
  );
}
