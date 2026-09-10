"use client";

import { useParams } from "next/navigation";
import { CourseDetail } from "@/components/features/CourseDetail";

export default function Page() {
  const params = useParams<{ courseId: string }>();

  return (
    <CourseDetail
      role="student"
      courseId={Number(params.courseId)}
    />
  );
}
