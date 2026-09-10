import { SessionsGrid } from "@/components/features/SessionsGrid";
import { PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader
        title="Class Sessions"
      />

      <SessionsGrid
        role="student"
      />
    </>
  );
}
