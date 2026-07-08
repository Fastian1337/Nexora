"use client";

import * as React from "react";

interface KnowledgeBase {
  id: string;
  name: string;
  description: string;
  category: string;
  isArchived: boolean;
  documentCount: number;
}

interface IngestedDocument {
  id: string;
  kbId: string;
  title: string;
  status: "Ready" | "Processing" | "Embedding" | "Failed";
  author: string;
  sizeKb: number;
  tags: string[];
  chunksCount: number;
}

export default function KnowledgePage() {
  // Mock knowledge bases
  const [kbList, setKbList] = React.useState<KnowledgeBase[]>([
    { id: "kb1", name: "Clinic Ingestion FAQs", description: "Frequently asked questions for incoming patients", category: "Clinic", isArchived: false, documentCount: 2 },
    { id: "kb2", name: "Internal SOP Manuals", description: "Standard operating procedures for staff members", category: "Operations", isArchived: false, documentCount: 1 },
    { id: "kb3", name: "Pricing Guidelines", description: "Pricing sheets for services and custom branding plans", category: "Sales", isArchived: false, documentCount: 0 },
  ]);

  // Mock ingested documents list
  const [documents, setDocuments] = React.useState<IngestedDocument[]>([
    { id: "doc1", kbId: "kb1", title: "incoming_patient_onboarding.pdf", status: "Ready", author: "Dr. Sarah", sizeKb: 345, tags: ["patient", "onboarding"], chunksCount: 12 },
    { id: "doc2", kbId: "kb1", title: "vaccination_faqs.txt", status: "Embedding", author: "Nurse John", sizeKb: 24, tags: ["vaccines", "faqs"], chunksCount: 3 },
    { id: "doc3", kbId: "kb2", title: "clinic_emergency_sop.docx", status: "Ready", author: "Admin Staff", sizeKb: 1540, tags: ["emergency", "sop"], chunksCount: 45 },
  ]);

  const [activeKbId, setActiveKbId] = React.useState("kb1");
  const [searchQuery, setSearchQuery] = React.useState("");

  // Modals state
  const [showCreateKbModal, setShowCreateKbModal] = React.useState(false);
  const [newKbName, setNewKbName] = React.useState("");
  const [newKbDesc, setNewKbDesc] = React.useState("");
  const [newKbCat, setNewKbCat] = React.useState("Clinic");

  const [showUploadModal, setShowUploadModal] = React.useState(false);
  const [uploadFileName, setUploadFileName] = React.useState("");
  const [uploadAuthor, setUploadAuthor] = React.useState("");
  const [uploadTags, setUploadTags] = React.useState("");
  const [chunkSize, setChunkSize] = React.useState(1000);
  const [chunkOverlap, setChunkOverlap] = React.useState(200);

  const handleCreateKb = (e: React.FormEvent) => {
    e.preventDefault();
    if (!newKbName) return;
    const newKb: KnowledgeBase = {
      id: `kb${Math.random().toString()}`,
      name: newKbName,
      description: newKbDesc,
      category: newKbCat,
      isArchived: false,
      documentCount: 0,
    };
    setKbList([...kbList, newKb]);
    setNewKbName("");
    setNewKbDesc("");
    setShowCreateKbModal(false);
  };

  const handleUploadDoc = (e: React.FormEvent) => {
    e.preventDefault();
    if (!uploadFileName) return;
    
    const newDoc: IngestedDocument = {
      id: `doc${Math.random().toString()}`,
      kbId: activeKbId,
      title: uploadFileName.endsWith(".txt") || uploadFileName.endsWith(".pdf") ? uploadFileName : `${uploadFileName}.txt`,
      status: "Processing",
      author: uploadAuthor || "Teammate",
      sizeKb: Math.floor(Math.random() * 500) + 12,
      tags: uploadTags ? uploadTags.split(",").map((t) => t.trim()) : [],
      chunksCount: 0,
    };
    
    setDocuments([...documents, newDoc]);
    
    // Simulate pipeline transitions
    setTimeout(() => {
      setDocuments((prev) =>
        prev.map((d) => (d.id === newDoc.id ? { ...d, status: "Embedding" } : d))
      );
    }, 1500);

    setTimeout(() => {
      setDocuments((prev) =>
        prev.map((d) => (d.id === newDoc.id ? { ...d, status: "Ready", chunksCount: Math.floor(Math.random() * 20) + 4 } : d))
      );
      // Increment doc count on KB
      setKbList((prev) =>
        prev.map((k) => (k.id === activeKbId ? { ...k, documentCount: k.documentCount + 1 } : k))
      );
    }, 3000);

    setUploadFileName("");
    setUploadAuthor("");
    setUploadTags("");
    setShowUploadModal(false);
  };

  const handleDeleteDoc = (docId: string, docKbId: string) => {
    if (confirm("Are you sure you want to delete this document from the Knowledge Base?")) {
      setDocuments(documents.filter((d) => d.id !== docId));
      setKbList(
        kbList.map((k) => (k.id === docKbId ? { ...k, documentCount: Math.max(0, k.documentCount - 1) } : k))
      );
    }
  };

  const filteredDocs = documents.filter(
    (d) =>
      d.kbId === activeKbId &&
      (d.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        d.author.toLowerCase().includes(searchQuery.toLowerCase()))
  );

  return (
    <div className="space-y-10 animate-in fade-in duration-300">
      
      {/* Title */}
      <div className="flex items-center justify-between">
        <div className="space-y-1">
          <h2 className="text-3xl font-extrabold tracking-tight">Knowledge Base Library</h2>
          <p className="text-sm text-muted-foreground font-semibold">
            Ingest unstructured documents, configure chunk splitters, and feed semantic prompt builders
          </p>
        </div>
        <div className="flex gap-3">
          <button
            onClick={() => setShowCreateKbModal(true)}
            className="px-4 py-2 border border-border hover:bg-card text-foreground font-bold text-xs rounded-xl transition-all cursor-pointer"
          >
            + Create Knowledge Base
          </button>
          <button
            onClick={() => setShowUploadModal(true)}
            className="px-4 py-2 bg-primary text-primary-foreground hover:bg-primary/95 font-bold text-xs rounded-xl transition-all cursor-pointer"
          >
            ↑ Ingest Document
          </button>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Knowledge Base Side Selectors List */}
        <div className="space-y-4">
          <div className="rounded-2xl border border-border bg-card p-5 shadow-sm space-y-4">
            <h3 className="text-sm font-bold uppercase tracking-wider text-muted-foreground">Knowledge Sources</h3>
            <div className="space-y-2">
              {kbList.map((kb) => {
                const isActive = kb.id === activeKbId;
                return (
                  <button
                    key={kb.id}
                    onClick={() => setActiveKbId(kb.id)}
                    className={`w-full text-left p-3.5 rounded-xl border transition-all flex flex-col gap-1.5 cursor-pointer ${
                      isActive
                        ? "border-primary bg-primary/5 text-primary shadow-sm"
                        : "border-border bg-background/20 text-muted-foreground hover:text-foreground"
                    }`}
                  >
                    <div className="flex justify-between items-center w-full">
                      <span className="text-xs font-bold text-foreground">{kb.name}</span>
                      <span className="text-[9px] px-2 py-0.5 rounded-xl bg-muted font-bold text-muted-foreground font-mono">
                        {kb.documentCount} docs
                      </span>
                    </div>
                    <p className="text-[10px] text-muted-foreground line-clamp-2 leading-relaxed">{kb.description}</p>
                  </button>
                );
              })}
            </div>
          </div>
        </div>

        {/* Documents repository main grid */}
        <div className="lg:col-span-3 space-y-6">
          <div className="rounded-2xl border border-border bg-card p-6 shadow-sm space-y-5">
            
            {/* Header filters */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
              <div className="space-y-1">
                <h3 className="text-lg font-bold">
                  {kbList.find((k) => k.id === activeKbId)?.name} Documents
                </h3>
                <p className="text-xs text-muted-foreground">
                  Ingested files supporting semantic prompt retrieval in the active base
                </p>
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                placeholder="Search documents or authors..."
                className="w-full sm:w-64 px-3 py-2 rounded-xl border border-border bg-background/50 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
              />
            </div>

            {/* Document list */}
            {filteredDocs.length === 0 ? (
              <div className="py-12 text-center rounded-xl border border-dashed border-border/80 bg-background/20 space-y-2">
                <p className="text-xs text-muted-foreground font-bold">No documents found in this Knowledge Base</p>
                <p className="text-[10px] text-muted-foreground/80 leading-normal">
                  Ingest files to build semantic chunk indexes for your AI employees
                </p>
              </div>
            ) : (
              <div className="overflow-hidden rounded-xl border border-border bg-background/30">
                <table className="w-full border-collapse text-left text-sm">
                  <thead>
                    <tr className="border-b border-border bg-muted/20">
                      <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px] w-2/5">File Title</th>
                      <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px]">Author</th>
                      <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px]">Chunks</th>
                      <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px]">Status</th>
                      <th className="p-3 font-bold text-muted-foreground uppercase tracking-wider text-[10px] text-right">Actions</th>
                    </tr>
                  </thead>
                  <tbody>
                    {filteredDocs.map((doc) => (
                      <tr key={doc.id} className="border-b border-border/40 last:border-0 text-xs">
                        <td className="p-3">
                          <div className="font-semibold text-foreground">{doc.title}</div>
                          <div className="flex items-center gap-1.5 mt-1">
                            <span className="text-[9px] text-muted-foreground font-mono">{(doc.sizeKb / 1024).toFixed(2)} MB</span>
                            {doc.tags.map((tag) => (
                              <span key={tag} className="text-[8px] px-1.5 py-0.2 bg-muted/70 text-muted-foreground rounded font-mono">
                                #{tag}
                              </span>
                            ))}
                          </div>
                        </td>
                        <td className="p-3 text-muted-foreground">{doc.author}</td>
                        <td className="p-3 font-mono font-semibold">{doc.chunksCount} splits</td>
                        <td className="p-3">
                          <span className={`text-[9px] font-extrabold px-2 py-0.5 rounded-xl ${
                            doc.status === "Ready"
                              ? "bg-green-500/10 text-green-500"
                              : doc.status === "Processing"
                              ? "bg-blue-500/10 text-blue-500 animate-pulse"
                              : doc.status === "Embedding"
                              ? "bg-purple-500/10 text-purple-500 animate-pulse"
                              : "bg-red-500/10 text-red-500"
                          }`}>
                            {doc.status}
                          </span>
                        </td>
                        <td className="p-3 text-right">
                          <button
                            onClick={() => handleDeleteDoc(doc.id, doc.kbId)}
                            className="text-[10px] text-red-500 hover:text-red-600 font-bold border border-red-500/20 hover:bg-red-500/5 px-2.5 py-1 rounded-lg transition-all cursor-pointer"
                          >
                            Delete
                          </button>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}

          </div>
        </div>

      </div>

      {/* Create KB Modal */}
      {showCreateKbModal && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
          <div className="bg-card border border-border rounded-3xl p-8 max-w-md w-full shadow-2xl space-y-6">
            <div className="text-center space-y-2">
              <h3 className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                CREATE KNOWLEDGE BASE
              </h3>
              <p className="text-sm text-muted-foreground font-semibold">
                Setup a logical container to ingestion patient data or policies
              </p>
            </div>

            <form onSubmit={handleCreateKb} className="space-y-4">
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">KB Name</label>
                <input
                  type="text"
                  required
                  value={newKbName}
                  onChange={(e) => setNewKbName(e.target.value)}
                  placeholder="e.g. Patient Onboarding Manuals"
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                />
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Category</label>
                <select
                  value={newKbCat}
                  onChange={(e) => setNewKbCat(e.target.value)}
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                >
                  <option value="Clinic">Clinic / Medicine</option>
                  <option value="School">School / Policies</option>
                  <option value="Operations">Operations / SOPs</option>
                  <option value="Sales">Sales / Products</option>
                </select>
              </div>

              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Description</label>
                <textarea
                  value={newKbDesc}
                  onChange={(e) => setNewKbDesc(e.target.value)}
                  placeholder="Guidelines detailing clinic checkin flowcharts..."
                  rows={3}
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all resize-none"
                />
              </div>

              <div className="flex gap-3 pt-2">
                <button
                  type="button"
                  onClick={() => setShowCreateKbModal(false)}
                  className="flex-1 py-2.5 border border-border text-foreground font-semibold text-xs rounded-xl hover:bg-muted transition-all cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-primary text-primary-foreground font-bold text-xs rounded-xl hover:bg-primary/90 transition-all cursor-pointer"
                >
                  Create Container
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Ingest File Modal */}
      {showUploadModal && (
        <div className="fixed inset-0 bg-background/80 backdrop-blur-sm flex items-center justify-center z-50 animate-in fade-in duration-200">
          <div className="bg-card border border-border rounded-3xl p-8 max-w-lg w-full shadow-2xl space-y-6 max-h-[85vh] overflow-y-auto">
            <div className="text-center space-y-2">
              <h3 className="text-2xl font-extrabold tracking-tight bg-gradient-to-r from-primary to-accent bg-clip-text text-transparent">
                INGEST UNSTRUCTURED DOCUMENT
              </h3>
              <p className="text-sm text-muted-foreground font-semibold">
                Upload files to extract text chunks and generate metadata nodes
              </p>
            </div>

            <form onSubmit={handleUploadDoc} className="space-y-4">
              <div className="space-y-1">
                <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Filename / Title</label>
                <input
                  type="text"
                  required
                  value={uploadFileName}
                  onChange={(e) => setUploadFileName(e.target.value)}
                  placeholder="e.g. employee_rules_2026.txt"
                  className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-sm focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Author / Publisher</label>
                  <input
                    type="text"
                    value={uploadAuthor}
                    onChange={(e) => setUploadAuthor(e.target.value)}
                    placeholder="Dr. Sarah"
                    className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Tags (comma-separated)</label>
                  <input
                    type="text"
                    value={uploadTags}
                    onChange={(e) => setUploadTags(e.target.value)}
                    placeholder="onboarding, staff"
                    className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4 border-t border-border/40 pt-4">
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Chunk Size (chars)</label>
                  <input
                    type="number"
                    value={chunkSize}
                    onChange={(e) => setChunkSize(parseInt(e.target.value) || 1000)}
                    className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all font-mono"
                  />
                </div>
                <div className="space-y-1">
                  <label className="text-[10px] font-bold text-muted-foreground uppercase tracking-wide">Chunk Overlap (chars)</label>
                  <input
                    type="number"
                    value={chunkOverlap}
                    onChange={(e) => setChunkOverlap(parseInt(e.target.value) || 200)}
                    className="w-full px-3 py-2 rounded-xl border border-border bg-background/50 text-xs focus:outline-none focus:ring-2 focus:ring-primary/30 transition-all font-mono"
                  />
                </div>
              </div>

              <div className="flex gap-3 pt-4">
                <button
                  type="button"
                  onClick={() => setShowUploadModal(false)}
                  className="flex-1 py-2.5 border border-border text-foreground font-semibold text-xs rounded-xl hover:bg-muted transition-all cursor-pointer"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="flex-1 py-2.5 bg-primary text-primary-foreground font-bold text-xs rounded-xl hover:bg-primary/90 transition-all cursor-pointer"
                >
                  Process & Splitting
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
