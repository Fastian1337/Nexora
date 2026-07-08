"use client";

import * as React from "react";

interface VectorIndex {
  id: string;
  kbName: string;
  indexType: "hnsw" | "ivfflat" | "exact";
  status: "active" | "building" | "degraded";
  vectorCount: number;
  sizeMb: number;
  recallRate: number;
}

interface EmbeddingModel {
  id: string;
  name: string;
  code: string;
  dimensions: number;
  costPerM: number;
  latencyMs: number;
}

interface SearchQueryLog {
  id: string;
  query: string;
  kbName: string;
  latencyMs: number;
  results: number;
  feedback: number | null;
}

export default function VectorDashboardPage() {
  // Mock Vector Indexes
  const [indexes, setIndexes] = React.useState<VectorIndex[]>([
    { id: "idx1", kbName: "Clinic Ingestion FAQs", indexType: "hnsw", status: "active", vectorCount: 1540, sizeMb: 45.2, recallRate: 0.98 },
    { id: "idx2", kbName: "Internal SOP Manuals", indexType: "hnsw", status: "active", vectorCount: 940, sizeMb: 28.5, recallRate: 0.99 },
    { id: "idx3", kbName: "Pricing Guidelines", indexType: "hnsw", status: "building", vectorCount: 0, sizeMb: 0.0, recallRate: 1.0 },
  ]);

  // Mock Embedding Models registry
  const embeddingModels: EmbeddingModel[] = [
    { id: "em1", name: "OpenAI text-embedding-3-small", code: "text-embedding-3-small", dimensions: 1536, costPerM: 2, latencyMs: 120 },
    { id: "em2", name: "OpenAI text-embedding-3-large", code: "text-embedding-3-large", dimensions: 3072, costPerM: 13, latencyMs: 220 },
    { id: "em3", name: "Google text-embedding-004", code: "text-embedding-004", dimensions: 768, costPerM: 1, latencyMs: 90 },
    { id: "em4", name: "Sentence Transformers (Local)", code: "all-MiniLM-L6-v2", dimensions: 384, costPerM: 0, latencyMs: 30 },
  ];

  // Mock Search Logs
  const [searchLogs, setSearchLogs] = React.useState<SearchQueryLog[]>([
    { id: "q1", query: "clinic onboarding procedures", kbName: "Clinic Ingestion FAQs", latencyMs: 34, results: 5, feedback: 5 },
    { id: "q2", query: "vaccine side effects guidelines", kbName: "Clinic Ingestion FAQs", latencyMs: 48, results: 4, feedback: null },
    { id: "q3", query: "emergency operation layout", kbName: "Internal SOP Manuals", latencyMs: 28, results: 3, feedback: 4 },
  ]);

  const handleOptimizeIndex = (id: string) => {
    // Simulate background rebuilding transitions
    setIndexes(
      indexes.map((idx) => (idx.id === id ? { ...idx, status: "building" } : idx))
    );

    setTimeout(() => {
      setIndexes((prev) =>
        prev.map((idx) =>
          idx.id === id
            ? {
                ...idx,
                status: "active",
                vectorCount: idx.vectorCount + 120,
                sizeMb: Number((idx.sizeMb + 3.4).toFixed(1)),
                recallRate: 0.99,
              }
            : idx
        )
      );
    }, 2500);
  };

  const handleGiveFeedback = (logId: string, rating: number) => {
    setSearchLogs(
      searchLogs.map((log) => (log.id === logId ? { ...log, feedback: rating } : log))
    );
  };

  // Aggregated totals
  const totalVectors = indexes.reduce((acc, curr) => acc + curr.vectorCount, 0);
  const totalSizeMb = indexes.reduce((acc, curr) => acc + curr.sizeMb, 0);

  return (
    <div className="space-y-10 animate-in fade-in duration-300">
      
      {/* Title */}
      <div className="space-y-1">
        <h2 className="text-3xl font-extrabold tracking-tight">Vector Database Index Center</h2>
        <p className="text-sm text-muted-foreground font-semibold">
          Monitor multi-tenant PostgreSQL pgvector similarity caches, trigger HNSW reindexing tasks, and trace hybrid rank recall rates
        </p>
      </div>

      {/* Metrics Row */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-6">
        <div className="rounded-2xl border border-border bg-card p-6 shadow-sm flex flex-col gap-1">
          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Total Embeddings Cached</span>
          <span className="text-3xl font-extrabold text-foreground font-mono">
            {totalVectors.toLocaleString()}
          </span>
          <span className="text-[9px] text-muted-foreground/80 mt-1 font-semibold">Vectors isolated by organization</span>
        </div>
        <div className="rounded-2xl border border-border bg-card p-6 shadow-sm flex flex-col gap-1">
          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Vector Indexes Size</span>
          <span className="text-3xl font-extrabold text-foreground font-mono">
            {totalSizeMb.toFixed(1)} MB
          </span>
          <span className="text-[9px] text-muted-foreground/80 mt-1 font-semibold">PostgreSQL pgvector storage utilization</span>
        </div>
        <div className="rounded-2xl border border-border bg-card p-6 shadow-sm flex flex-col gap-1">
          <span className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Average Query Latency</span>
          <span className="text-3xl font-extrabold text-foreground font-mono">
            36.7 ms
          </span>
          <span className="text-[9px] text-muted-foreground/80 mt-1 font-semibold">Retrieval speed combined keyword + vector</span>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Left Columns: Indexes and Embedding Model registry */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* Active Indexes */}
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
            <h3 className="text-lg font-bold">Vector Indexes Monitor</h3>
            <div className="overflow-hidden rounded-xl border border-border bg-background/30">
              <table className="w-full border-collapse text-left text-sm">
                <thead>
                  <tr className="border-b border-border bg-muted/20">
                    <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px] w-2/5">Knowledge Source</th>
                    <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px]">Index Config</th>
                    <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px]">Recall</th>
                    <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px]">Status</th>
                    <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px] text-right">Actions</th>
                  </tr>
                </thead>
                <tbody>
                  {indexes.map((idx) => (
                    <tr key={idx.id} className="border-b border-border/40 last:border-0 text-xs">
                      <td className="p-3">
                        <div className="font-semibold text-foreground">{idx.kbName}</div>
                        <div className="text-[9px] text-muted-foreground font-mono mt-0.5">
                          Size: {idx.sizeMb} MB | Count: {idx.vectorCount} vectors
                        </div>
                      </td>
                      <td className="p-3 text-muted-foreground font-mono uppercase font-semibold">{idx.indexType}</td>
                      <td className="p-3 font-mono font-semibold">{(idx.recallRate * 100).toFixed(0)}%</td>
                      <td className="p-3">
                        <span className={`text-[9px] font-extrabold px-2 py-0.5 rounded-xl ${
                          idx.status === "active"
                            ? "bg-green-500/10 text-green-500"
                            : "bg-blue-500/10 text-blue-500 animate-pulse"
                        }`}>
                          {idx.status}
                        </span>
                      </td>
                      <td className="p-3 text-right">
                        <button
                          disabled={idx.status === "building"}
                          onClick={() => handleOptimizeIndex(idx.id)}
                          className="text-[10px] text-primary hover:text-primary-foreground font-bold border border-primary/20 hover:bg-primary px-2.5 py-1 rounded-lg transition-all cursor-pointer disabled:opacity-50 disabled:pointer-events-none"
                        >
                          {idx.status === "building" ? "Optimizing..." : "Rebuild HNSW"}
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* Model registries list */}
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
            <h3 className="text-lg font-bold">Embedding Model Registry</h3>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              {embeddingModels.map((em) => (
                <div key={em.id} className="p-4 rounded-xl border border-border/80 bg-background/50 space-y-2">
                  <div className="flex justify-between items-start">
                    <h4 className="text-xs font-bold text-foreground">{em.name}</h4>
                    <span className="text-[9px] font-mono font-bold bg-primary/10 text-primary px-1.5 py-0.2 rounded">
                      {em.dimensions}d
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-2 text-[10px] text-muted-foreground font-mono pt-1">
                    <div>
                      <span>Cost per 1M</span>
                      <span className="block text-foreground font-bold">${(em.costPerM / 100).toFixed(2)}</span>
                    </div>
                    <div>
                      <span>Avg Latency</span>
                      <span className="block text-foreground font-bold">{em.latencyMs}ms</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

        </div>

        {/* Right Column: Search Query log & feedback checks */}
        <div className="space-y-6">
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-4">
            <h3 className="text-lg font-bold">Search Performance Logs</h3>
            <div className="space-y-4">
              {searchLogs.map((log) => (
                <div key={log.id} className="p-4 rounded-xl border border-border/60 bg-background/20 space-y-3">
                  <div className="space-y-1">
                    <p className="text-xs font-bold text-foreground leading-snug">"{log.query}"</p>
                    <div className="flex justify-between text-[9px] text-muted-foreground font-mono">
                      <span>KB: {log.kbName}</span>
                      <span>Latency: {log.latencyMs}ms</span>
                    </div>
                  </div>

                  <div className="flex items-center justify-between border-t border-border/40 pt-2.5">
                    <span className="text-[9px] text-muted-foreground font-bold">Relevance Rating:</span>
                    <div className="flex gap-1">
                      {[1, 2, 3, 4, 5].map((star) => (
                        <button
                          key={star}
                          onClick={() => handleGiveFeedback(log.id, star)}
                          className={`text-xs cursor-pointer transition-all ${
                            log.feedback && log.feedback >= star
                              ? "text-yellow-500 scale-110"
                              : "text-muted-foreground hover:text-yellow-500"
                          }`}
                        >
                          ★
                        </button>
                      ))}
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

      </div>

    </div>
  );
}
