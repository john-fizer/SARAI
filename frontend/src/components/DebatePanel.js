import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, MessageSquare, ArrowRight } from "lucide-react";

const BACKDROP_ANIM = { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 } };
const PANEL_ANIM = { initial: { opacity: 0, y: 20, scale: 0.97 }, animate: { opacity: 1, y: 0, scale: 1 }, exit: { opacity: 0, y: 10 } };

const AgentDebateCard = ({ agentKey, entry, index }) => {
  const [expanded, setExpanded] = useState(true);

  return (
    <motion.div
      initial={{ opacity: 0, x: -16 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.07 }}
      className="glass-panel rounded-xl overflow-hidden"
      style={{ borderColor: entry.color + "30" }}
      data-testid={`debate-agent-${agentKey}`}
    >
      <button
        onClick={() => setExpanded((v) => !v)}
        className="w-full flex items-center gap-2.5 px-3 py-2.5 hover:bg-white/5 transition-colors"
      >
        <div className="w-2 h-2 rounded-full shrink-0" style={{ background: entry.color, boxShadow: `0 0 6px ${entry.color}` }} />
        <span className="text-xs font-body font-semibold" style={{ color: entry.color }}>{entry.name}</span>
        <ArrowRight size={10} color="#475569" className={`ml-auto transition-transform ${expanded ? "rotate-90" : ""}`} />
      </button>

      <AnimatePresence>
        {expanded && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            exit={{ opacity: 0, height: 0 }}
            className="overflow-hidden"
          >
            <div className="px-3 pb-3 space-y-2.5">
              {entry.position && (
                <div>
                  <div className="text-[9px] font-body tracking-widest uppercase text-[#475569] mb-1">Position</div>
                  <p className="text-[11px] font-body text-[#94A3B8] leading-relaxed">{entry.position}</p>
                </div>
              )}
              {entry.rebuttal && (
                <div style={{ borderTopColor: entry.color + "20" }} className="border-t pt-2">
                  <div className="text-[9px] font-body tracking-widest uppercase mb-1" style={{ color: entry.color }}>Rebuttal</div>
                  <p className="text-[11px] font-body text-[#CBD5E1] leading-relaxed italic">{entry.rebuttal}</p>
                </div>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const DebatePanel = ({ debate, thought, onClose }) => (
  <AnimatePresence>
    {debate && (
      <motion.div
        {...BACKDROP_ANIM}
        className="fixed inset-0 z-50 flex items-center justify-center p-6"
        style={{ background: "rgba(3, 3, 5, 0.88)", backdropFilter: "blur(8px)" }}
        onClick={(e) => e.target === e.currentTarget && onClose()}
        data-testid="debate-panel"
      >
        <motion.div
          {...PANEL_ANIM}
          className="glass-panel rounded-2xl w-full max-w-xl max-h-[85vh] overflow-hidden flex flex-col"
          style={{ borderColor: "rgba(59, 130, 246, 0.3)" }}
        >
          <div className="flex items-center justify-between px-5 py-4 border-b border-[#1E293B] shrink-0">
            <div className="flex items-center gap-2">
              <MessageSquare size={16} color="#3B82F6" style={{ filter: "drop-shadow(0 0 6px #3B82F6)" }} />
              <div>
                <h2 className="text-sm font-body font-semibold text-[#F8FAFC]">Agent Debate</h2>
                <p className="text-[10px] font-body text-[#475569] mt-0.5 truncate max-w-[340px]">{thought}</p>
              </div>
            </div>
            <button onClick={onClose} className="text-[#475569] hover:text-[#F8FAFC] transition-colors" data-testid="close-debate">
              <X size={16} />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto scroll-cyber p-4 space-y-2">
            {Object.entries(debate).map(([key, entry], i) => (
              <AgentDebateCard key={key} agentKey={key} entry={entry} index={i} />
            ))}
          </div>
        </motion.div>
      </motion.div>
    )}
  </AnimatePresence>
);

export default DebatePanel;
