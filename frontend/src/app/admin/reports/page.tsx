import { StudentReports } from "@/components/features/StudentReports";
import { PageHeader } from "@/components/ui";

export default function Page() {
  return <>
    <PageHeader title="Student Reports" description="Review enrolments, progress, submissions, and results across all students." />
    <StudentReports />
  </>;
}
