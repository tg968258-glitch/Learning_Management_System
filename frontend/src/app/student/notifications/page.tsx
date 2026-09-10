import { NotificationList } from "@/components/features/NotificationList";
import { PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader
        title="Notifications"
      />

      <NotificationList />
    </>
  );
}
