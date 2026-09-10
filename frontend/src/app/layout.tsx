import type { Metadata } from "next";
import "./globals.css";
import { FeedbackProvider } from "@/context/FeedbackContext";

export const metadata: Metadata = {
  title: "LearnSphere LMS",
  description: "Learning Management System UI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        <FeedbackProvider>
          {children}
        </FeedbackProvider>
      </body>
    </html>
  );
}
