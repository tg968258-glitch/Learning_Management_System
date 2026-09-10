import { ProfilePage } from "@/components/features/ProfilePage";
import { PageHeader } from "@/components/ui";

export default function Page() {
  return (
    <>
      <PageHeader title="My Profile" />
      <ProfilePage role="teacher" />
    </>
  );
}
