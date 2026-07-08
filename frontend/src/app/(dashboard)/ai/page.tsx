"use client";

import * as React from "react";

interface AIProvider {
  id: string;
  name: string;
  code: string;
  baseUrl: string;
  status: "active" | "inactive";
  latencyMs: number;
  uptime: number;
}

interface AIModel {
  id: string;
  name: string;
  code: string;
  providerCode: string;
  contextWindow: number;
  promptCostPerM: number;
  completionCostPerM: number;
  status: "active" | "inactive";
}

interface PromptTemplate {
  id: string;
  name: string;
  code: string;
  systemPrompt: string;
  userPrompt: string;
  variables: string[];
}

export default function AiGatewayPage() {
  // Mock AI Providers
  const [providers, setProviders] = React.useState<AIProvider[]>([
    { id: "1", name: "OpenAI API", code: "openai", baseUrl: "https://api.openai.com/v1", status: "active", latencyMs: 450, uptime: 99.98 },
    { id: "2", name: "Google Gemini", code: "gemini", baseUrl: "https://generativelanguage.googleapis.com/v1", status: "active", latencyMs: 320, uptime: 99.95 },
    { id: "3", name: "Anthropic Claude", code: "anthropic", baseUrl: "https://api.anthropic.com/v1", status: "active", latencyMs: 780, uptime: 99.9 },
    { id: "4", name: "Local Ollama", code: "ollama", baseUrl: "http://localhost:11434/v1", status: "inactive", latencyMs: 0, uptime: 100.0 },
  ]);

  // Mock Model Registry
  const [models, setModels] = React.useState<AIModel[]>([
    { id: "m1", name: "GPT-4o", code: "gpt-4o", providerCode: "openai", contextWindow: 128000, promptCostPerM: 300, completionCostPerM: 1500, status: "active" },
    { id: "m2", name: "Gemini 1.5 Pro", code: "gemini-1.5-pro", providerCode: "gemini", contextWindow: 1000000, promptCostPerM: 125, completionCostPerM: 375, status: "active" },
    { id: "m3", name: "Claude 3.5 Sonnet", code: "claude-3-5-sonnet", providerCode: "anthropic", contextWindow: 200000, promptCostPerM: 300, completionCostPerM: 1500, status: "active" },
  ]);

  // Mock Prompt templates
  const [prompts, setPrompts] = React.useState<PromptTemplate[]>([
    { id: "p1", name: "Customer Receptionist Welcome", code: "receptionist_welcome", systemPrompt: "You are a receptionist at {{clinic_name}}. Welcome {{patient_name}}...", userPrompt: "Welcome!", variables: ["clinic_name", "patient_name"] },
    { id: "p2", name: "Admission Policies Assistant", code: "admission_assistant", systemPrompt: "Explain standard admission fee: {{base_fee}}...", userPrompt: "Explain details.", variables: ["base_fee"] },
  ]);

  // Telemetry logs stats
  const usageStats = [
    { model: "GPT-4o", requests: 1240, promptTokens: 345000, completionTokens: 189000, cost: 2.14 },
    { model: "Gemini 1.5 Pro", requests: 890, promptTokens: 420000, completionTokens: 98000, cost: 0.89 },
    { model: "Claude 3.5 Sonnet", requests: 450, promptTokens: 120000, completionTokens: 60000, cost: 1.26 },
  ];

  // Forms state
  const [showConfigProviderModal, setShowConfigProviderModal] = React.useState(false);
  const [selectedProvider, setSelectedProvider] = React.useState<AIProvider | null>(null);
  const [providerUrl, setProviderUrl] = React.useState("");
  const [providerKey, setProviderKey] = React.useState("");

  const [showPromptModal, setShowPromptModal] = React.useState(false);
  const [promptName, setPromptName] = React.useState("");
  const [promptCode, setPromptCode] = React.useState("");
  const [sysPrompt, setSysPrompt] = React.useState("");
  const [userPromptText, setUserPromptText] = React.useState("");

  const handleToggleProvider = (id: string) => {
    setProviders(
      providers.map((p) => (p.id === id ? { ...p, status: p.status === "active" ? "inactive" : "active" } : p))
    );
  };

  const handleConfigureProvider = (e: React.FormEvent) => {
    e.preventDefault();
    if (selectedProvider) {
      setProviders(
        providers.map((p) => (p.id === selectedProvider.id ? { ...p, baseUrl: providerUrl } : p))
      );
      setShowConfigProviderModal(false);
      setProviderKey("");
    }
  };

  const handleCreatePrompt = (e: React.FormEvent) => {
    e.preventDefault();
    if (!promptName || !promptCode) return;
    
    // Parse variables matching {{variable}}
    const varRegex = /\{\{([^}]+)\}\}/g;
    const matches = [];
    let match;
    while ((match = varRegex.exec(sysPrompt)) !== null) {
      matches.push(match[1].trim());
    }

    const newPrompt: PromptTemplate = {
      id: Math.random().toString(),
      name: promptName,
      code: promptCode.toLowerCase().replace(/\s+/g, "_"),
      systemPrompt: sysPrompt,
      userPrompt: userPromptText,
      variables: Array.from(new Set(matches)),
    };

    setPrompts([...prompts, newPrompt]);
    setPromptName("");
    setPromptCode("");
    setSysPrompt("");
    setUserPromptText("");
    setShowPromptModal(false);
  };

  return (
    <div className="space-y-10 animate-in fade-in duration-300">
      
      {/* Title */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-3xl font-extrabold tracking-tight">AI Gateway Control Room</h2>
          <p className="text-sm text-muted-foreground font-semibold">
            Manage LLM provider credentials, model fallback routing rules, prompt template versioning, and token usage cost logs
          </p>
        </div>
        <button
          onClick={() => setShowPromptModal(true)}
          className="px-4 py-2 bg-primary text-primary-foreground hover:bg-primary/95 font-bold text-xs rounded-xl transition-all cursor-pointer"
        >
          + Create Prompt Template
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Side: Providers List & Prompts */}
        <div className="lg:col-span-2 space-y-6">
          
          {/* AI Providers list */}
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
            <h3 className="text-lg font-bold">AI Providers Status</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {providers.map((p) => (
                <div
                  key={p.id}
                  className="p-5 rounded-xl border border-border/80 bg-background/50 flex flex-col justify-between gap-4"
                >
                  <div className="space-y-2">
                    <div className="flex items-center justify-between">
                      <h4 className="text-sm font-bold text-foreground">{p.name}</h4>
                      <span className={`text-[10px] font-extrabold px-2 py-0.5 rounded-xl ${
                        p.status === "active"
                          ? "bg-green-500/10 text-green-500"
                          : "bg-muted/80 text-muted-foreground"
                      }`}>
                        {p.status}
                      </span>
                    </div>
                    <p className="text-[10px] text-muted-foreground font-mono truncate">{p.baseUrl}</p>
                    {p.status === "active" && (
                      <div className="flex gap-4 text-[10px] text-muted-foreground font-mono pt-1">
                        <span>Latency: {p.latencyMs}ms</span>
                        <span>Uptime: {p.uptime}%</span>
                      </div>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <button
                      onClick={() => handleToggleProvider(p.id)}
                      className={`flex-1 py-1.5 border font-bold text-[10px] rounded-lg transition-all cursor-pointer ${
                        p.status === "active"
                          ? "border-red-500/30 hover:bg-red-500/10 text-red-500"
                          : "border-green-500/30 hover:bg-green-500/10 text-green-500"
                      }`}
                    >
                      {p.status === "active" ? "Deactivate" : "Activate"}
                    </button>
                    <button
                      onClick={() => {
                        setSelectedProvider(p);
                        setProviderUrl(p.baseUrl);
                        setShowConfigProviderModal(true);
                      }}
                      className="flex-1 py-1.5 border border-border hover:bg-card text-foreground font-bold text-[10px] rounded-lg transition-all cursor-pointer"
                    >
                      Configure
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Prompt Templates */}
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
            <h3 className="text-lg font-bold">Variables Prompt templates</h3>
            <div className="space-y-4">
              {prompts.map((pt) => (
                <div key={pt.id} className="p-4 rounded-xl border border-border/80 bg-background/50 space-y-3">
                  <div className="flex items-center justify-between">
                    <div>
                      <h4 className="text-xs font-bold text-foreground">{pt.name}</h4>
                      <span className="text-[9px] font-mono text-muted-foreground">Code: {pt.code}</span>
                    </div>
                    <div className="flex gap-1.5">
                      {pt.variables.map((v) => (
                        <span key={v} className="text-[9px] px-2 py-0.5 rounded bg-primary/10 text-primary font-mono font-bold">
                          {"{" + v + "}"}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-background/90 border border-border/40 text-[10px] text-muted-foreground font-mono leading-relaxed max-h-20 overflow-y-auto">
                    {pt.systemPrompt}
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Right Side: Cost telemetry usage graphs */}
        <div className="space-y-6">
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
            <h3 className="text-lg font-bold">Token Cost Analytics</h3>
            <div className="space-y-4">
              {usageStats.map((stat, i) => {
                const totalTokens = stat.promptTokens + stat.completionTokens;
                return (
                  <div key={i} className="p-4 rounded-xl border border-border/60 bg-background/20 space-y-3">
                    <div className="flex justify-between items-start">
                      <span className="text-xs font-bold text-foreground">{stat.model}</span>
                      <span className="text-xs font-extrabold text-primary">${stat.cost.toFixed(2)} USD</span>
                    </div>
                    
                    <div className="grid grid-cols-2 gap-2 text-[10px] text-muted-foreground font-mono border-t border-border/40 pt-2.5">
                      <div className="space-y-0.5">
                        <span>Requests count</span>
                        <span className="block text-foreground font-bold">{stat.requests} runs</span>
                      </div>
                      <div className="space-y-0.5">
                        <span>Total token usage</span>
                        <span className="block text-foreground font-bold">{(totalTokens / 1000).toFixed(1)}k tokens</span>
                      </div>
                    </div>
                  </div>
                );
              })}
            </div>
          </div>
        </div>

      </div>

      {/* Configure Provider Modal */}
      {showConfigProviderModal && selectedProvider && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
          <div className="bg-card border border-border rounded-3xl p-8 max-w-md w-full shadow-2xl space-y-6">
            <div className="text-center space-y-2">
              <h3 className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                CONFIGURE {selectedProvider.name}
              </h3>
              <p className="text-sm text-muted-foreground font-semibold">
                Update base URL addresses and credential hashes safely
              </p>
            </div>

            <form onSubmit={handleConfigureProvider} className="space-y-4">
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Base Endpoint URL</label>
                <input
                  type="text"
                  required
                  value={providerUrl}
                  onChange={(e) => setProviderUrl(e.target.value)}
                  placeholder="https://api.provider.com/v1"
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all font-mono"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">API Key Credentials (Encrypted)</label>
                <input
                  type="password"
                  value={providerKey}
                  onChange={(e) => setProviderKey(e.target.value)}
                  placeholder="sk-••••••••••••••••••••••••"
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all font-mono"
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowConfigProviderModal(false)}
                  className="flex-1 py-2.5 border border-border text-foreground font-semibold text-xs rounded-xl hover:bg-muted transition-all cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-primary text-primary-foreground font-bold text-xs rounded-xl hover:bg-primary/90 transition-all cursor-pointer"
                >
                  Update Provider
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Create Prompt Template Modal */}
      {showPromptModal && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
          <div className="bg-card border border-border rounded-3xl p-8 max-w-lg w-full shadow-2xl space-y-6 max-h-[85vh] overflow-y-auto">
            <div className="text-center space-y-2">
              <h3 className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                CREATE PROMPT TEMPLATE
              </h3>
              <p className="text-sm text-muted-foreground font-semibold">
                Build variables-based system instructions
              </p>
            </div>

            <form onSubmit={handleCreatePrompt} className="space-y-4">
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Template Title</label>
                <input
                  type="text"
                  required
                  value={promptName}
                  onChange={(e) => setPromptName(e.target.value)}
                  placeholder="Patient Reception Greeting"
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Identifier Code</label>
                <input
                  type="text"
                  required
                  value={promptCode}
                  onChange={(e) => setPromptCode(e.target.value)}
                  placeholder="reception_greeting"
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">System Prompt (Use `{{variable}}` formats)</label>
                <textarea
                  required
                  value={sysPrompt}
                  onChange={(e) => setSysPrompt(e.target.value)}
                  placeholder="You are an assistant at {{clinic_name}}. Welcome patients for their {{appointment_reason}}..."
                  rows={4}
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all resize-none leading-relaxed"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Default User Message</label>
                <input
                  type="text"
                  value={userPromptText}
                  onChange={(e) => setUserPromptText(e.target.value)}
                  placeholder="Welcome patient."
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowPromptModal(false)}
                  className="flex-1 py-2.5 border border-border text-foreground font-semibold text-xs rounded-xl hover:bg-muted transition-all cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-primary text-primary-foreground font-bold text-xs rounded-xl hover:bg-primary/90 transition-all cursor-pointer"
                >
                  Register Template
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
