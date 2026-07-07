"use client";

import * as React from "react";
import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { client, ApiError } from "@/lib/api/client";

function VerifyEmailForm() {
  const searchParams = useSearchParams();
  const token = searchParams.get("token");

  const [loading, setLoading] = React.useState(true);
  const [success, setSuccess] = React.useState(false);
  const [errorMsg, setErrorMsg] = React.useState<string | null>(null);

  React.useEffect(() => {
    if (!token) {
      setErrorMsg("Verification token is missing in the URL.");
      setLoading(false);
      return;
    }

    const triggerVerification = async () => {
      try {
        await client.post("/api/v1/auth/verify-email", { token });
        setSuccess(true);
      } catch (err: any) {
        if (err instanceof ApiError) {
          setErrorMsg(err.data.message || "Email verification failed.");
        } else {
          setErrorMsg("An unexpected network error occurred.");
        }
      } finally {
        setLoading(false);
      }
    };

    triggerVerification();
  }, [token]);

  return (
    <div className="w-full max-w-md space-y-6 rounded-2xl border border-border/50 bg-card/40 p-8 backdrop-blur-xl shadow-2xl text-center">
      <h2 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
        EMAIL VERIFICATION
      </h2>

      {loading ? (
        <div className="space-y-4">
          <div className="h-10 w-10 mx-auto animate-spin rounded-full border-4 border-t-primary border-border/40" />
          <p className="text-sm font-semibold text-muted-foreground font-mono">Verifying credentials...</p>
        </div>
      ) : success ? (
        <div className="space-y-6">
          <div className="rounded-xl bg-green-500/10 border border-green-500/20 p-4 text-xs text-green-500 font-semibold">
            ✓ Your email address has been successfully verified!
          </div>
          <Link
            href="/login"
            className="inline-block px-6 py-2.5 bg-primary text-primary-foreground font-bold text-xs rounded-xl transition-all"
          >
            Go to sign in
          </Link>
        </div>
      ) : (
        <div className="space-y-6">
          <div className="rounded-xl bg-red-500/10 border border-red-500/20 p-4 text-xs text-red-500 font-semibold">
            ✗ {errorMsg}
          </div>
          <Link
            href="/login"
            className="inline-block px-6 py-2.5 border border-border/80 hover:bg-muted text-foreground font-bold text-xs rounded-xl transition-all"
          >
            Back to login
          </Link>
        </div>
      )}
    </div>
  );
}

export default function VerifyEmailPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-6 py-12">
      <div className="absolute top-1/4 left-1/4 -z-10 h-72 w-72 rounded-full bg-primary/10 blur-[80px]" />
      <div className="absolute bottom-1/4 right-1/4 -z-10 h-80 w-80 rounded-full bg-accent/10 blur-[100px]" />
      <React.Suspense fallback={
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-t-primary border-border/40" />
          <p className="text-sm font-semibold text-muted-foreground font-mono">Loading verification token...</p>
        </div>
      }>
        <VerifyEmailForm />
      </React.Suspense>
    </div>
  );
}
