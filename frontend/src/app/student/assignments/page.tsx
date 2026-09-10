import { AssignmentTable } from "@/components/features/AssignmentTable";
import { PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader
        title="Assignments"
      />

      <AssignmentTable
        role="student"
      />
    </>
  );
}
