import { CommunicationCards } from "@/components/features/CommunicationCards";
import { ActionDialogButton, PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader
        title="Discussions"
        actions={
          <ActionDialogButton
            action="new-discussion"
            label="New Discussion"
          />
        }
      />

      <CommunicationCards
        type="discussions"
      />
    </>
  );
}
