"use client";

import * as React from "react";

interface Member {
  id: string;
  email: string;
  role: string;
  joinedAt: string;
}

export default function OrganizationPage() {
  const [name, setName] = React.useState("Nexora Technologies");
  const [industry, setIndustry] = React.useState("technology");
  const [size, setSize] = React.useState("10-50");
  const [email, setEmail] = React.useState("info@nexora.ai");
  const [phone, setPhone] = React.useState("+92 300 1234567");
  const [website, setWebsite] = React.useState("https://nexora.ai");
  
  // Settings
  const [themeMode, setThemeMode] = React.useState("dark");
  const [voiceDialect, setVoiceDialect] = React.useState("en-US");
  const [brandColor, setBrandColor] = React.useState("#2563EB");

  // Invitation
  const [showInviteModal, setShowInviteModal] = React.useState(false);
  const [inviteEmail, setInviteEmail] = React.useState("");
  const [inviteRole, setInviteRole] = React.useState("employee");
  
  const [members, setMembers] = React.useState<Member[]>([
    { id: "1", email: "saif@nexora.ai", role: "Owner", joinedAt: "2026-07-07" },
    { id: "2", email: "assistant@nexora.ai", role: "Receptionist", joinedAt: "2026-07-08" },
  ]);

  const handleInvite = (e: React.FormEvent) => {
    e.preventDefault();
    if (!inviteEmail) return;
    const newMember: Member = {
      id: Math.random().toString(),
      email: inviteEmail,
      role: inviteRole.charAt(0).toUpperCase() + inviteRole.slice(1),
      joinedAt: new Date().toISOString().split("T")[0],
    };
    setMembers([...members, newMember]);
    setInviteEmail("");
    setShowInviteModal(false);
  };

  return (
    <div className="space-y-10 animate-in fade-in duration-300">
      
      {/* Title */}
      <div className="space-y-1">
        <h2 className="text-3xl font-extrabold tracking-tight">Organization Profile</h2>
        <p className="text-sm text-muted-foreground font-semibold">
          Manage your business metadata, team memberships, and brand identity
        </p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Profile Card Settings */}
        <div className="lg:col-span-2 space-y-6">
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-6">
            <h3 className="text-lg font-bold">Business Parameters</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Business Name</label>
                <input
                  type="text"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Industry</label>
                <input
                  type="text"
                  value={industry}
                  onChange={(e) => setIndustry(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Company Size</label>
                <input
                  type="text"
                  value={size}
                  onChange={(e) => setSize(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Phone Number</label>
                <input
                  type="text"
                  value={phone}
                  onChange={(e) => setPhone(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Website</label>
                <input
                  type="text"
                  value={website}
                  onChange={(e) => setWebsite(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                />
              </div>
            </div>
            
            <button className="px-5 py-2.5 bg-primary text-primary-foreground font-bold text-xs rounded-xl hover:bg-primary/95 transition-all cursor-pointer">
              Save Parameters
            </button>
          </div>

          {/* Members Table */}
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
            <div className="flex items-center justify-between">
              <h3 className="text-lg font-bold">Teammates & Access</h3>
              <button
                onClick={() => setShowInviteModal(true)}
                className="px-4 py-2 border border-dashed border-border hover:border-primary hover:text-primary font-bold text-xs rounded-xl transition-all cursor-pointer"
              >
                + Invite Teammate
              </button>
            </div>

            <div className="overflow-hidden rounded-xl border border-border bg-background/30">
              <table className="w-full border-collapse text-left text-sm">
                <thead>
                  <tr className="border-b border-border bg-muted/20">
                    <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px]">Email</th>
                    <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px]">Workspace Role</th>
                    <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px]">Joined At</th>
                  </tr>
                </thead>
                <tbody>
                  {members.map((member) => (
                    <tr key={member.id} className="border-b border-border/40 last:border-0">
                      <td className="p-3 font-medium">{member.email}</td>
                      <td className="p-3">
                        <span className={`px-2.5 py-0.5 rounded-full text-xs font-bold ${
                          member.role === "Owner"
                            ? "bg-primary/10 text-primary"
                            : "bg-muted text-muted-foreground"
                        }`}>
                          {member.role}
                        </span>
                      </td>
                      <td className="p-3 text-muted-foreground text-sm">{member.joinedAt}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Brand Customization settings */}
        <div className="space-y-6">
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-6">
            <h3 className="text-lg font-bold">Brand Styling</h3>
            
            {/* Logo placeholder upload */}
            <div className="space-y-2">
              <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Logo Uploader</label>
              <div className="border border-dashed border-border/80 rounded-xl p-6 text-center hover:border-primary transition-all cursor-pointer bg-background/30">
                <svg className="w-8 h-8 mx-auto text-muted-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <span className="inline-block text-xs font-semibold text-muted-foreground mt-2">
                  Drop logo image here or click to browse
                </span>
              </div>
            </div>

            <div className="space-y-4">
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Primary Branding Color</label>
                <div className="flex gap-2">
                  <input
                    type="color"
                    value={brandColor}
                    onChange={(e) => setBrandColor(e.target.value)}
                    className="h-8 w-8 rounded-xl border border-border cursor-pointer"
                  />
                  <input
                    type="text"
                    value={brandColor}
                    onChange={(e) => setBrandColor(e.target.value)}
                    className="flex-1 px-3 py-1.5 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all font-mono"
                  />
                </div>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Voice Language model</label>
                <select
                  value={voiceDialect}
                  onChange={(e) => setVoiceDialect(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                >
                  <option value="en-US">English (US)</option>
                  <option value="en-GB">English (UK)</option>
                  <option value="ur-PK">Urdu (Pakistan)</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Default UI Theme</label>
                <select
                  value={themeMode}
                  onChange={(e) => setThemeMode(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                >
                  <option value="dark">Dark Theme (Midnight Navy)</option>
                  <option value="light">Light Theme (Cloud White)</option>
                </select>
              </div>
            </div>
            
            <button className="w-full py-2.5 bg-gradient-to-r from-primary to-secondary text-white font-bold text-sm rounded-xl transition-all shadow-md">
              Save Brand Setup
            </button>
          </div>
        </div>

      </div>

      {/* Invite Modal */}
      {showInviteModal && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
          <div className="bg-card border border-border rounded-3xl p-8 max-w-md w-full shadow-2xl space-y-6">
            <div className="text-center space-y-2">
              <h3 className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                INVITE TEAMMATE
              </h3>
              <p className="text-sm text-muted-foreground font-semibold">
                Send an invitation to join your tenant organization
              </p>
            </div>

            <form onSubmit={handleInvite} className="space-y-4">
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Email Address</label>
                <input
                  type="email"
                  required
                  value={inviteEmail}
                  onChange={(e) => setInviteEmail(e.target.value)}
                  placeholder="e.g. colleague@company.com"
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Workspace Role</label>
                <select
                  value={inviteRole}
                  onChange={(e) => setInviteRole(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                >
                  <option value="admin">Admin</option>
                  <option value="manager">Manager</option>
                  <option value="employee">Employee</option>
                  <option value="receptionist">Receptionist</option>
                </select>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowInviteModal(false)}
                  className="flex-1 py-2.5 border border-border text-foreground font-semibold text-xs rounded-xl hover:bg-muted transition-all cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-primary text-primary-foreground font-bold text-xs rounded-xl hover:bg-primary/90 transition-all cursor-pointer"
                >
                  Send Invitation
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
