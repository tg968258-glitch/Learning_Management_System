const DEFAULT_ERROR_MESSAGE = "Something went wrong. Please try again.";

const TECHNICAL_ERROR_PATTERN =
  /traceback|stack trace|sql(state)?|database|constraint|exception|internal server|typeerror|referenceerror|undefined|null value|foreign key|duplicate key|localhost:\d+|https?:\/\//i;

const MESSAGE_RULES: Array<{ pattern: RegExp; message: string }> = [
  {
    pattern: /active invitation.*(already )?exists|invitation.*already.*(active|sent)|already invited/i,
    message: "An active invitation already exists for this email. Please wait for it to expire or ask the teacher to use the existing invitation.",
  },
  {
    pattern: /email.*(already exists|already registered|in use)|user.*already exists/i,
    message: "An account already exists with this email. Try signing in or use a different email.",
  },
  {
    pattern: /invalid.*(credential|password)|incorrect.*(credential|password)|email or password/i,
    message: "The email or password is incorrect. Please check your details and try again.",
  },
  {
    pattern: /token.*expired|expired.*token|invitation.*expired/i,
    message: "This invitation has expired. Please ask an administrator to send a new one.",
  },
  {
    pattern: /invalid.*token|invitation.*invalid/i,
    message: "This invitation link is invalid. Please check the link or request a new invitation.",
  },
  {
    pattern: /not authenticated|session.*expired|unauthorized/i,
    message: "Your session has expired. Please sign in again.",
  },
  {
    pattern: /permission|forbidden|not allowed/i,
    message: "You do not have permission to perform this action.",
  },
  {
    pattern: /course (does not exist|not found)/i,
    message: "The selected course is no longer available. Please choose another course.",
  },
  {
    pattern: /student (does not exist|not found)/i,
    message: "The selected student is no longer available. Please choose another student.",
  },
  {
    pattern: /teacher (does not exist|not found)/i,
    message: "The selected teacher is no longer available. Please choose another teacher.",
  },
  {
    pattern: /module (does not exist|not found)/i,
    message: "The selected module is no longer available. Please choose another module.",
  },
  {
    pattern: /lesson (does not exist|not found)/i,
    message: "The selected lesson is no longer available. Please choose another lesson.",
  },
  {
    pattern: /network|failed to fetch|load failed|unable to connect/i,
    message: "We could not connect to LearnSphere. Check your internet connection and try again.",
  },
];

const STATUS_MESSAGES: Record<number, string> = {
  400: "Some information is missing or invalid. Please review the form and try again.",
  401: "Your session has expired. Please sign in again.",
  403: "You do not have permission to perform this action.",
  404: "The requested item could not be found. It may have been removed.",
  408: "The request took too long. Please check your connection and try again.",
  409: "This change conflicts with existing information. Please refresh and try again.",
  413: "This file is too large. Please choose a smaller file and try again.",
  422: "Some information is invalid. Please check the highlighted fields and try again.",
  429: "Too many attempts were made. Please wait a moment and try again.",
};

function cleanMessage(message: string) {
  return message
    .replace(/^error:\s*/i, "")
    .replace(/^\[object Object\]$/i, "")
    .replace(/\s+/g, " ")
    .trim();
}

export function getUserFacingErrorMessage(
  error: unknown,
  fallback = DEFAULT_ERROR_MESSAGE,
  status?: number
): string {
  const raw =
    typeof error === "string"
      ? error
      : error instanceof Error
        ? error.message
        : "";
  const message = cleanMessage(raw);

  for (const rule of MESSAGE_RULES) {
    if (rule.pattern.test(message)) return rule.message;
  }

  if (status && status >= 500) {
    return "LearnSphere is having trouble completing this request. Please try again in a moment.";
  }

  if (!message || TECHNICAL_ERROR_PATTERN.test(message)) {
    return (status && STATUS_MESSAGES[status]) || fallback;
  }

  // Preserve already-readable backend messages while preventing excessively long
  // responses from taking over the notification area.
  if (message.length <= 220) return message;

  return (status && STATUS_MESSAGES[status]) || fallback;
}
