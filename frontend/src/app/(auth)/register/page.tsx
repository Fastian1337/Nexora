"use client";

import * as React from "react";
import Link from "next/link";
import { useAuth } from "@/context/auth-context";

export default function RegisterPage() {
  const { register, error, clearError } = useAuth();

  const [email, setEmail] = React.useState("");
  const [username, setUsername] = React.useState("");
  const [password, setPassword] = React.useState("");
  const [firstName, setFirstName] = React.useState("");
  const [lastName, setLastName] = React.useState("");
  const [phoneNumber, setPhoneNumber] = React.useState("");
  const [submitting, setSubmitting] = React.useState(false);

  React.useEffect(() => {
    clearError();
  }, [clearError]);

  // Password Strength Indicators
  const strengthCriteria = {
    length: password.length >= 8,
    uppercase: /[A-Z]/.test(password),
    lowercase: /[a-z]/.test(password),
    digit: /\d/.test(password),
    special: /[!@#$%^&*(),.?":{}|<>]/.test(password),
  };

  const strengthCount = Object.values(strengthCriteria).filter(Boolean).length;
  const strengthColor =
    strengthCount <= 2 ? "bg-red-500" : strengthCount <= 4 ? "bg-yellow-500" : "bg-green-500";

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (strengthCount < 5) return;

    setSubmitting(true);
    try {
      await register({
        email,
        username,
        password,
        first_name: firstName || undefined,
        last_name: lastName || undefined,
        phone_number: phoneNumber || undefined,
      });
    } catch {
      // Handled in context
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen items-center justify-center bg-background px-6 py-12">
      {/* Background shapes */}
      <div className="absolute top-1/4 left-1/4 -z-10 h-72 w-72 rounded-full bg-primary/10 blur-[80px]" />
      <div className="absolute bottom-1/4 right-1/4 -z-10 h-80 w-80 rounded-full bg-accent/10 blur-[100px]" />

      <div className="w-full max-w-md space-y-6 rounded-2xl border border-border/50 bg-card/40 p-8 backdrop-blur-xl shadow-2xl">
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
            CREATE ACCOUNT
          </h2>
          <p className="text-sm text-muted-foreground font-semibold">Sign up to Nexora automation employee platform</p>
        </div>

        {error && (
          <div className="rounded-xl bg-red-500/10 border border-red-500/20 p-4 text-xs text-red-500 font-semibold animate-none">
            {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div className="grid grid-cols-2 gap-4">
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">First Name</label>
              <input
                type="text"
                value={firstName}
                onChange={(e) => setFirstName(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                placeholder="Saif"
              />
            </div>
            <div className="space-y-1">
              <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Last Name</label>
              <input
                type="text"
                value={lastName}
                onChange={(e) => setLastName(e.target.value)}
                className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                placeholder="Ullah"
              />
            </div>
          </div>

          <div className="space-y-1">
            <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Username *</label>
            <input
              type="text"
              required
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
              placeholder="fastian1337"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Email Address *</label>
            <input
              type="email"
              required
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
              placeholder="saifu@nexora.tech"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Phone Number</label>
            <input
              type="tel"
              value={phoneNumber}
              onChange={(e) => setPhoneNumber(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
              placeholder="+92 300 1234567"
            />
          </div>

          <div className="space-y-1">
            <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Password *</label>
            <input
              type="password"
              required
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
              placeholder="••••••••"
            />
            {password.length > 0 && (
              <div className="mt-2 space-y-2">
                <div className="flex h-1 gap-1 rounded bg-muted/30">
                  {Array.from({ length: 5 }).map((_, i) => (
                    <div
                      key={i}
                      className={`h-full flex-1 rounded transition-all duration-300 ${
                        i < strengthCount ? strengthColor : "bg-transparent"
                      }`}
                    />
                  ))}
                </div>
                <div className="grid grid-cols-2 gap-x-2 gap-y-1 text-[10px]">
                  <span className={strengthCriteria.length ? "text-green-500" : "text-muted-foreground"}>
                    ✓ Min 8 characters
                  </span>
                  <span className={strengthCriteria.uppercase ? "text-green-500" : "text-muted-foreground"}>
                    ✓ Capital Letter
                  </span>
                  <span className={strengthCriteria.lowercase ? "text-green-500" : "text-muted-foreground"}>
                    ✓ Lowercase Letter
                  </span>
                  <span className={strengthCriteria.digit ? "text-green-500" : "text-muted-foreground"}>
                    ✓ Number
                  </span>
                  <span className={strengthCriteria.special ? "text-green-500" : "text-muted-foreground"}>
                    ✓ Special character
                  </span>
                </div>
              </div>
            )}
          </div>

          <button
            type="submit"
            disabled={submitting || strengthCount < 5}
            className="w-full py-2.5 mt-2 bg-gradient-to-r from-primary to-secondary text-white font-bold text-sm rounded-xl transition-all shadow-md hover:shadow-primary/10 disabled:opacity-50 cursor-pointer"
          >
            {submitting ? "Creating Account..." : "Sign Up"}
          </button>
        </form>

        <p className="text-center text-xs text-muted-foreground font-semibold">
          Already have an account?{" "}
          <Link href="/login" className="text-primary hover:underline">
            Sign In
          </Link>
        </p>
      </div>
    </div>
  );
}
