"use client";

import * as React from "react";
import Link from "next/link";
import { client, ApiError } from "@/lib/api/client";

export default function ForgotPasswordPage() {
  const [email, setEmail] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);
  const [success, setSuccess] = React.useState(false);
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email) return;

    setSubmitting(true);
    setErrorMsg(null);

    try {
      await client.post("/api/v1/auth/forgot-password", { email });
      setSuccess(true);
    } catch (err: any) {
      if (err instanceof ApiError) {
        setErrorMsg(err.data.message || "Failed to trigger password recovery.");
      } else {
        setErrorMsg("An unexpected network error occurred.");
      }
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-6 py-12">
      <div className="absolute top-1/4 left-1/4 -z-10 h-72 w-72 rounded-full bg-blue-500/10 blur-[80px]" />
      <div className="absolute bottom-1/4 right-1/4 -z-10 h-80 w-80 rounded-full bg-purple-500/10 blur-[100px]" />

      <div className="w-full max-w-md space-y-6 rounded-2xl border border-border/50 bg-card/40 p-8 backdrop-blur-xl shadow-2xl">
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-blue-500 to-indigo-500 bg-clip-text text-transparent">
            RECOVER PASSWORD
          </h2>
          <p className="text-sm text-muted-foreground">Type your email to receive recovery instructions</p>
        </div>

        {errorMsg && (
          <div className="rounded-lg bg-red-500/10 border border-red-500/20 p-4 text-xs text-red-500 font-medium">
            {errorMsg}
          </div>
        )}

        {success ? (
          <div className="space-y-4 text-center">
            <div className="rounded-lg bg-green-500/10 border border-green-500/20 p-4 text-xs text-green-500 font-medium">
              If the account exists, we have sent a secure password reset link to your email.
            </div>
            <Link
              href="/login"
              className="inline-block px-6 py-2.5 bg-primary text-primary-foreground font-semibold text-xs rounded-lg transition-all"
            >
              Return to login
            </Link>
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Email Address</label>
              <input
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="w-full px-3 py-2.5 rounded-lg border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500/30 transition-all"
                placeholder="saifu@nexora.tech"
              />
            </div>

            <button
              type="submit"
              disabled={submitting}
              className="w-full py-2.5 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-500 hover:to-indigo-500 text-white font-semibold text-sm rounded-lg transition-all shadow-lg shadow-blue-500/25 disabled:opacity-50 cursor-pointer"
            >
              {submitting ? "Sending Link..." : "Send Reset Link"}
            </button>
          </form>
        )}

        <p className="text-center text-xs text-muted-foreground font-medium">
          Remember password?{" "}
          <Link href="/login" className="text-blue-500 hover:underline">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
}
