import { PeopleTable } from "@/components/features/PeopleTable";
import { PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader
        title="Students"
      />

      <PeopleTable
        kind="students"
      />
    </>
  );
}
