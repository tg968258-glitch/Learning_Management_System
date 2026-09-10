# LearnSphere LMS Frontend

Frontend-only LMS prototype built with Next.js App Router, TypeScript, Tailwind CSS, React and Lucide icons.

## Run locally

```bash
npm install
npm run dev
```

Open `http://localhost:3000`. The sign-in screen is intentionally inactive until backend authentication is connected. Use **Open developer preview** to enter the Admin, Teacher or Student UI.

## Frontend preview behavior

The prototype now supports client-side navigation, global and table search, filters, pagination, profile editing, password-change validation, active/inactive status editing, teacher qualification selection, course/teacher/enrollment/assignment/quiz/session/announcement/discussion/module/lesson mock creation and editing, notification read state, quiz attempts and other UI interactions.

Preview changes are stored in browser `localStorage`, so they survive route changes and reloads on the same browser. This temporary storage is intentionally isolated from backend integration and can later be replaced by API responses and database writes. Clear the site's local storage to reset the preview data.

## Frontend preview behavior
- Students self-register from the login screen; Admin does not manually add student accounts.
- Forgot-password, local profile editing, filters, pagination, status changes, quiz attempts, quiz creation with questions, sessions, assignments and other preview actions work without a backend using browser local storage where appropriate.
- The real sign-in/authentication request is intentionally left for backend integration.
