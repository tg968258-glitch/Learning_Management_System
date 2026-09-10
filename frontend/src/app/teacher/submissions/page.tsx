import { AssignmentTable } from "@/components/features/AssignmentTable";
import { PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader
        title="Submissions"
        description="Select an assignment to review student work, grade it, and leave feedback."
      />

      <AssignmentTable
        role="teacher"
        submissions
      />
    </>
  );
}
