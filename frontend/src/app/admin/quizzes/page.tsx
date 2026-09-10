import { QuizGrid } from "@/components/features/QuizGrid";
import { QuizBuilderButton } from "@/components/features/QuizBuilderButton";
import { PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader
        title="Quizzes"
        description="Create and manage course quizzes."
        actions={<QuizBuilderButton />}
      />

      <QuizGrid role="admin" />
    </>
  );
}
