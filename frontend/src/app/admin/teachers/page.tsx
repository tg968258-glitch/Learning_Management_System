import { PeopleTable } from "@/components/features/PeopleTable";
import { ActionDialogButton, PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader
        title="Teachers"
        actions={
          <ActionDialogButton
            action="invite-teacher"
            label="Invite Teacher"
          />
        }
      />

      <PeopleTable kind="teachers" />
    </>
  );
}
