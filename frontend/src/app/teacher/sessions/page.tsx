import { SessionsGrid } from "@/components/features/SessionsGrid";
import { ActionDialogButton, PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader
        title="Class Sessions"
        actions={
          <ActionDialogButton
            action="schedule-session"
            label="Schedule Session"
          />
        }
      />

      <SessionsGrid
        role="teacher"
      />
    </>
  );
}
