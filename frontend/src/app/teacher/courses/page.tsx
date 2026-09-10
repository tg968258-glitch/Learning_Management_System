import { CoursesGrid } from "@/components/features/CoursesGrid";
import { PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader
        title="My Courses"
      />

      <CoursesGrid
        role="teacher"
      />
    </>
  );
}
