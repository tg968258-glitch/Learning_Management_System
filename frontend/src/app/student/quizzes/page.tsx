import { QuizGrid } from "@/components/features/QuizGrid";
import { PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader
        title="Quizzes"
      />

      <QuizGrid
        role="student"
      />
    </>
  );
}
