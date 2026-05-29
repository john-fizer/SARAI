import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, GitBranch, Clock, TrendingUp } from "lucide-react";

const TIMEFRAME_COLORS = {
  "short-term": "#10B981",
  "medium-term": "#F59E0B",
  "long-term": "#8B5CF6",
};

const BACKDROP_ANIM = { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 } };
const PANEL_ANIM = { initial: { opacity: 0, y: 20, scale: 0.97 }, animate: { opacity: 1, y: 0, scale: 1 }, exit: { opacity: 0, y: 10 } };

const ScenarioCard = ({ scenario, index }) => {
  const prob = Math.round((scenario.probability || 0) * 100);
  const tfColor = TIMEFRAME_COLORS[scenario.timeframe] || "#06B6D4";

  return (
    <motion.div
      initial={{ opacity: 0, x: -20 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.1 }}
      className="glass-panel rounded-xl p-4"
      style={{ borderColor: tfColor + "30" }}
      data-testid={`scenario-${index}`}
    >
      <div className="flex items-start justify-between gap-3 mb-3">
        <h3 className="text-sm font-body font-semibold text-[#F8FAFC] leading-tight">{scenario.title}</h3>
        <span
          className="shrink-0 text-[9px] font-body uppercase tracking-widest px-2 py-0.5 rounded-full border"
          style={{ color: tfColor, borderColor: tfColor + "40", background: tfColor + "10" }}
        >
          {scenario.timeframe}
        </span>
      </div>

      <p className="text-[11px] font-body text-[#94A3B8] leading-relaxed mb-3">{scenario.description}</p>

      {scenario.key_driver && (
        <div className="flex items-center gap-1.5 mb-3">
          <TrendingUp size={10} color="#64748B" />
          <span className="text-[10px] font-body text-[#64748B]">Driver: </span>
          <span className="text-[10px] font-body text-[#CBD5E1]">{scenario.key_driver}</span>
        </div>
      )}

      <div className="flex items-center gap-2">
        <span className="text-[10px] font-body text-[#64748B]">Probability</span>
        <div className="flex-1 h-1.5 rounded-full bg-[#1E293B] overflow-hidden">
          <motion.div
            className="h-full rounded-full"
            style={{ background: tfColor, boxShadow: `0 0 6px ${tfColor}` }}
            initial={{ width: 0 }}
            animate={{ width: `${prob}%` }}
            transition={{ duration: 0.8, delay: index * 0.1 + 0.3, ease: "easeOut" }}
          />
        </div>
        <span className="text-[10px] font-body font-medium" style={{ color: tfColor }}>{prob}%</span>
      </div>
    </motion.div>
  );
};

const SimulationPanel = ({ scenarios, thought, onClose }) => (
  <AnimatePresence>
    {scenarios && (
      <motion.div
        {...BACKDROP_ANIM}
        className="fixed inset-0 z-50 flex items-center justify-center p-6"
        style={{ background: "rgba(3, 3, 5, 0.85)", backdropFilter: "blur(8px)" }}
        onClick={(e) => e.target === e.currentTarget && onClose()}
        data-testid="simulation-panel"
      >
        <motion.div
          {...PANEL_ANIM}
          className="glass-panel rounded-2xl w-full max-w-2xl max-h-[85vh] overflow-hidden flex flex-col"
          style={{ borderColor: "rgba(139, 92, 246, 0.3)" }}
        >
          <div className="flex items-center justify-between px-5 py-4 border-b border-[#1E293B]">
            <div className="flex items-center gap-2">
              <GitBranch size={16} color="#8B5CF6" style={{ filter: "drop-shadow(0 0 6px #8B5CF6)" }} />
              <div>
                <h2 className="text-sm font-body font-semibold text-[#F8FAFC] tracking-wide">Simulation Engine</h2>
                <p className="text-[10px] font-body text-[#475569] mt-0.5 truncate max-w-[400px]">{thought}</p>
              </div>
            </div>
            <button onClick={onClose} className="text-[#475569] hover:text-[#F8FAFC] transition-colors" data-testid="close-simulation">
              <X size={16} />
            </button>
          </div>

          <div className="flex-1 overflow-y-auto scroll-cyber p-5 space-y-3">
            <div className="flex items-center gap-1.5 mb-4">
              <Clock size={11} color="#64748B" />
              <span className="text-[10px] font-body text-[#64748B] tracking-widest uppercase">Projected Futures</span>
            </div>
            {scenarios.length === 0 ? (
              <p className="text-[11px] font-body text-[#334155] text-center py-8">No scenarios generated</p>
            ) : (
              scenarios.map((s, i) => <ScenarioCard key={i} scenario={s} index={i} />)
            )}
          </div>
        </motion.div>
      </motion.div>
    )}
  </AnimatePresence>
);

export default SimulationPanel;
