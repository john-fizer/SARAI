import React from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, TrendingUp, Eye, GitMerge } from "lucide-react";

const BACKDROP_ANIM = { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 } };
const PANEL_ANIM = { initial: { opacity: 0, y: 20, scale: 0.97 }, animate: { opacity: 1, y: 0, scale: 1 }, exit: { opacity: 0, y: 10 } };

const PredictPanel = ({ result, thought, onClose }) => (
  <AnimatePresence>
    {result && (
      <motion.div {...BACKDROP_ANIM} className="fixed inset-0 z-50 flex items-center justify-center p-6" style={{ background: "rgba(3, 3, 5, 0.88)", backdropFilter: "blur(8px)" }} onClick={(e) => e.target === e.currentTarget && onClose()} data-testid="predict-panel">
        <motion.div {...PANEL_ANIM} className="glass-panel rounded-2xl w-full max-w-xl max-h-[85vh] overflow-hidden flex flex-col" style={{ borderColor: "rgba(245, 158, 11, 0.3)" }}>
          <div className="flex items-center justify-between px-5 py-4 border-b border-[#1E293B] shrink-0">
            <div className="flex items-center gap-2">
              <TrendingUp size={16} color="#F59E0B" style={{ filter: "drop-shadow(0 0 6px #F59E0B)" }} />
              <div>
                <h2 className="text-sm font-body font-semibold text-[#F8FAFC]">Predictive Model</h2>
                <p className="text-[10px] font-body text-[#475569] mt-0.5 truncate max-w-[340px]">{thought}</p>
              </div>
            </div>
            <button onClick={onClose} className="text-[#475569] hover:text-[#F8FAFC] transition-colors" data-testid="close-predict"><X size={16} /></button>
          </div>

          <div className="flex-1 overflow-y-auto scroll-cyber p-4 space-y-3">
            {result.trajectory && (
              <div className="glass-panel rounded-xl p-3 flex items-start gap-2" style={{ borderColor: "#F59E0B30" }}>
                <GitMerge size={14} color="#F59E0B" className="shrink-0 mt-0.5" />
                <div>
                  <div className="text-[9px] font-body uppercase tracking-widest text-[#F59E0B] mb-0.5">Trajectory</div>
                  <p className="text-[11px] font-body text-[#CBD5E1]">{result.trajectory}</p>
                </div>
              </div>
            )}

            <div className="space-y-2">
              {(result.predictions || []).map((p, i) => {
                const prob = Math.round((p.probability || 0) * 100);
                return (
                  <motion.div key={i} initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.08 }} className="glass-panel rounded-xl p-3" style={{ borderColor: "#F59E0B25" }} data-testid={`prediction-${i}`}>
                    <div className="flex items-start justify-between gap-2 mb-2">
                      <p className="text-xs font-body font-medium text-[#F8FAFC] leading-tight">{p.outcome}</p>
                      <span className="text-[10px] font-body shrink-0 text-[#F59E0B]">{p.timeframe}</span>
                    </div>
                    <div className="flex items-center gap-2 mb-2">
                      <div className="flex-1 h-1.5 rounded-full bg-[#1E293B] overflow-hidden">
                        <motion.div className="h-full rounded-full bg-[#F59E0B]" style={{ boxShadow: "0 0 6px #F59E0B" }} initial={{ width: 0 }} animate={{ width: `${prob}%` }} transition={{ duration: 0.8, delay: i * 0.08 + 0.3 }} />
                      </div>
                      <span className="text-[10px] font-body text-[#F59E0B] w-8 text-right">{prob}%</span>
                    </div>
                    {p.driving_force && <p className="text-[10px] font-body text-[#64748B]">↑ {p.driving_force}</p>}
                    {p.early_signal && <p className="text-[10px] font-body text-[#475569] mt-0.5">◉ Watch: {p.early_signal}</p>}
                  </motion.div>
                );
              })}
            </div>

            {(result.inflection_point || result.blind_spot) && (
              <div className="space-y-2">
                {result.inflection_point && (
                  <div className="glass-panel rounded-xl p-3" style={{ borderColor: "#8B5CF630" }}>
                    <div className="text-[9px] font-body uppercase tracking-widest text-[#8B5CF6] mb-1">Inflection Point</div>
                    <p className="text-[11px] font-body text-[#94A3B8]">{result.inflection_point}</p>
                  </div>
                )}
                {result.blind_spot && (
                  <div className="glass-panel rounded-xl p-3" style={{ borderColor: "#EF444430" }}>
                    <div className="flex items-center gap-1.5 mb-1"><Eye size={11} color="#EF4444" /><span className="text-[9px] font-body uppercase tracking-widest text-[#EF4444]">Blind Spot</span></div>
                    <p className="text-[11px] font-body text-[#94A3B8]">{result.blind_spot}</p>
                  </div>
                )}
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    )}
  </AnimatePresence>
);

export default PredictPanel;
