import React, { useState, useCallback, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Search, X, Zap } from "lucide-react";

const BACKEND = process.env.REACT_APP_BACKEND_URL;
const API_HEADERS = { "X-API-Key": process.env.REACT_APP_API_KEY || "" };

const TYPE_COLORS = { idea: "#06B6D4", question: "#8B5CF6", insight: "#F59E0B", memory: "#10B981" };

const RESULTS_ANIM = {
  initial: { opacity: 0, y: -8, scale: 0.97 },
  animate: { opacity: 1, y: 0, scale: 1 },
  exit: { opacity: 0, y: -4 },
};

const SearchBar = ({ onSelectNode, nodes }) => {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);
  const [open, setOpen] = useState(false);
  const debounceRef = useRef(null);
  const inputRef = useRef(null);

  const search = useCallback(async (q) => {
    if (!q.trim()) { setResults([]); setOpen(false); return; }
    setLoading(true);
    try {
      const resp = await fetch(
        `${BACKEND}/api/search?q=${encodeURIComponent(q)}&limit=8`,
        { headers: API_HEADERS }
      );
      if (resp.ok) {
        const data = await resp.json();
        setResults(data.results || []);
        setOpen(true);
      }
    } catch (_) {
      // fallback: filter local nodes
      const lo = q.toLowerCase();
      const local = nodes
        .filter((n) => n.content?.toLowerCase().includes(lo) || (n.concepts || []).some((c) => c.toLowerCase().includes(lo)))
        .slice(0, 8)
        .map((n) => ({ id: n.id, content: n.content, type: n.type, summary: n.summary, score: 1, match_type: "local" }));
      setResults(local);
      setOpen(local.length > 0);
    } finally {
      setLoading(false);
    }
  }, [nodes]);

  const handleChange = (e) => {
    const val = e.target.value;
    setQuery(val);
    clearTimeout(debounceRef.current);
    debounceRef.current = setTimeout(() => search(val), 300);
  };

  const handleSelect = (result) => {
    const node = nodes.find((n) => n.id === result.id);
    if (node) onSelectNode(node);
    setQuery("");
    setResults([]);
    setOpen(false);
  };

  const handleClear = () => { setQuery(""); setResults([]); setOpen(false); inputRef.current?.focus(); };

  // Close on outside click
  const containerRef = useRef(null);
  useEffect(() => {
    const handler = (e) => { if (!containerRef.current?.contains(e.target)) setOpen(false); };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  return (
    <div ref={containerRef} className="relative" data-testid="search-bar">
      <div className={`flex items-center gap-2 px-3 py-1.5 rounded-lg border transition-all duration-200 ${
        open ? "border-[#06B6D4]/50 bg-[#06B6D4]/5" : "border-[#1E293B] bg-[#0A0A0F]/80"
      }`}>
        {loading
          ? <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: "linear" }}><Zap size={12} color="#06B6D4" /></motion.div>
          : <Search size={12} color={open ? "#06B6D4" : "#334155"} />
        }
        <input
          ref={inputRef}
          value={query}
          onChange={handleChange}
          onFocus={() => results.length > 0 && setOpen(true)}
          placeholder="Search thoughts..."
          className="bg-transparent text-[11px] font-body text-[#F8FAFC] placeholder-[#334155] outline-none w-36 focus:w-48 transition-all duration-300"
          data-testid="search-input"
        />
        {query && (
          <button onClick={handleClear} className="text-[#334155] hover:text-[#64748B]" data-testid="search-clear">
            <X size={11} />
          </button>
        )}
      </div>

      <AnimatePresence>
        {open && results.length > 0 && (
          <motion.div
            {...RESULTS_ANIM}
            className="absolute right-0 top-full mt-1 w-72 glass-panel rounded-xl overflow-hidden z-50"
            style={{ borderColor: "rgba(6, 182, 212, 0.2)" }}
            data-testid="search-results"
          >
            {results.map((r, i) => {
              const color = TYPE_COLORS[r.type] || "#06B6D4";
              return (
                <button
                  key={r.id}
                  onClick={() => handleSelect(r)}
                  className="w-full text-left px-3 py-2.5 hover:bg-[#06B6D4]/8 transition-colors border-b border-[#1E293B]/50 last:border-0"
                  data-testid={`search-result-${i}`}
                >
                  <div className="flex items-center gap-2 mb-0.5">
                    <div className="w-1.5 h-1.5 rounded-full shrink-0" style={{ background: color }} />
                    <span className="text-[11px] font-body text-[#F8FAFC] truncate">{r.summary || r.content?.slice(0, 60)}</span>
                  </div>
                  <div className="flex items-center gap-2 ml-3.5">
                    <span className="text-[9px] font-body uppercase tracking-widest" style={{ color }}>{r.type}</span>
                    <span className="text-[9px] font-body text-[#334155]">{r.match_type}</span>
                    {(r.concepts || []).slice(0, 2).map((c) => (
                      <span key={c} className="text-[9px] font-body text-[#475569]">#{c}</span>
                    ))}
                  </div>
                </button>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default SearchBar;
