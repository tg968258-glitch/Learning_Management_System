import { CoursesGrid } from "@/components/features/CoursesGrid";
import { ActionDialogButton, PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader
        title="Courses"
        actions={
          <ActionDialogButton
            action="create-course"
            label="Create course"
          />
        }
      />

      <CoursesGrid
        role="admin"
      />
    </>
  );
}
