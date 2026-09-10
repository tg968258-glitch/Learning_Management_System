import { AssignmentTable } from "@/components/features/AssignmentTable";
import { ActionDialogButton, PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader
        title="Assignments"
        description="Create and manage assignment instructions, marks, and deadlines."
        actions={
          <ActionDialogButton
            action="new-assignment"
            label="New Assignment"
          />
        }
      />

      <AssignmentTable
        role="teacher"
      />
    </>
  );
}
