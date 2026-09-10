import { AuditLogList } from "@/components/features/AuditLogList";
import { PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader
        title="Audit Logs"
      />

      <AuditLogList />
    </>
  );
}
