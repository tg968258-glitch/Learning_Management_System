import { ContentManager } from "@/components/features/ContentManager";
import { PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader
        title="Modules & Lessons"
      />

      <ContentManager
        role="teacher"
      />
    </>
  );
}
