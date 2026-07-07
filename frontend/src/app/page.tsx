"use client";

import * as React from "react";
import Link from "next/link";
import { useTheme } from "@/app/providers";

export default function Home() {
  const { theme, toggleTheme } = useTheme();
  const [activeWorkspace, setActiveWorkspace] = React.useState<"reception" | "school" | "marketing">("reception");

  return (
    <div className="relative min-h-screen bg-background text-foreground transition-colors duration-300 font-sans antialiased">
      {/* Subtle background glow */}
      <div className="absolute top-0 left-1/2 -translate-x-1/2 -z-10 h-[500px] w-full max-w-7xl bg-[radial-gradient(ellipse_at_top,rgba(79,70,229,0.04),transparent_45%)]" />

      {/* Header */}
      <header className="border-b border-border/40 bg-background/70 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-8">
            <Link href="/" className="text-base font-bold tracking-tight hover:opacity-90 transition-opacity">
              Nexora
            </Link>
            <nav className="hidden md:flex items-center gap-6 text-xs font-semibold text-muted-foreground uppercase tracking-wider">
              <a href="#solutions" className="hover:text-foreground transition-colors">Solutions</a>
              <a href="#features" className="hover:text-foreground transition-colors">Architecture</a>
            </nav>
          </div>

          <div className="flex items-center gap-4">
            {/* Theme Selector */}
            <button
              onClick={toggleTheme}
              className="p-2 rounded-md border border-border/40 hover:bg-card text-muted-foreground hover:text-foreground transition-all cursor-pointer"
              aria-label="Toggle theme"
            >
              {theme === "light" ? (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              ) : (
                <svg className="w-4 h-4 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m2.828 0l-.707-.707m12.728-12.728l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
                </svg>
              )}
            </button>

            <Link
              href="/login"
              className="text-xs font-bold hover:text-primary transition-colors uppercase tracking-wider px-3 py-1.5"
            >
              Log In
            </Link>
            <Link
              href="/register"
              className="px-4 py-2 bg-primary text-primary-foreground hover:bg-primary/95 text-xs font-bold rounded transition-all shadow-sm"
            >
              Get Started
            </Link>
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <main className="max-w-6xl mx-auto px-6 py-16 md:py-28 space-y-24">
        
        {/* Hero Section */}
        <section className="text-center space-y-6 max-w-2xl mx-auto">
          <h1 className="text-4xl sm:text-5xl font-bold tracking-tight leading-[1.15] text-foreground">
            Automate your daily <br className="hidden sm:inline" />
            business operations.
          </h1>

          <p className="text-sm sm:text-base text-muted-foreground leading-relaxed max-w-lg mx-auto">
            Deploy digital assistants that schedule patient bookings, manage school admissions, and coordinate marketing campaigns. Connect your tools and let Nexora handle the rest.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-3 pt-2">
            <Link
              href="/register"
              className="px-5 py-2.5 bg-primary text-primary-foreground font-bold text-xs rounded hover:bg-primary/90 transition-all shadow-md"
            >
              Create Account
            </Link>
            <a
              href="#solutions"
              className="px-5 py-2.5 border border-border/80 bg-card/50 hover:bg-card text-foreground font-semibold text-xs rounded transition-all"
            >
              See Solutions
            </a>
          </div>
        </section>

        {/* Feature Tab Showcase */}
        <section id="solutions" className="space-y-6 max-w-4xl mx-auto">
          <div className="flex justify-center border-b border-border/30 max-w-xs mx-auto">
            <button
              onClick={() => setActiveWorkspace("reception")}
              className={`flex-1 pb-2 text-center text-xs font-bold border-b-2 transition-all cursor-pointer ${
                activeWorkspace === "reception"
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              Clinics
            </button>
            <button
              onClick={() => setActiveWorkspace("school")}
              className={`flex-1 pb-2 text-center text-xs font-bold border-b-2 transition-all cursor-pointer ${
                activeWorkspace === "school"
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              Schools
            </button>
            <button
              onClick={() => setActiveWorkspace("marketing")}
              className={`flex-1 pb-2 text-center text-xs font-bold border-b-2 transition-all cursor-pointer ${
                activeWorkspace === "marketing"
                  ? "border-primary text-primary"
                  : "border-transparent text-muted-foreground hover:text-foreground"
              }`}
            >
              Marketing
            </button>
          </div>

          <div className="rounded border border-border bg-card p-6 shadow-sm min-h-[280px] flex flex-col justify-between">
            <div className="flex items-center justify-between pb-3 border-b border-border/40">
              <div className="flex items-center gap-1.5">
                <span className="w-2 h-2 rounded-full bg-red-500/50" />
                <span className="w-2 h-2 rounded-full bg-yellow-500/50" />
                <span className="w-2 h-2 rounded-full bg-green-500/50" />
                <span className="text-xs text-muted-foreground ml-2 font-mono">{activeWorkspace}_workspace</span>
              </div>
              <span className="text-xs uppercase font-bold text-muted-foreground px-2 py-0.5 rounded bg-muted/60">
                Preview
              </span>
            </div>

            <div className="py-4 flex-1">
              {activeWorkspace === "reception" && (
                <div className="space-y-4 animate-in fade-in duration-200">
                  <div>
                    <h4 className="text-sm font-bold">Clinic Coordinator</h4>
                    <p className="text-xs text-muted-foreground">Keep doctor calendars fully booked without answering calls.</p>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="p-3 rounded border border-border/80 bg-background/50 space-y-1">
                      <div className="text-xs text-muted-foreground font-semibold">Incoming Request</div>
                      <p className="text-xs font-medium italic">"Is Dr. Sarah free this Friday afternoon?"</p>
                    </div>

                    <div className="p-3 rounded border border-primary/20 bg-primary/5 space-y-1">
                      <div className="text-xs text-primary font-bold">Action Completed</div>
                      <p className="text-xs font-medium">
                        Booked Friday at 3:30 PM. Sent SMS confirmation to patient.
                      </p>
                    </div>
                  </div>
                </div>
              )}

              {activeWorkspace === "school" && (
                <div className="space-y-4 animate-in fade-in duration-200">
                  <div>
                    <h4 className="text-sm font-bold">Admission Assistant</h4>
                    <p className="text-xs text-muted-foreground">Streamline parent onboarding and application tracking.</p>
                  </div>

                  <div className="overflow-hidden rounded border border-border bg-background/50">
                    <table className="w-full border-collapse text-left text-xs">
                      <thead>
                        <tr className="border-b border-border bg-muted/30">
                          <th className="p-2.5 font-bold text-muted-foreground">Parent Name</th>
                          <th className="p-2.5 font-bold text-muted-foreground">Age</th>
                          <th className="p-2.5 font-bold text-muted-foreground">Status</th>
                          <th className="p-2.5 font-bold text-muted-foreground">Latest Update</th>
                        </tr>
                      </thead>
                      <tbody>
                        <tr className="border-b border-border/40">
                          <td className="p-2.5 font-medium">Muhammad Ali</td>
                          <td className="p-2.5">7 Years</td>
                          <td className="p-2.5">
                            <span className="px-1.5 py-0.5 rounded bg-yellow-500/10 text-yellow-500 font-bold text-xs">Interview Scheduled</span>
                          </td>
                          <td className="p-2.5 text-muted-foreground text-xs">Emailed curriculum details.</td>
                        </tr>
                        <tr>
                          <td className="p-2.5 font-medium">Ayesha Siddiqui</td>
                          <td className="p-2.5">5 Years</td>
                          <td className="p-2.5">
                            <span className="px-1.5 py-0.5 rounded bg-green-500/10 text-green-500 font-bold text-xs">Registered</span>
                          </td>
                          <td className="p-2.5 text-muted-foreground text-xs">Added parent details to CRM.</td>
                        </tr>
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {activeWorkspace === "marketing" && (
                <div className="space-y-4 animate-in fade-in duration-200">
                  <div>
                    <h4 className="text-sm font-bold">Campaign Planner</h4>
                    <p className="text-xs text-muted-foreground">Draft and schedule posts across all channels in one click.</p>
                  </div>

                  <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                    <div className="p-3 rounded border border-border bg-background/50 space-y-1">
                      <div className="text-xs text-muted-foreground font-semibold">Bilingual Copy Draft</div>
                      <p className="text-xs">
                        "Enrollment starts next week! 🌟 داخلے شروع ہو چکے ہیں۔ Click the link to register."
                      </p>
                    </div>

                    <div className="p-3 rounded border border-primary/20 bg-primary/5 space-y-1">
                      <div className="text-xs text-primary font-bold">Scheduling Rule</div>
                      <p className="text-xs text-muted-foreground">
                        Post scheduled for 6:30 PM (optimal engagement window).
                      </p>
                    </div>
                  </div>
                </div>
              )}
            </div>

            <div className="pt-3 border-t border-border/20 flex items-center justify-between text-xs text-muted-foreground font-mono">
              <span>Data isolation active</span>
              <span>Version 0.2.1</span>
            </div>
          </div>
        </section>

        {/* Features / Architecture Section */}
        <section id="features" className="space-y-12">
          <div className="text-center max-w-md mx-auto space-y-2">
            <h2 className="text-2xl font-bold tracking-tight">Built to scale securely</h2>
            <p className="text-xs text-muted-foreground">
              Robust operational structures designed to keep your business running smoothly.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 max-w-4xl mx-auto">
            <div className="p-5 rounded border border-border bg-card space-y-3">
              <h3 className="text-sm font-bold">Modular Structure</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Decoupled database architecture means fast response times even during high volume workloads.
              </p>
            </div>

            <div className="p-5 rounded border border-border bg-card space-y-3">
              <h3 className="text-sm font-bold">Isolated & Secure</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Every client organization gets full database isolation to protect customer and patient privacy.
              </p>
            </div>

            <div className="p-5 rounded border border-border bg-card space-y-3">
              <h3 className="text-sm font-bold">Smart Integrations</h3>
              <p className="text-xs text-muted-foreground leading-relaxed">
                Connect with n8n, Meta API, Google Workspace, and your local CRM tools out of the box.
              </p>
            </div>
          </div>
        </section>

        {/* CTA section */}
        <section className="rounded border border-primary/20 bg-primary/5 p-6 text-center max-w-2xl mx-auto space-y-4">
          <h2 className="text-xl font-bold text-foreground">
            Ready to automate your operations?
          </h2>
          <p className="text-xs text-muted-foreground max-w-md mx-auto">
            Get started with our standard workspaces or invite your team to collaborate on custom integrations.
          </p>
          <div className="pt-1">
            <Link
              href="/register"
              className="inline-flex px-5 py-2.5 bg-primary text-primary-foreground font-bold text-xs rounded hover:bg-primary/95 transition-all shadow-md"
            >
              Start Free Trial
            </Link>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-border/40 py-10 bg-card/20">
        <div className="max-w-6xl mx-auto px-6 flex flex-col sm:flex-row items-center justify-between gap-4 text-xs text-muted-foreground font-semibold uppercase tracking-wider">
          <div>
            © 2026 Nexora Technologies.
          </div>
          <div className="flex gap-6">
            <a href="#" className="hover:text-foreground transition-colors">Privacy</a>
            <a href="#" className="hover:text-foreground transition-colors">Terms</a>
            <a href="#" className="hover:text-foreground transition-colors">API docs</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
