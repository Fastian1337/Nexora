"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { client, ApiError } from "@/lib/api/client";

function ResetPasswordForm() {
  const searchParams = useSearchParams();
  const router = useRouter();

  const [password, setPassword] = React.useState("");
  const [confirmPassword, setConfirmPassword] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);
  const [success, setSuccess] = React.useState(false);
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);

  const token = searchParams.get("token");

  // Password strength check
  const meetsCriteria = password.length >= 8 && /[A-Z]/.test(password) && /[a-z]/.test(password) && /\d/.test(password);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!token) {
      setErrorMsg("Recovery token is missing. Please initiate reset again.");
      return;
    }
    if (password !== confirmPassword) {
      setErrorMsg("Passwords do not match.");
      return;
    }
    if (!meetsCriteria) {
      setErrorMsg("Password does not meet complexity criteria.");
      return;
    }

    setSubmitting(true);
    setErrorMsg(null);

    try {
      await client.post("/api/v1/auth/reset-password", {
        token,
        new_password: password,
      });
      setSuccess(true);
    } catch (err: any) {
      if (err instanceof ApiError) {
        setErrorMsg(err.data.message || "Failed to reset password.");
      } else {
        setErrorMsg("An unexpected network error occurred.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="w-full max-w-md space-y-6 rounded-2xl border border-border/50 bg-card/40 p-8 backdrop-blur-xl shadow-2xl">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
          RESET PASSWORD
        </h2>
        <p className="text-sm text-muted-foreground font-semibold">Type your new secure account password</p>
      </div>

      {errorMsg && (
        <div className="rounded-xl bg-red-500/10 border border-red-500/20 p-4 text-xs text-red-500 font-semibold">
          {errorMsg}
        </div>
      )}

      {success ? (
        <div className="space-y-4 text-center">
          <div className="rounded-xl bg-green-500/10 border border-green-500/20 p-4 text-xs text-green-500 font-semibold">
            Password has been successfully updated.
          </div>
          <Link
            href="/login"
            className="inline-block px-6 py-2.5 bg-primary text-primary-foreground font-bold text-xs rounded-xl transition-all"
          >
            Sign In
          </Link>
        </div>
      ) : (
        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="space-y-1">
            <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">New Password</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
              placeholder="••••••••"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Confirm Password</label>
            <input
              type="password"
              required
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
              placeholder="••••••••"
            />
          </div>

          <button
            type="submit"
            disabled={submitting}
            className="w-full py-2.5 mt-2 bg-gradient-to-r from-primary to-secondary text-white font-bold text-sm rounded-xl transition-all shadow-md hover:shadow-primary/10 disabled:opacity-50 cursor-pointer"
          >
            {submitting ? "Resetting Password..." : "Update Password"}
          </button>
        </form>
      )}
    </div>
  );
}

export default function ResetPasswordPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-6 py-12">
      <div className="absolute top-1/4 left-1/4 -z-10 h-72 w-72 rounded-full bg-primary/10 blur-[80px]" />
      <div className="absolute bottom-1/4 right-1/4 -z-10 h-80 w-80 rounded-full bg-accent/10 blur-[100px]" />
      <React.Suspense fallback={
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-t-primary border-border/40" />
          <p className="text-sm font-semibold text-muted-foreground font-mono">Loading form context...</p>
        </div>
      }>
        <ResetPasswordForm />
      </React.Suspense>
    </div>
  );
}
