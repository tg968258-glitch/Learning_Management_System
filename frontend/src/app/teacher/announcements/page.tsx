import { CommunicationCards } from "@/components/features/CommunicationCards";
import { ActionDialogButton, PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader
        title="Announcements"
        actions={
          <ActionDialogButton
            action="new-announcement"
            label="New Announcement"
          />
        }
      />

      <CommunicationCards
        type="announcements"
      />
    </>
  );
}
