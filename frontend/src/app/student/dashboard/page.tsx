import { DashboardOverview } from "@/components/features/DashboardOverview";
import { PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader
        title="Dashboard"
      />

      <DashboardOverview
        role="student"
      />
    </>
  );
}
