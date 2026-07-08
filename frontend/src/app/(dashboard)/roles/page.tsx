"use client";

import * as React from "react";

interface Permission {
  id: string;
  module: string;
  code: string;
  description: string;
}

interface Role {
  id: string;
  name: string;
  slug: string;
  description: string;
  isSystem: boolean;
  priority: number;
  permissions: string[];
}

export default function RolesPage() {
  // Mock permissions
  const [permissions] = React.useState<Permission[]>([
    { id: "1", module: "users", code: "users.create", description: "Create organization users" },
    { id: "2", module: "users", code: "users.read", description: "View organization users list" },
    { id: "3", module: "users", code: "users.update", description: "Update user profiles" },
    { id: "4", module: "users", code: "users.delete", description: "Remove user accounts" },
    { id: "5", module: "chat", code: "chat.reply", description: "Send chat completions or agent replies" },
    { id: "6", module: "voice", code: "voice.call", description: "Initiate voice call campaigns" },
    { id: "7", module: "marketing", code: "marketing.publish", description: "Auto publish social channels posts" },
  ]);

  // Mock roles
  const [roles, setRoles] = React.useState<Role[]>([
    {
      id: "1",
      name: "Organization Owner",
      slug: "owner",
      description: "Full control over organization resources",
      isSystem: true,
      priority: 100,
      permissions: ["users.create", "users.read", "users.update", "users.delete", "chat.reply", "voice.call", "marketing.publish"],
    },
    {
      id: "2",
      name: "Receptionist",
      slug: "receptionist",
      description: "Manage chats and schedules",
      isSystem: true,
      priority: 60,
      permissions: ["users.read", "chat.reply"],
    },
    {
      id: "3",
      name: "Employee",
      slug: "employee",
      description: "Standard workspace collaborator",
      isSystem: true,
      priority: 30,
      permissions: ["users.read", "chat.reply"],
    },
  ]);

  // Custom role state
  const [showCreateModal, setShowCreateModal] = React.useState(false);
  const [roleName, setRoleName] = React.useState("");
  const [roleSlug, setRoleSlug] = React.useState("");
  const [roleDesc, setRoleDesc] = React.useState("");
  const [selectedPerms, setSelectedPerms] = React.useState<string[]>([]);

  // Assignment state
  const [showAssignModal, setShowAssignModal] = React.useState(false);
  const [assignUserEmail, setAssignUserEmail] = React.useState("");
  const [assignRoleId, setAssignRoleId] = React.useState(roles[1].id);

  const handleTogglePerm = (code: string) => {
    if (selectedPerms.includes(code)) {
      setSelectedPerms(selectedPerms.filter((p) => p !== code));
    } else {
      setSelectedPerms([...selectedPerms, code]);
    }
  };

  const handleCreateRole = (e: React.FormEvent) => {
    e.preventDefault();
    if (!roleName || !roleSlug) return;
    const newRole: Role = {
      id: Math.random().toString(),
      name: roleName,
      slug: roleSlug.toLowerCase().replace(/\s+/g, "_"),
      description: roleDesc,
      isSystem: false,
      priority: 10,
      permissions: selectedPerms,
    };
    setRoles([...roles, newRole]);
    setRoleName("");
    setRoleSlug("");
    setRoleDesc("");
    setSelectedPerms([]);
    setShowCreateModal(false);
  };

  const handleAssignRole = (e: React.FormEvent) => {
    e.preventDefault();
    if (!assignUserEmail) return;
    alert(`Assigned role successfully to ${assignUserEmail}`);
    setAssignUserEmail("");
    setShowAssignModal(false);
  };

  return (
    <div className="space-y-10 animate-in fade-in duration-300">
      
      {/* Title */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-3xl font-extrabold tracking-tight">Access Management (RBAC)</h2>
          <p className="text-sm text-muted-foreground font-semibold">
            Define system scopes, design custom client roles, and control teammate permissions
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowAssignModal(true)}
            className="px-4 py-2 border border-border hover:bg-card text-foreground font-bold text-xs rounded-xl transition-all cursor-pointer"
          >
            Assign Teammate Role
          </button>
          <button
            onClick={() => setShowCreateModal(true)}
            className="px-4 py-2 bg-primary text-primary-foreground hover:bg-primary/95 font-bold text-xs rounded-xl transition-all cursor-pointer"
          >
            + Create Custom Role
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Roles Grid Cards */}
        <div className="lg:col-span-2 space-y-6">
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
            <h3 className="text-lg font-bold">Workspace Roles</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {roles.map((role) => (
                <div
                  key={role.id}
                  className="p-5 rounded-xl border border-border/80 bg-background/50 space-y-4 flex flex-col justify-between"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-bold text-foreground">{role.name}</h4>
                      <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded-xl ${
                        role.isSystem
                          ? "bg-primary/10 text-primary"
                          : "bg-purple-500/10 text-purple-500"
                      }`}>
                        {role.isSystem ? "System" : "Custom"}
                      </span>
                    </div>
                    <p className="text-xs text-muted-foreground leading-relaxed">{role.description}</p>
                  </div>
                  <div className="pt-2 flex items-center justify-between text-[10px] text-muted-foreground font-mono">
                    <span>Priority: {role.priority}</span>
                    <span>{role.permissions.length} Permissions</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Permissions Matrix */}
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
            <h3 className="text-lg font-bold">Permissions Matrix</h3>
            <div className="overflow-hidden rounded-xl border border-border bg-background/30">
              <table className="w-full border-collapse text-left text-sm">
                <thead>
                  <tr className="border-b border-border bg-muted/20">
                    <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px] w-1/3">Permission</th>
                    {roles.map((role) => (
                      <th
                        key={role.id}
                        className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px] text-center"
                      >
                        {role.name}
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {permissions.map((perm) => (
                    <tr key={perm.id} className="border-b border-border/40 last:border-0">
                      <td className="p-3">
                        <div className="font-semibold text-xs">{perm.code}</div>
                        <div className="text-[10px] text-muted-foreground">{perm.description}</div>
                      </td>
                      {roles.map((role) => {
                        const hasPerm = role.permissions.includes(perm.code);
                        return (
                          <td key={role.id} className="p-3 text-center">
                            <span className={`inline-block h-2 w-2 rounded-full ${
                              hasPerm ? "bg-green-500" : "bg-muted/80"
                            }`} />
                          </td>
                        );
                      })}
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        </div>

        {/* Permissions catalog sidebar */}
        <div className="space-y-6">
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
            <h3 className="text-lg font-bold">Capability Catalog</h3>
            <div className="space-y-3">
              {permissions.map((perm) => (
                <div key={perm.id} className="p-3 rounded-xl border border-border/60 bg-background/20 space-y-1">
                  <div className="flex items-center justify-between">
                    <span className="text-xs font-mono font-bold text-primary">{perm.code}</span>
                    <span className="text-[9px] uppercase font-bold text-muted-foreground px-2 py-0.5 rounded-xl bg-muted/50">
                      {perm.module}
                    </span>
                  </div>
                  <p className="text-[11px] text-muted-foreground leading-normal">{perm.description}</p>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>

      {/* Create Custom Role Wizard Modal */}
      {showCreateModal && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
          <div className="bg-card border border-border rounded-3xl p-8 max-w-lg w-full shadow-2xl space-y-6 max-h-[85vh] overflow-y-auto">
            <div className="text-center space-y-2">
              <h3 className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                CREATE CUSTOM ROLE
              </h3>
              <p className="text-sm text-muted-foreground font-semibold">
                Setup custom scopes and capabilities for your team
              </p>
            </div>

            <form onSubmit={handleCreateRole} className="space-y-4">
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Role Name</label>
                <input
                  type="text"
                  required
                  value={roleName}
                  onChange={(e) => {
                    setRoleName(e.target.value);
                    setRoleSlug(e.target.value.toLowerCase().replace(/\s+/g, "_"));
                  }}
                  placeholder="e.g. Content Writer"
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Role Identifier Slug</label>
                <input
                  type="text"
                  required
                  value={roleSlug}
                  onChange={(e) => setRoleSlug(e.target.value)}
                  placeholder="e.g. content_writer"
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Description</label>
                <input
                  type="text"
                  value={roleDesc}
                  onChange={(e) => setRoleDesc(e.target.value)}
                  placeholder="Can draft campaign posts..."
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                />
              </div>

              {/* Permissions Checkbox Selection */}
              <div className="space-y-2">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Assign Scopes</label>
                <div className="border border-border rounded-xl p-3 bg-background/30 space-y-2 max-h-40 overflow-y-auto">
                  {permissions.map((perm) => {
                    const isChecked = selectedPerms.includes(perm.code);
                    return (
                      <label key={perm.id} className="flex items-start gap-2.5 p-1.5 hover:bg-muted/40 rounded-lg cursor-pointer">
                        <input
                          type="checkbox"
                          checked={isChecked}
                          onChange={() => handleTogglePerm(perm.code)}
                          className="mt-0.5"
                        />
                        <div className="space-y-0.5">
                          <div className="text-xs font-mono font-bold">{perm.code}</div>
                          <div className="text-[10px] text-muted-foreground">{perm.description}</div>
                        </div>
                      </label>
                    );
                  })}
                </div>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateModal(false)}
                  className="flex-1 py-2.5 border border-border text-foreground font-semibold text-xs rounded-xl hover:bg-muted transition-all cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-primary text-primary-foreground font-bold text-xs rounded-xl hover:bg-primary/90 transition-all cursor-pointer"
                >
                  Create Custom Role
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Assign Role Modal */}
      {showAssignModal && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
          <div className="bg-card border border-border rounded-3xl p-8 max-w-md w-full shadow-2xl space-y-6">
            <div className="text-center space-y-2">
              <h3 className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                ASSIGN TEAMMATE ROLE
              </h3>
              <p className="text-sm text-muted-foreground font-semibold">
                Link an access role mapping to a registered colleague email
              </p>
            </div>

            <form onSubmit={handleAssignRole} className="space-y-4">
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Teammate Email</label>
                <input
                  type="email"
                  required
                  value={assignUserEmail}
                  onChange={(e) => setAssignUserEmail(e.target.value)}
                  placeholder="colleague@company.com"
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Select Role</label>
                <select
                  value={assignRoleId}
                  onChange={(e) => setAssignRoleId(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                >
                  {roles.map((r) => (
                    <option key={r.id} value={r.id}>{r.name}</option>
                  ))}
                </select>
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowAssignModal(false)}
                  className="flex-1 py-2.5 border border-border text-foreground font-semibold text-xs rounded-xl hover:bg-muted transition-all cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-primary text-primary-foreground font-bold text-xs rounded-xl hover:bg-primary/90 transition-all cursor-pointer"
                >
                  Confirm Assignment
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
