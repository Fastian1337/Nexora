"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { useAuth } from "@/context/auth-context";

function LoginForm() {
  const { login, error, clearError } = useAuth();
  const searchParams = useSearchParams();
  const router = useRouter();

  const [email, setEmail] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [rememberMe, setRememberMe] = React.useState(false);
  const [submitting, setSubmitting] = React.useState(false);
  const [successMsg, setSuccessMsg] = React.useState<string | null>(null);

  React.useEffect(() => {
    clearError();
    if (searchParams.get("registered") === "true") {
      setSuccessMsg("Registration complete! A verification link has been sent to your email.");
    }
  }, [searchParams, clearError]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) return;

    setSubmitting(true);
    setSuccessMsg(null);

    try {
      await login({ email, password, remember_me: rememberMe });
    } catch {
      // Error is caught and stored inside the AuthContext
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="w-full max-w-md space-y-8 rounded-2xl border border-border/50 bg-card/40 p-8 backdrop-blur-xl shadow-2xl">
      <div className="text-center space-y-2">
        <h2 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
          NEXORA
        </h2>
        <p className="text-sm text-muted-foreground font-semibold">Sign in to manage your AI Employees</p>
      </div>

      {error && (
        <div className="rounded-xl bg-red-500/10 border border-red-500/20 p-4 text-xs text-red-500 font-semibold">
          {error}
        </div>
      )}

      {successMsg && (
        <div className="rounded-xl bg-green-500/10 border border-green-500/20 p-4 text-xs text-green-500 font-semibold">
          {successMsg}
        </div>
      )}

      <form onSubmit={handleSubmit} className="space-y-6">
        <div className="space-y-1">
          <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
            Username or Email
          </label>
          <input
            type="text"
            required
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl border border-border bg-background/50 focus:outline-none focus:ring-2 focus:ring-primary/40 text-sm transition-all"
            placeholder="e.g. fastian1337"
          />
        </div>

        <div className="space-y-1">
          <div className="flex items-center justify-between">
            <label className="text-xs font-semibold text-muted-foreground uppercase tracking-wide">
              Password
            </label>
            <Link
              href="/forgot-password"
              className="text-xs font-semibold text-primary hover:underline"
            >
              Forgot?
            </Link>
          </div>
          <input
            type="password"
            required
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2.5 rounded-xl border border-border bg-background/50 focus:outline-none focus:ring-2 focus:ring-primary/40 text-sm transition-all"
            placeholder="••••••••"
          />
        </div>

        <div className="flex items-center justify-between">
          <label className="flex items-center gap-2 cursor-pointer select-none">
            <input
              type="checkbox"
              checked={rememberMe}
              onChange={(e) => setRememberMe(e.target.checked)}
              className="rounded border-border bg-background/50 text-primary focus:ring-primary/30"
            />
            <span className="text-xs text-muted-foreground font-semibold">Remember me</span>
          </label>
        </div>

        <button
          type="submit"
          disabled={submitting}
          className="w-full py-3 bg-gradient-to-r from-primary to-secondary text-white font-bold text-sm rounded-xl transition-all shadow-md hover:shadow-primary/10 disabled:opacity-50 cursor-pointer animate-none"
        >
          {submitting ? "Signing in..." : "Sign In"}
        </button>
      </form>

      <p className="text-center text-xs text-muted-foreground font-semibold">
        New to Nexora?{" "}
        <Link href="/register" className="text-primary hover:underline">
          Create an account
        </Link>
      </p>
    </div>
  );
}

export default function LoginPage() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-6 py-12">
      {/* Background shapes */}
      <div className="absolute top-1/4 left-1/4 -z-10 h-72 w-72 rounded-full bg-primary/10 blur-[80px]" />
      <div className="absolute bottom-1/4 right-1/4 -z-10 h-80 w-80 rounded-full bg-accent/10 blur-[100px]" />
      <React.Suspense fallback={
        <div className="flex flex-col items-center gap-4 text-center">
          <div className="h-10 w-10 animate-spin rounded-full border-4 border-t-primary border-border/40" />
          <p className="text-sm font-semibold text-muted-foreground font-mono">Loading login form...</p>
        </div>
      }>
        <LoginForm />
      </React.Suspense>
    </div>
  );
}
