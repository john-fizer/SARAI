import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Upload, FileText, CheckCircle, AlertCircle } from "lucide-react";

const BACKEND = process.env.REACT_APP_BACKEND_URL;
const API_HEADERS = { "X-API-Key": process.env.REACT_APP_API_KEY || "" };

const BACKDROP_ANIM = { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 } };
const PANEL_ANIM = { initial: { opacity: 0, y: 20, scale: 0.97 }, animate: { opacity: 1, y: 0, scale: 1 }, exit: { opacity: 0, y: 10 } };

const SPLIT_OPTIONS = [
  { value: "paragraph", label: "Paragraph", desc: "Split on blank lines" },
  { value: "line",      label: "Line",      desc: "One thought per line" },
  { value: "sentence",  label: "Sentence",  desc: "Split on punctuation" },
];

const ImportModal = ({ onClose, onImported }) => {
  const [text, setText] = useState("");
  const [splitBy, setSplitBy] = useState("paragraph");
  const [status, setStatus] = useState(null); // null | "loading" | {imported, thoughts} | "error"

  const preview = () => {
    if (!text.trim()) return [];
    if (splitBy === "line") return text.split("\n").filter((l) => l.trim().length > 10).slice(0, 5);
    if (splitBy === "sentence") return text.split(/(?<=[.!?])\s+/).filter((s) => s.trim().length > 15).slice(0, 5);
    return text.split(/\n\s*\n/).filter((p) => p.trim().length > 10).slice(0, 5);
  };

  const handleImport = async () => {
    if (!text.trim() || status === "loading") return;
    setStatus("loading");
    try {
      const resp = await fetch(`${BACKEND}/api/import`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...API_HEADERS },
        body: JSON.stringify({ text, split_by: splitBy }),
      });
      if (resp.ok) {
        const data = await resp.json();
        setStatus(data);
        onImported?.();
      } else {
        setStatus("error");
      }
    } catch (_) {
      setStatus("error");
    }
  };

  const chunks = preview();
  const isDone = status && typeof status === "object";

  return (
    <AnimatePresence>
      <motion.div
        {...BACKDROP_ANIM}
        className="fixed inset-0 z-50 flex items-center justify-center p-6"
        style={{ background: "rgba(3, 3, 5, 0.88)", backdropFilter: "blur(8px)" }}
        onClick={(e) => e.target === e.currentTarget && onClose()}
        data-testid="import-modal"
      >
        <motion.div
          {...PANEL_ANIM}
          className="glass-panel rounded-2xl w-full max-w-lg flex flex-col"
          style={{ borderColor: "rgba(6, 182, 212, 0.3)" }}
        >
          {/* Header */}
          <div className="flex items-center justify-between px-5 py-4 border-b border-[#1E293B] shrink-0">
            <div className="flex items-center gap-2">
              <Upload size={16} color="#06B6D4" style={{ filter: "drop-shadow(0 0 6px #06B6D4)" }} />
              <h2 className="text-sm font-body font-semibold text-[#F8FAFC]">Bulk Import</h2>
            </div>
            <button onClick={onClose} className="text-[#475569] hover:text-[#F8FAFC] transition-colors" data-testid="close-import">
              <X size={16} />
            </button>
          </div>

          <div className="p-5 space-y-4">
            {isDone ? (
              <motion.div initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} className="text-center py-6">
                <CheckCircle size={40} color="#10B981" className="mx-auto mb-3" style={{ filter: "drop-shadow(0 0 10px #10B981)" }} />
                <p className="text-lg font-body font-semibold text-[#F8FAFC]">{status.imported} thoughts imported</p>
                <p className="text-[11px] font-body text-[#64748B] mt-1">Added to your knowledge graph</p>
                <button onClick={onClose} className="mt-4 px-4 py-2 rounded-lg text-xs font-body bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/30 hover:bg-[#10B981]/20 transition-all">
                  Done
                </button>
              </motion.div>
            ) : (
              <>
                {/* Split mode */}
                <div>
                  <div className="text-[10px] font-body text-[#64748B] tracking-widest uppercase mb-2">Split Mode</div>
                  <div className="flex gap-2">
                    {SPLIT_OPTIONS.map((opt) => (
                      <button
                        key={opt.value}
                        onClick={() => setSplitBy(opt.value)}
                        className={`flex-1 py-2 px-2 rounded-lg text-[10px] font-body border transition-all ${
                          splitBy === opt.value
                            ? "border-[#06B6D4]/50 text-[#06B6D4] bg-[#06B6D4]/10"
                            : "border-[#1E293B] text-[#475569] hover:border-[#334155]"
                        }`}
                      >
                        <div className="font-semibold">{opt.label}</div>
                        <div className="opacity-60 mt-0.5">{opt.desc}</div>
                      </button>
                    ))}
                  </div>
                </div>

                {/* Text input */}
                <div>
                  <div className="text-[10px] font-body text-[#64748B] tracking-widest uppercase mb-2 flex items-center gap-1">
                    <FileText size={10} />
                    <span>Paste your notes</span>
                  </div>
                  <textarea
                    value={text}
                    onChange={(e) => setText(e.target.value)}
                    placeholder="Paste markdown, notes, or any text here..."
                    rows={6}
                    className="w-full bg-[#0A0A0F] border border-[#1E293B] rounded-lg px-3 py-2 text-[11px] font-body text-[#94A3B8] placeholder-[#334155] outline-none focus:border-[#06B6D4]/40 transition-colors resize-none"
                    data-testid="import-textarea"
                  />
                  {text && (
                    <div className="text-[10px] font-body text-[#334155] mt-1">
                      ~{chunks.length}+ chunks detected (max 50 imported)
                    </div>
                  )}
                </div>

                {/* Preview */}
                {chunks.length > 0 && (
                  <div>
                    <div className="text-[10px] font-body text-[#64748B] tracking-widest uppercase mb-1.5">Preview</div>
                    <div className="space-y-1 max-h-28 overflow-y-auto scroll-cyber">
                      {chunks.map((c, i) => (
                        <div key={i} className="text-[10px] font-body text-[#475569] bg-[#0A0A0F] rounded px-2 py-1 truncate">
                          {i + 1}. {c.slice(0, 80)}{c.length > 80 ? "…" : ""}
                        </div>
                      ))}
                    </div>
                  </div>
                )}

                {status === "error" && (
                  <div className="flex items-center gap-2 text-[11px] font-body text-[#EF4444]">
                    <AlertCircle size={12} /> Import failed — check your connection and try again
                  </div>
                )}

                <button
                  onClick={handleImport}
                  disabled={!text.trim() || status === "loading"}
                  className="w-full py-2.5 rounded-lg text-xs font-body bg-[#06B6D4]/10 text-[#06B6D4] border border-[#06B6D4]/30 hover:bg-[#06B6D4]/20 disabled:opacity-30 transition-all flex items-center justify-center gap-2"
                  data-testid="import-btn"
                >
                  {status === "loading" ? (
                    <><motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: "linear" }}><Upload size={12} /></motion.div> Importing...</>
                  ) : (
                    <><Upload size={12} /> Import {chunks.length > 0 ? `~${Math.min(chunks.length, 50)} thoughts` : "thoughts"}</>
                  )}
                </button>
              </>
            )}
          </div>
        </motion.div>
      </motion.div>
    </AnimatePresence>
  );
};

export default ImportModal;
