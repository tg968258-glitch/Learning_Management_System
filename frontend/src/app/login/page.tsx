"use client";

import Link from "next/link";
import { FormEvent, Suspense, useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import {
  BookOpenCheck,
  CheckCircle2,
  Eye,
  EyeOff,
  Loader2,
  LockKeyhole,
  Mail,
  UserRoundPlus,
  X,
} from "lucide-react";

import { api } from "@/lib/api";

type AuthDialog = "register" | "forgot" | null;

function LoginContent() {
  const router = useRouter();

  const [showPassword, setShowPassword] = useState(false);
  const [identifier, setIdentifier] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);

  const [dialog, setDialog] = useState<AuthDialog>(null);
  const [message, setMessage] = useState("");
  const [successMessage, setSuccessMessage] = useState("");

  const [registerType, setRegisterType] =
    useState<"student" | "teacher">("student");

  const [registerDone, setRegisterDone] = useState(false);

  const [inviteToken, setInviteToken] = useState("");
  const [inviteEmail, setInviteEmail] = useState("");
  const [inviteLoading, setInviteLoading] = useState(false);
  const [inviteValidationError, setInviteValidationError] = useState("");

  const [forgotStep, setForgotStep] = useState<1 | 2 | 3>(1);
  const [forgotEmail, setForgotEmail] = useState("");

  useEffect(() => {
    if (!inviteToken.trim()) {
      setInviteEmail("");
      setInviteLoading(false);
      setInviteValidationError("");
      return;
    }

    let active = true;
    setInviteLoading(true);
    setInviteEmail("");
    setInviteValidationError("");

    const timer = setTimeout(async () => {
      try {
        const details = await api.auth.getInvitationDetails(inviteToken.trim());
        if (active && details?.email) {
          setInviteEmail(details.email);
          setInviteValidationError("");
        }
      } catch (error) {
        if (active) {
          setInviteEmail("");
          setInviteValidationError(error instanceof Error ? error.message : "This invitation link is invalid.");
        }
      } finally {
        if (active) setInviteLoading(false);
      }
    }, 350);

    return () => {
      active = false;
      clearTimeout(timer);
    };
  }, [inviteToken]);

  const closeDialog = () => {
    setDialog(null);
    setMessage("");
    setSuccessMessage("");
    setRegisterDone(false);
    setInviteToken("");
    setInviteEmail("");
    setInviteValidationError("");
    setInviteLoading(false);
    setForgotStep(1);
    setForgotEmail("");
  };

  const handleLogin = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();

    setMessage("");
    setLoading(true);

    try {
      const response = await api.auth.login({
        email: identifier.trim(),
        password,
      });

      console.log("Login response:", response);

      /*
       * Supports these possible backend responses:
       *
       * {
       *   access_token: "...",
       *   role: "admin"
       * }
       *
       * {
       *   access_token: "...",
       *   user: {
       *     role: "admin"
       *   }
       * }
       *
       * {
       *   data: {
       *     access_token: "...",
       *     role: "admin"
       *   }
       * }
       */

      const result = response as any;

      const role = String(
        result?.user?.role ??
        result?.role ??
        result?.data?.user?.role ??
        result?.data?.role ??
        ""
      )
        .trim()
        .toLowerCase();

      if (!role) {
        console.error("User role missing from login response:", response);

        throw new Error(
          "Login succeeded but the backend did not return a user role."
        );
      }

      if (role === "admin") {
        router.replace("/admin/dashboard");
        return;
      }

      if (role === "teacher") {
        router.replace("/teacher/dashboard");
        return;
      }

      if (role === "student") {
        router.replace("/student/dashboard");
        return;
      }

      throw new Error(`Unsupported user role: ${role}`);
    } catch (error: unknown) {
      console.error("Login error:", error);

      if (error instanceof Error) {
        setMessage(error.message);
      } else {
        setMessage("Invalid credentials. Please try again.");
      }
    } finally {
      setLoading(false);
    }
  };

  const registerStudent = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setMessage("");

    const form = new FormData(event.currentTarget);

    const name = String(form.get("name") ?? "").trim();
    const username = String(form.get("username") ?? "").trim().toLowerCase();
    const email = String(form.get("email") ?? "").trim().toLowerCase();
    const pwd = String(form.get("password") ?? "");
    const confirmPassword = String(
      form.get("confirmPassword") ?? ""
    );

    if (!name || name.length < 2) {
      setMessage("Full name must be at least 2 characters.");
      return;
    }

    if (!username) {
      setMessage("Username is required.");
      return;
    }

    if (username.length < 3 || username.length > 50) {
      setMessage("Username must be between 3 and 50 characters.");
      return;
    }

    if (!/^[a-zA-Z0-9_.-]+$/.test(username)) {
      setMessage("Username can only contain letters, numbers, underscores, dots, and hyphens.");
      return;
    }

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email) {
      setMessage("Email is required.");
      return;
    }

    if (!emailRegex.test(email)) {
      setMessage("Please enter a valid email address.");
      return;
    }

    if (pwd.length < 8) {
      setMessage("Password must be at least 8 characters.");
      return;
    }

    if (!/[a-zA-Z]/.test(pwd) || !/[0-9]/.test(pwd)) {
      setMessage("Password must contain at least one letter and one number.");
      return;
    }

    if (pwd !== confirmPassword) {
      setMessage("Password and confirm password must match.");
      return;
    }

    try {
      setLoading(true);

      await api.auth.register({
        username,
        email,
        password: pwd,
        name,
        role: "student",
      });

      setRegisterDone(true);
    } catch (error: unknown) {
      if (error instanceof Error) {
        setMessage(error.message);
      } else {
        setMessage("Registration failed.");
      }
    } finally {
      setLoading(false);
    }
  };

  const acceptTeacherInvite = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setMessage("");

    const form = new FormData(event.currentTarget);

    const token = inviteToken.trim();
    const name = String(form.get("name") ?? "").trim();
    const phoneNumber = String(form.get("phoneNumber") ?? "").trim();
    const pwd = String(form.get("password") ?? "");
    const confirmPassword = String(
      form.get("confirmPassword") ?? ""
    );

    if (!token || !inviteEmail || inviteValidationError) {
      setMessage(inviteValidationError || "Enter the invitation token sent to your email.");
      return;
    }

    if (!name || name.length < 2) {
      setMessage("Full name must be at least 2 characters.");
      return;
    }

    if (phoneNumber && !/^\d{10}$/.test(phoneNumber)) {
      setMessage("Phone number must contain exactly 10 digits.");
      return;
    }

    if (pwd.length < 8) {
      setMessage("Password must be at least 8 characters.");
      return;
    }

    if (!/[a-zA-Z]/.test(pwd) || !/[0-9]/.test(pwd)) {
      setMessage("Password must contain at least one letter and one number.");
      return;
    }

    if (pwd !== confirmPassword) {
      setMessage("Password and confirm password must match.");
      return;
    }

    try {
      setLoading(true);

      await api.auth.acceptTeacherInvite({
        token,
        password: pwd,
        name,
        phone_number: phoneNumber || undefined,
      });

      setRegisterDone(true);
    } catch (error: unknown) {
      if (error instanceof Error) {
        setMessage(error.message);
      } else {
        setMessage("Failed to accept teacher invitation.");
      }
    } finally {
      setLoading(false);
    }
  };

  const requestReset = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setMessage("");
    setSuccessMessage("");

    const form = new FormData(event.currentTarget);

    const email = String(
      form.get("email") ?? ""
    ).trim().toLowerCase();

    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!email || !emailRegex.test(email)) {
      setMessage("Please enter a valid email address.");
      return;
    }

    setForgotEmail(email);

    try {
      setLoading(true);

      const response =
        await api.auth.forgotPassword(email);

      setSuccessMessage(
        response?.message ||
        "Reset OTP sent to your email."
      );

      setForgotStep(2);
    } catch (error: unknown) {
      if (error instanceof Error) {
        setMessage(error.message);
      } else {
        setMessage(
          "Failed to request password reset."
        );
      }
    } finally {
      setLoading(false);
    }
  };

  const resetPassword = async (
    event: FormEvent<HTMLFormElement>
  ) => {
    event.preventDefault();

    setMessage("");

    const form = new FormData(event.currentTarget);

    const code = String(
      form.get("code") ?? ""
    ).trim();

    const pwd = String(
      form.get("password") ?? ""
    );

    const confirmPassword = String(
      form.get("confirmPassword") ?? ""
    );

    if (!code || !/^\d{6}$/.test(code)) {
      setMessage("OTP must be exactly 6 digits.");
      return;
    }

    if (pwd.length < 8) {
      setMessage("Password must be at least 8 characters.");
      return;
    }

    if (!/[a-zA-Z]/.test(pwd) || !/[0-9]/.test(pwd)) {
      setMessage("Password must contain at least one letter and one number.");
      return;
    }

    if (pwd !== confirmPassword) {
      setMessage(
        "New password and confirm password must match."
      );
      return;
    }

    try {
      setLoading(true);

      await api.auth.resetPassword({
        email: forgotEmail,
        otp: code,
        new_password: pwd,
      });

      setForgotStep(3);
    } catch (error: unknown) {
      if (error instanceof Error) {
        setMessage(error.message);
      } else {
        setMessage("Failed to reset password.");
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="grid min-h-screen bg-white lg:grid-cols-[1.05fr_.95fr]">
      {/* LEFT SIDE */}

      <section className="relative hidden overflow-hidden bg-slate-950 p-12 text-white lg:flex lg:flex-col lg:justify-between">
        <div className="absolute inset-0 bg-linear-to-br from-indigo-600/35 via-transparent to-violet-500/20" />

        <div className="relative flex items-center gap-3">
          <span className="grid h-11 w-11 place-items-center rounded-2xl bg-white/10 ring-1 ring-white/15">
            <BookOpenCheck size={22} />
          </span>

          <div>
            <div className="text-lg font-bold">
              LearnSphere
            </div>

            <div className="text-xs text-white/55">
              Learning Management System
            </div>
          </div>
        </div>

        <div className="relative max-w-xl">
          <div className="mb-5 inline-flex rounded-full bg-white/10 px-3 py-1.5 text-xs font-semibold text-indigo-100 ring-1 ring-white/10">
            Modern learning, one workspace
          </div>

          <h1 className="text-5xl font-bold leading-[1.08] tracking-tight">
            Teach, learn and manage your academic
            journey.
          </h1>

          <p className="mt-6 max-w-lg text-base leading-7 text-slate-300">
            A focused LMS experience for
            administrators, instructors and students.
          </p>
        </div>

        <div />
      </section>

      {/* LOGIN SECTION */}

      <section className="flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-md">
          <div className="mb-9 lg:hidden">
            <div className="flex items-center gap-3">
              <span className="grid h-11 w-11 place-items-center rounded-2xl bg-(--brand) text-white">
                <BookOpenCheck size={22} />
              </span>

              <div>
                <div className="font-bold">
                  LearnSphere
                </div>

                <div className="text-xs text-slate-500">
                  Learning Management System
                </div>
              </div>
            </div>
          </div>

          <div className="text-xs font-bold uppercase tracking-[0.18em] text-(--brand)">
            Welcome back
          </div>

          <h2 className="mt-2 text-3xl font-bold tracking-tight text-slate-950">
            Sign in to your account
          </h2>

          <p className="mt-2 text-sm leading-6 text-slate-500">
            Enter your credentials to access your LMS
            account.
          </p>

          {message && !dialog && (
            <div className="mt-4 rounded-xl bg-rose-50 px-3 py-2.5 text-sm text-rose-600">
              {message}
            </div>
          )}

          <form
            onSubmit={handleLogin}
            className="mt-8 space-y-5"
          >
            {/* EMAIL */}

            <label className="block">
              <span className="mb-2 block text-sm font-semibold text-slate-700">
                Email
              </span>

              <div className="form-control">
                <Mail
                  size={18}
                  className="text-slate-400"
                />

                <input
                  type="text"
                  required
                  value={identifier}
                  onChange={(event) =>
                    setIdentifier(event.target.value)
                  }
                  className="w-full bg-transparent text-sm outline-none"
                  placeholder="Enter email or UID"
                  autoComplete="username"
                />
              </div>
            </label>

            {/* PASSWORD */}

            <label className="block">
              <span className="mb-2 block text-sm font-semibold text-slate-700">
                Password
              </span>

              <div className="form-control">
                <LockKeyhole
                  size={18}
                  className="text-slate-400"
                />

                <input
                  type={
                    showPassword
                      ? "text"
                      : "password"
                  }
                  required
                  value={password}
                  onChange={(event) =>
                    setPassword(event.target.value)
                  }
                  className="w-full bg-transparent text-sm outline-none"
                  placeholder="Enter password"
                  autoComplete="current-password"
                />

                <button
                  type="button"
                  className="text-slate-400"
                  onClick={() =>
                    setShowPassword(
                      (current) => !current
                    )
                  }
                  aria-label={
                    showPassword
                      ? "Hide password"
                      : "Show password"
                  }
                >
                  {showPassword ? (
                    <EyeOff size={17} />
                  ) : (
                    <Eye size={17} />
                  )}
                </button>
              </div>
            </label>

            <div className="flex items-center justify-between text-sm">
              <label className="flex items-center gap-2 text-slate-600">
                <input
                  type="checkbox"
                  defaultChecked
                  className="accent-indigo-600"
                />

                Remember me
              </label>

              <button
                type="button"
                onClick={() => {
                  setMessage("");
                  setDialog("forgot");
                }}
                className="font-semibold text-(--brand)"
              >
                Forgot password?
              </button>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="primary-button w-full justify-center py-3.5"
            >
              {loading
                ? "Signing in..."
                : "Sign in"}
            </button>
          </form>

          {/* REGISTER */}

          <div className="mt-6 border-t border-(--border) pt-6 text-center">
            <p className="text-sm text-slate-500">New user?</p>
            <button
              type="button"
              onClick={() => {
                setMessage("");
                setRegisterType("student");
                setDialog("register");
              }}
              className="mt-2 inline-flex items-center gap-2 font-semibold text-(--brand)"
            >
              <UserRoundPlus size={17} />
              Register
            </button>
          </div>
        </div>
      </section>

      {/* AUTH DIALOG */}

      {dialog && (
        <div className="fixed inset-0 z-50 grid place-items-center bg-slate-950/40 p-4 backdrop-blur-sm">
          <button
            type="button"
            className="absolute inset-0"
            onClick={closeDialog}
            aria-label="Close dialog"
          />

          <div className="card relative z-10 max-h-[92vh] w-full max-w-lg overflow-y-auto p-6 shadow-2xl">
            <div className="flex items-start justify-between gap-4">
              <div>
                <h2 className="text-xl font-bold">
                  {dialog === "register"
                    ? "User Registration"
                    : "Forgot Password"}
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  {dialog === "register"
                    ? "Create your account to start learning or teaching."
                    : "Reset your password securely."}
                </p>
              </div>

              <button
                type="button"
                onClick={closeDialog}
                className="icon-button"
                aria-label="Close"
              >
                <X size={17} />
              </button>
            </div>

            {/* REGISTRATION */}

            {dialog === "register" &&
              !registerDone && (
                <div className="mt-4">
                  <div className="mb-4 flex gap-2 rounded-xl bg-slate-100 p-1 text-sm font-semibold">
                    <button
                      type="button"
                      onClick={() =>
                        setRegisterType("student")
                      }
                      className={`flex-1 rounded-lg py-1.5 transition ${registerType === "student"
                        ? "bg-white text-slate-900 shadow-xs"
                        : "text-slate-500"
                        }`}
                    >
                      Student
                    </button>

                    <button
                      type="button"
                      onClick={() =>
                        setRegisterType("teacher")
                      }
                      className={`flex-1 rounded-lg py-1.5 transition ${registerType === "teacher"
                        ? "bg-white text-slate-900 shadow-xs"
                        : "text-slate-500"
                        }`}
                    >
                      Teacher (Invite)
                    </button>
                  </div>

                  {registerType === "student" ? (
                    <form
                      onSubmit={registerStudent}
                      className="space-y-4"
                    >
                      <div className="grid gap-4 sm:grid-cols-2">
                        <label className="block">
                          <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                            Full name
                          </span>

                          <input
                            name="name"
                            required
                            placeholder="Enter full name"
                            className="w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300"
                          />
                        </label>

                        <label className="block">
                          <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                            Username
                          </span>

                          <input
                            name="username"
                            required
                            placeholder="Choose a username"
                            autoCapitalize="none"
                            autoCorrect="off"
                            className="w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300"
                          />
                        </label>
                      </div>

                      <label className="block">
                        <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                          Email
                        </span>

                        <input
                          name="email"
                          type="email"
                          required
                          placeholder="Enter email"
                          className="w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300"
                        />
                      </label>

                      <div className="grid gap-4 sm:grid-cols-2">
                        <label>
                          <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                            Password
                          </span>

                          <input
                            name="password"
                            type="password"
                            minLength={8}
                            required
                            placeholder="Create password (min 8 chars)"
                            className="w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300"
                          />
                        </label>

                        <label>
                          <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                            Confirm password
                          </span>

                          <input
                            name="confirmPassword"
                            type="password"
                            minLength={8}
                            required
                            placeholder="Confirm password"
                            className="w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300"
                          />
                        </label>
                      </div>

                      {message && (
                        <div className="rounded-xl bg-rose-50 px-3 py-2 text-sm text-rose-600">
                          {message}
                        </div>
                      )}

                      <div className="flex justify-end gap-2 border-t border-(--border) pt-4">
                        <button
                          type="button"
                          onClick={closeDialog}
                          className="secondary-button"
                        >
                          Cancel
                        </button>

                        <button
                          type="submit"
                          disabled={loading}
                          className="primary-button"
                        >
                          {loading
                            ? "Registering..."
                            : "Register"}
                        </button>
                      </div>
                    </form>
                  ) : (
                    <form onSubmit={acceptTeacherInvite} className="space-y-4">
                      <label className="block">
                        <span className="mb-1.5 flex items-center justify-between text-xs font-semibold text-slate-500">
                          <span>Invitation Token</span>
                          {inviteLoading && <span className="animate-pulse text-[11px] text-indigo-600">Verifying token...</span>}
                        </span>
                        <input
                          value={inviteToken}
                          onChange={(event) => setInviteToken(event.target.value)}
                          required
                          autoComplete="off"
                          placeholder="Enter invitation token"
                          className="w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300"
                        />
                      </label>

                      <label className="block">
                        <span className="mb-1.5 block text-xs font-semibold text-slate-500">Invited Email</span>
                        <input
                          type="email"
                          value={inviteEmail}
                          readOnly
                          placeholder="Email appears after token validation"
                          className="w-full cursor-not-allowed rounded-xl border border-(--border) bg-slate-50 px-3 py-2.5 text-sm text-slate-600 outline-none"
                        />
                      </label>

                      {inviteValidationError && (
                        <div className="rounded-xl bg-rose-50 px-3 py-2 text-sm text-rose-600">{inviteValidationError}</div>
                      )}

                      <div className="grid gap-4 sm:grid-cols-2">
                        <label className="block">
                          <span className="mb-1.5 block text-xs font-semibold text-slate-500">Full name</span>
                          <input name="name" required placeholder="Enter full name" className="w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300" />
                        </label>
                        <label className="block">
                          <span className="mb-1.5 block text-xs font-semibold text-slate-500">Phone Number</span>
                          <input
                            name="phoneNumber"
                            type="tel"
                            inputMode="numeric"
                            maxLength={10}
                            pattern="[0-9]{10}"
                            title="Phone number must be exactly 10 digits"
                            placeholder="Enter 10-digit phone number"
                            onInput={(event) => { event.currentTarget.value = event.currentTarget.value.replace(/\D/g, "").slice(0, 10); }}
                            className="w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300"
                          />
                        </label>
                      </div>

                      <div className="grid gap-4 sm:grid-cols-2">
                        <label>
                          <span className="mb-1.5 block text-xs font-semibold text-slate-500">Password</span>
                          <input name="password" type="password" minLength={8} required placeholder="Create password (min 8 chars)" className="w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300" />
                        </label>
                        <label>
                          <span className="mb-1.5 block text-xs font-semibold text-slate-500">Confirm password</span>
                          <input name="confirmPassword" type="password" minLength={8} required placeholder="Confirm password" className="w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300" />
                        </label>
                      </div>

                      {message && <div className="rounded-xl bg-rose-50 px-3 py-2 text-sm text-rose-600">{message}</div>}

                      <div className="flex justify-end gap-2 border-t border-(--border) pt-4">
                        <button type="button" onClick={closeDialog} className="secondary-button">Cancel</button>
                        <button
                          type="submit"
                          disabled={loading || inviteLoading || !inviteEmail || Boolean(inviteValidationError)}
                          className="primary-button"
                        >
                          {loading ? "Completing..." : "Complete Registration"}
                        </button>
                      </div>
                    </form>
                  )}
                </div>
              )}

            {/* REGISTRATION COMPLETE */}

            {registerDone && (
              <div className="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-5 text-center">
                <CheckCircle2
                  size={30}
                  className="mx-auto text-emerald-600"
                />

                <h3 className="mt-3 font-bold text-emerald-900">
                  Registration Complete
                </h3>

                <p className="mt-1 text-sm text-emerald-700">
                  Your account has been registered
                  successfully. You can now sign in
                  with your credentials.
                </p>

                <button
                  type="button"
                  onClick={closeDialog}
                  className="primary-button mt-4"
                >
                  Return to Sign In
                </button>
              </div>
            )}

            {/* FORGOT PASSWORD STEP 1 */}

            {dialog === "forgot" &&
              forgotStep === 1 && (
                <form
                  onSubmit={requestReset}
                  className="mt-6 space-y-4"
                >
                  <label className="block">
                    <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                      Registered Email
                    </span>

                    <input
                      name="email"
                      type="email"
                      required
                      placeholder="Enter registered email"
                      className="w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300"
                    />
                  </label>

                  {message && (
                    <div className="rounded-xl bg-rose-50 px-3 py-2 text-sm text-rose-600">
                      {message}
                    </div>
                  )}

                  <div className="flex justify-end gap-2 border-t border-(--border) pt-4">
                    <button
                      type="button"
                      onClick={closeDialog}
                      className="secondary-button"
                    >
                      Cancel
                    </button>

                    <button
                      type="submit"
                      disabled={loading}
                      className="primary-button"
                    >
                      {loading
                        ? "Sending..."
                        : "Send Reset Code"}
                    </button>
                  </div>
                </form>
              )}

            {/* FORGOT PASSWORD STEP 2 */}

            {dialog === "forgot" &&
              forgotStep === 2 && (
                <form
                  onSubmit={resetPassword}
                  className="mt-6 space-y-4"
                >
                  {successMessage && (
                    <div className="rounded-xl bg-indigo-50 px-3 py-2 text-sm text-indigo-700">
                      {successMessage}
                    </div>
                  )}

                  <label className="block">
                    <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                      Verification OTP
                    </span>

                    <input
                      name="code"
                      required
                      placeholder="Enter OTP from email/server"
                      className="w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300"
                    />
                  </label>

                  <div className="grid gap-4 sm:grid-cols-2">
                    <label>
                      <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                        New password
                      </span>

                      <input
                        name="password"
                        type="password"
                        minLength={6}
                        required
                        placeholder="Enter new password"
                        className="w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300"
                      />
                    </label>

                    <label>
                      <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                        Confirm password
                      </span>

                      <input
                        name="confirmPassword"
                        type="password"
                        minLength={6}
                        required
                        placeholder="Confirm password"
                        className="w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300"
                      />
                    </label>
                  </div>

                  {message && (
                    <div className="rounded-xl bg-rose-50 px-3 py-2 text-sm text-rose-600">
                      {message}
                    </div>
                  )}

                  <div className="flex justify-end gap-2 border-t border-(--border) pt-4">
                    <button
                      type="button"
                      onClick={() =>
                        setForgotStep(1)
                      }
                      className="secondary-button"
                    >
                      Back
                    </button>

                    <button
                      type="submit"
                      disabled={loading}
                      className="primary-button"
                    >
                      {loading
                        ? "Resetting..."
                        : "Reset Password"}
                    </button>
                  </div>
                </form>
              )}

            {/* FORGOT PASSWORD COMPLETE */}

            {dialog === "forgot" &&
              forgotStep === 3 && (
                <div className="mt-6 rounded-2xl border border-emerald-200 bg-emerald-50 p-5 text-center">
                  <CheckCircle2
                    size={30}
                    className="mx-auto text-emerald-600"
                  />

                  <h3 className="mt-3 font-bold text-emerald-900">
                    Password Reset Complete
                  </h3>

                  <p className="mt-1 text-sm text-emerald-700">
                    Your password has been reset
                    successfully.
                  </p>

                  <button
                    type="button"
                    onClick={closeDialog}
                    className="primary-button mt-4"
                  >
                    Return to Sign In
                  </button>
                </div>
              )}
          </div>
        </div>
      )}
    </main>
  );
}

export default function LoginPage() {
  return (
    <Suspense
      fallback={
        <div className="grid min-h-screen place-items-center bg-white text-slate-400">
          <Loader2 className="animate-spin text-(--brand)" size={32} />
        </div>
      }
    >
      <LoginContent />
    </Suspense>
  );
}
