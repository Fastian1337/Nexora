"use client";

import * as React from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { useTheme } from "@/app/providers";

interface Organization {
  id: string;
  name: string;
  slug: string;
}

export default function DashboardLayout({ children }: { children: React.ReactNode }) {
  const { theme, toggleTheme } = useTheme();
  const router = useRouter();
  const [organizations, setOrganizations] = React.useState<Organization[]>([
    { id: "1", name: "Nexora Technologies", slug: "nexora-tech" },
    { id: "2", name: "Haleem Clinic", slug: "haleem-clinic" },
  ]);
  const [activeOrg, setActiveOrg] = React.useState<Organization>(organizations[0]);
  const [showSwitchDropdown, setShowSwitchDropdown] = React.useState(false);
  const [showWizard, setShowWizard] = React.useState(false);

  // Wizard fields
  const [newOrgName, setNewOrgName] = React.useState("");
  const [newOrgSlug, setNewOrgSlug] = React.useState("");
  const [newOrgIndustry, setNewOrgIndustry] = React.useState("technology");

  const handleCreateOrg = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newOrgName || !newOrgSlug) return;
    const newOrg: Organization = {
      id: Math.random().toString(),
      name: newOrgName,
      slug: newOrgSlug.toLowerCase().replace(/\s+/g, "-"),
    };
    setOrganizations([...organizations, newOrg]);
    setActiveOrg(newOrg);
    setNewOrgName("");
    setNewOrgSlug("");
    setShowWizard(false);
  };

  return (
    <div className="min-h-screen bg-background text-foreground transition-colors duration-300">
      {/* Navigation Header */}
      <header className="border-b border-border/40 bg-card/40 backdrop-blur-md sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          <div className="flex items-center gap-6">
            <Link href="/" className="text-lg font-bold tracking-tight hover:opacity-90 transition-opacity">
              Nexora
            </Link>
            
            <div className="h-4 w-px bg-border/60" />

            {/* Tenant switcher dropdown */}
            <div className="relative">
              <button
                onClick={() => setShowSwitchDropdown(!showSwitchDropdown)}
                className="flex items-center gap-2 px-3 py-1.5 rounded-xl border border-border/50 hover:bg-card/85 text-sm font-semibold transition-all cursor-pointer"
              >
                <span>{activeOrg.name}</span>
                <svg className="w-4 h-4 text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {showSwitchDropdown && (
                <div className="absolute left-0 mt-2 w-64 rounded-2xl border border-border/50 bg-card p-2 shadow-2xl backdrop-blur-lg z-50 animate-in fade-in duration-100">
                  <div className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide px-3 py-2">
                    Switch Workspace
                  </div>
                  <div className="space-y-1">
                    {organizations.map((org) => (
                      <button
                        key={org.id}
                        onClick={() => {
                          setActiveOrg(org);
                          setShowSwitchDropdown(false);
                        }}
                        className={`w-full text-left px-3 py-2 rounded-xl text-sm font-medium transition-all cursor-pointer ${
                          org.id === activeOrg.id
                            ? "bg-primary text-primary-foreground"
                            : "hover:bg-muted text-muted-foreground hover:text-foreground"
                        }`}
                      >
                        {org.name}
                      </button>
                    ))}
                  </div>
                  <div className="border-t border-border/40 my-2 pt-2">
                    <button
                      onClick={() => {
                        setShowWizard(true);
                        setShowSwitchDropdown(false);
                      }}
                      className="w-full flex items-center justify-center gap-2 py-2 border border-dashed border-border hover:border-primary text-xs font-bold rounded-xl transition-all cursor-pointer"
                    >
                      + Create Organization
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>

          <div className="flex items-center gap-4">
            <button
              onClick={toggleTheme}
              className="p-2 rounded-xl border border-border/40 hover:bg-card text-muted-foreground hover:text-foreground transition-all cursor-pointer"
            >
              {theme === "light" ? (
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M20.354 15.354A9 9 0 018.646 3.646 9.003 9.003 0 0012 21a9.003 9.003 0 008.354-5.646z" />
                </svg>
              ) : (
                <svg className="w-5 h-5 text-yellow-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 3v1m0 16v1m9-9h-1M4 12H3m15.364-6.364l-.707.707M6.343 17.657l-.707.707m2.828 0l-.707-.707m12.728-12.728l-.707-.707M12 8a4 4 0 100 8 4 4 0 000-8z" />
                </svg>
              )}
            </button>
            <div className="h-8 w-8 rounded-full bg-gradient-to-r from-primary to-secondary flex items-center justify-center text-xs font-extrabold text-white">
              US
            </div>
          </div>
        </div>
      </header>

      {/* Main Workspace Frame */}
      <div className="max-w-7xl mx-auto px-6 py-10 flex gap-8">
        <aside className="w-64 shrink-0 hidden md:block">
          <nav className="space-y-1">
            <Link
              href="/organization"
              className="flex items-center gap-3 px-4 py-2.5 rounded-xl hover:bg-card border border-transparent hover:border-border/40 text-sm font-bold text-muted-foreground hover:text-foreground transition-all"
            >
              Organization Settings
            </Link>
            <Link
              href="/roles"
              className="flex items-center gap-3 px-4 py-2.5 rounded-xl hover:bg-card border border-transparent hover:border-border/40 text-sm font-bold text-muted-foreground hover:text-foreground transition-all"
            >
              Access Control (RBAC)
            </Link>
            <Link
              href="/billing"
              className="flex items-center gap-3 px-4 py-2.5 rounded-xl hover:bg-card border border-transparent hover:border-border/40 text-sm font-bold text-muted-foreground hover:text-foreground transition-all"
            >
              Billing & Subscription
            </Link>
            <Link
              href="/knowledge"
              className="flex items-center gap-3 px-4 py-2.5 rounded-xl hover:bg-card border border-transparent hover:border-border/40 text-sm font-bold text-muted-foreground hover:text-foreground transition-all"
            >
              Knowledge Library
            </Link>
            <Link
              href="/ai"
              className="flex items-center gap-3 px-4 py-2.5 rounded-xl hover:bg-card border border-transparent hover:border-border/40 text-sm font-bold text-muted-foreground hover:text-foreground transition-all"
            >
              AI Gateway
            </Link>
            <Link
              href="/vector"
              className="flex items-center gap-3 px-4 py-2.5 rounded-xl hover:bg-card border border-transparent hover:border-border/40 text-sm font-bold text-muted-foreground hover:text-foreground transition-all"
            >
              Vector Database
            </Link>
          </nav>
        </aside>

        <main className="flex-1 min-w-0">
          {children}
        </main>
      </div>

      {/* Create Organization Wizard Modal */}
      {showWizard && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
          <div className="bg-card border border-border rounded-3xl p-8 max-w-md w-full shadow-2xl space-y-6">
            <div className="text-center space-y-2">
              <h3 className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                CREATE ORGANIZATION
              </h3>
              <p className="text-sm text-muted-foreground font-semibold">
                Setup your secure multi-tenant workspace context
              </p>
            </div>

            <form onSubmit={handleCreateOrg} className="space-y-4">
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Organization Name</label>
                <input
                  type="text"
                  required
                  value={newOrgName}
                  onChange={(e) => {
                    setNewOrgName(e.target.value);
                    setNewOrgSlug(e.target.value.toLowerCase().replace(/\s+/g, "-"));
                  }}
                  placeholder="e.g. Acme Corp"
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Slug / URL segment</label>
                <input
                  type="text"
                  required
                  value={newOrgSlug}
                  onChange={(e) => setNewOrgSlug(e.target.value)}
                  placeholder="e.g. acme-corp"
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Industry</label>
                <select
                  value={newOrgIndustry}
                  onChange={(e) => setNewOrgIndustry(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                >
                  <option value="technology">Technology</option>
                  <option value="healthcare">Healthcare</option>
                  <option value="education">Education</option>
                  <option value="retail">Retail</option>
                </select>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowWizard(false)}
                  className="flex-1 py-2.5 border border-border text-foreground font-semibold text-xs rounded-xl hover:bg-muted transition-all cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-primary text-primary-foreground font-bold text-xs rounded-xl hover:bg-primary/90 transition-all cursor-pointer"
                >
                  Create Workspace
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
