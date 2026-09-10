import { EnrollmentsTable } from "@/components/features/EnrollmentsTable";
import { PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader title="Enrollments" />

      <EnrollmentsTable />
    </>
  );
}
