"use client";

import { FormEvent, useCallback, useEffect, useState } from "react";
import { CheckCircle2, Loader2, Pencil, UserRound } from "lucide-react";
import { api, getStoredSession, setStoredSession } from "@/lib/api";
import { showSuccess } from "@/context/FeedbackContext";
import { InlineError } from "@/components/ui";
import type { Role } from "@/types/role";
import { PageSkeleton } from "@/components/ui/Skeleton";

const qualifications = [
  "B.Tech",
  "B.E.",
  "B.Sc",
  "BCA",
  "B.Ed",
  "B.Com",
  "B.A.",
  "M.Tech",
  "M.E.",
  "M.Sc",
  "MCA",
  "MBA",
  "M.Ed",
  "M.Com",
  "M.A.",
  "M.Phil",
  "Ph.D.",
];

export function ProfilePage({ role }: { role: Role }) {
  const canEdit = role !== "admin";
  const [profile, setProfile] = useState<any>({
    name: "",
    email: "",
    uid: "",
    detail: "",
    qualification: "M.Tech",
    specialization: "",
    experience: 0,
    phone_number: "",
    date_of_birth: "",
    gender: "",
  });
  const [editing, setEditing] = useState(false);
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const fetchProfile = useCallback(async () => {
    try {
      setError("");
      const storedUser = getStoredSession()?.user;
      if (role === "student") {
        const [studentRes, userRes] = await Promise.all([
          api.students.getMe().catch(() => null),
          api.users.getMe().catch(() => null),
        ]);
        const student = studentRes?.student || studentRes;
        const user = userRes?.user || userRes;

        setProfile({
          name: student?.name || user?.name || "Student User",
          email: student?.email || user?.email || storedUser?.email || "",
          uid: student?.uid || user?.uid || storedUser?.uid || "",
          studentId: student?.student_id,
          detail: student?.course_name || "General Studies",
          phone_number: student?.phone_number || "",
          date_of_birth: student?.date_of_birth
            ? String(student.date_of_birth).slice(0, 10)
            : "",
          gender: student?.gender || "",
        });
      } else if (role === "teacher") {
        const [teacherRes, userRes] = await Promise.all([
          api.teachers.getMe().catch(() => null),
          api.users.getMe().catch(() => null),
        ]);
        const teacher = teacherRes?.teacher || teacherRes;
        const user = userRes?.user || userRes;

        setProfile({
          name: teacher?.name || user?.name || "Faculty Instructor",
          email: user?.email || storedUser?.email || "",
          uid: user?.uid || storedUser?.uid || "",
          detail: "Academic Faculty",
          qualification: teacher?.qualification || "M.Tech",
          specialization: teacher?.specialization || "",
          experience: teacher?.experience ?? 0,
          phone_number: teacher?.phone_number || user?.phone_number || "",
        });
      } else {
        const userRes = await api.users.getMe().catch(() => null);
        const user = userRes?.user || userRes;

        setProfile({
          name: user?.name || "Platform Administrator",
          email: user?.email || storedUser?.email || "",
          uid: user?.uid || storedUser?.uid || "",
          detail: "Platform Administrator",
          qualification: "M.Tech",
          specialization: "",
          experience: 0,
          phone_number: user?.phone_number || "",
        });
      }
    } catch (err) {
      console.error("Failed to load profile:", err);
      setError("Unable to load your profile. Please try again.");
    } finally {
      setLoading(false);
    }
  }, [role]);

  useEffect(() => {
    fetchProfile();
  }, [fetchProfile]);

  const saveProfile = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setSaving(true);
    setError("");
    const form = new FormData(event.currentTarget);
    const name = String(form.get("name") ?? "").trim();
    const phoneNumber = String(form.get("phoneNumber") ?? "").trim();
    const qualification = String(form.get("qualification") ?? "M.Tech").trim();
    const specialization = String(form.get("specialization") ?? "").trim();
    const experienceRaw = form.get("experience");
    const experience = experienceRaw !== null ? Number(experienceRaw) : undefined;
    const dateOfBirth = String(form.get("dateOfBirth") ?? "").trim();
    const gender = String(form.get("gender") ?? "").trim();

    if (!name || name.length < 2) {
      setError("Full name must be at least 2 characters.");
      setSaving(false);
      return;
    }

    if (phoneNumber && !/^\d{10}$/.test(phoneNumber)) {
      setError("Phone number must contain exactly 10 digits.");
      setSaving(false);
      return;
    }

    if (role === "student" && dateOfBirth) {
      const dob = new Date(dateOfBirth);
      const today = new Date();
      today.setHours(0, 0, 0, 0);
      if (isNaN(dob.getTime())) {
        setError("Please enter a valid date of birth.");
        setSaving(false);
        return;
      }
      if (dob >= today) {
        setError("Date of birth must be in the past.");
        setSaving(false);
        return;
      }
      // Must be at least 5 years old (sanity check)
      const minAge = new Date(today);
      minAge.setFullYear(minAge.getFullYear() - 5);
      if (dob > minAge) {
        setError("Please enter a valid date of birth.");
        setSaving(false);
        return;
      }
    }

    const validGenders = ["Male", "Female", "Other", "Prefer not to say"];
    if (role === "student" && gender && !validGenders.includes(gender)) {
      setError("Please select a valid gender option.");
      setSaving(false);
      return;
    }

    if (role === "teacher" && experience !== undefined && !Number.isNaN(experience)) {
      if (experience < 0 || experience > 60) {
        setError("Experience must be between 0 and 60 years.");
        setSaving(false);
        return;
      }
    }

    try {
      if (role === "student") {
        await api.students.updateMe({
          name,
          phone_number: phoneNumber || undefined,
          date_of_birth: dateOfBirth || undefined,
          gender: gender || undefined,
        });
      } else if (role === "teacher") {
        await api.teachers.updateMe({
          name,
          phone_number: phoneNumber,
          qualification,
          specialization,
          experience: Number.isNaN(experience) ? 0 : experience,
        });
        await api.users.updateMe({ name }).catch(() => {});
      } else {
        await api.users.updateMe({
          name,
        });
      }

      // Update session storage
      const currentSession = getStoredSession();
      if (currentSession) {
        setStoredSession({
          ...currentSession,
          user: {
            ...currentSession.user,
            name,
          },
        });
      }

      showSuccess("Profile updated successfully.");
      setEditing(false);
      fetchProfile();
    } catch (err: any) {
      console.error("Failed to update profile:", err);
      setError(err.message || "Unable to update profile. Please try again.");
    } finally {
      setSaving(false);
    }
  };

  if (loading) {
    return <PageSkeleton variant="profile" />;
  }

  return (
    <section className="card p-6">
      <InlineError message={error} className="mb-4" />
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <span className="grid h-12 w-12 place-items-center rounded-2xl bg-indigo-50 text-(--brand)">
            <UserRound size={21} />
          </span>

          <div>
            <h2 className="font-bold text-slate-900">Profile Information</h2>
            <p className="text-sm text-slate-500">
              Your account details and personal credentials.
            </p>
          </div>
        </div>

        {canEdit && !editing && (
          <button
            type="button"
            onClick={() => setEditing(true)}
            className="secondary-button"
          >
            <Pencil size={16} />
            Edit Profile
          </button>
        )}
      </div>

      <form onSubmit={saveProfile} className="mt-6 grid gap-4 sm:grid-cols-2">
        <label>
          <span className="mb-1.5 block text-xs font-semibold text-slate-500">
            Full Name
          </span>
          <input
            name="name"
            defaultValue={profile.name}
            placeholder="Enter name"
            required
            readOnly={!editing}
            className={`w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300 ${
              editing ? "bg-white" : "bg-slate-50 text-slate-600"
            }`}
          />
        </label>

        <label>
          <span className="mb-1.5 block text-xs font-semibold text-slate-500">
            Email Address
          </span>
          <input
            value={profile.email}
            placeholder="Email address unavailable"
            readOnly
            aria-readonly="true"
            className="w-full rounded-xl border border-(--border) bg-slate-50 px-3 py-2.5 text-sm text-slate-500 outline-none"
          />
        </label>

        <label>
          <span className="mb-1.5 block text-xs font-semibold text-slate-500">
            {role === "student" ? "Student ID" : "Account UID"}
          </span>
          <input
            value={
              role === "student"
                ? profile.studentId
                  ? `STD-${String(profile.studentId).padStart(3, "0")}`
                  : ""
                : profile.uid
            }
            placeholder={role === "student" ? "Student ID unavailable" : "Account UID unavailable"}
            readOnly
            aria-readonly="true"
            className="w-full rounded-xl border border-(--border) bg-slate-50 px-3 py-2.5 text-sm text-slate-500 outline-none font-mono"
          />
        </label>

        <label>
          <span className="mb-1.5 block text-xs font-semibold text-slate-500">
            Phone Number
          </span>
          <input
            name="phoneNumber"
            type="tel"
            inputMode="numeric"
            maxLength={10}
            pattern="[0-9]{10}"
            defaultValue={profile.phone_number}
            placeholder="Enter 10-digit phone number"
            readOnly={!editing}
            onInput={(e) => {
              if (editing) {
                e.currentTarget.value = e.currentTarget.value.replace(/\D/g, "").slice(0, 10);
              }
            }}
            className={`w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300 ${
              editing ? "bg-white" : "bg-slate-50 text-slate-600"
            }`}
          />
        </label>

        {role === "student" && (
          <>
            <label>
              <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                Date of Birth
              </span>
              <input
                name="dateOfBirth"
                type="date"
                key={profile.date_of_birth}
                defaultValue={profile.date_of_birth}
                max={new Date().toISOString().slice(0, 10)}
                readOnly={!editing}
                disabled={!editing}
                className={`w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300 ${
                  editing
                    ? "bg-white cursor-pointer"
                    : "bg-slate-50 text-slate-600"
                }`}
              />
            </label>

            <label>
              <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                Gender
              </span>
              <select
                name="gender"
                key={profile.gender}
                defaultValue={profile.gender}
                disabled={!editing}
                className={`w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300 ${
                  editing
                    ? "bg-white cursor-pointer"
                    : "bg-slate-50 text-slate-600"
                }`}
              >
                <option value="">Select gender</option>
                <option value="Male">Male</option>
                <option value="Female">Female</option>
                <option value="Other">Other</option>
                <option value="Prefer not to say">Prefer not to say</option>
              </select>
            </label>
          </>
        )}

        {role === "teacher" && (
          <>
            <label>
              <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                Specialization
              </span>
              <input
                name="specialization"
                defaultValue={profile.specialization}
                placeholder="e.g. Computer Science, AI, Web Development"
                readOnly={!editing}
                className={`w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300 ${
                  editing ? "bg-white" : "bg-slate-50 text-slate-600"
                }`}
              />
            </label>

            <label>
              <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                Highest Qualification
              </span>
              <select
                name="qualification"
                defaultValue={profile.qualification ?? "M.Tech"}
                disabled={!editing}
                className="w-full rounded-xl border border-(--border) bg-white px-3 py-2.5 text-sm outline-none disabled:bg-slate-50 disabled:text-slate-600 focus:border-indigo-300"
              >
                {qualifications.map((qualification) => (
                  <option key={qualification} value={qualification}>
                    {qualification}
                  </option>
                ))}
              </select>
            </label>

            <label>
              <span className="mb-1.5 block text-xs font-semibold text-slate-500">
                Experience (Years)
              </span>
              <input
                name="experience"
                type="number"
                min={0}
                max={60}
                defaultValue={profile.experience ?? 0}
                placeholder="Years of experience"
                readOnly={!editing}
                className={`w-full rounded-xl border border-(--border) px-3 py-2.5 text-sm outline-none focus:border-indigo-300 ${
                  editing ? "bg-white" : "bg-slate-50 text-slate-600"
                }`}
              />
            </label>
          </>
        )}

        {editing && (
          <div className="flex items-center justify-end gap-3 border-t border-(--border) pt-4 sm:col-span-2">
            <button
              type="button"
              onClick={() => setEditing(false)}
              disabled={saving}
              className="secondary-button"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={saving}
              className="primary-button"
            >
              {saving ? "Saving..." : "Save Changes"}
            </button>
          </div>
        )}
      </form>
    </section>
  );
}
