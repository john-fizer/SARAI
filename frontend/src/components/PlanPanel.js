import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Map, ChevronDown, ChevronUp, AlertTriangle, Zap } from "lucide-react";

const EFFORT_COLORS = { low: "#10B981", medium: "#F59E0B", high: "#EF4444" };
const TIME_COLORS = { immediate: "#06B6D4", "short-term": "#10B981", "long-term": "#8B5CF6" };

const BACKDROP_ANIM = { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 } };
const PANEL_ANIM = { initial: { opacity: 0, y: 20, scale: 0.97 }, animate: { opacity: 1, y: 0, scale: 1 }, exit: { opacity: 0, y: 10 } };

const StepCard = ({ step, index }) => {
  const [open, setOpen] = useState(index === 0);
  const effortColor = EFFORT_COLORS[step.effort] || "#06B6D4";
  const timeColor = TIME_COLORS[step.timeframe] || "#06B6D4";

  return (
    <motion.div
      initial={{ opacity: 0, x: -12 }}
      animate={{ opacity: 1, x: 0 }}
      transition={{ delay: index * 0.06 }}
      className="glass-panel rounded-xl overflow-hidden"
      style={{ borderColor: effortColor + "25" }}
      data-testid={`plan-step-${step.id}`}
    >
      <button onClick={() => setOpen((v) => !v)} className="w-full flex items-center gap-3 px-3 py-2.5 hover:bg-white/5 transition-colors">
        <div className="w-5 h-5 rounded-full border flex items-center justify-center shrink-0 text-[10px] font-body font-bold" style={{ borderColor: effortColor, color: effortColor }}>{step.id}</div>
        <span className="text-xs font-body text-[#F8FAFC] text-left flex-1 leading-tight">{step.action}</span>
        <div className="flex items-center gap-1.5 shrink-0">
          <span className="text-[9px] font-body px-1.5 py-0.5 rounded border" style={{ color: timeColor, borderColor: timeColor + "40", background: timeColor + "10" }}>{step.timeframe}</span>
          {open ? <ChevronUp size={11} color="#475569" /> : <ChevronDown size={11} color="#475569" />}
        </div>
      </button>
      <AnimatePresence>
        {open && (
          <motion.div initial={{ height: 0, opacity: 0 }} animate={{ height: "auto", opacity: 1 }} exit={{ height: 0, opacity: 0 }} className="overflow-hidden">
            <div className="px-3 pb-3 space-y-1.5">
              {step.success_metric && (
                <p className="text-[10px] font-body text-[#64748B]">✓ {step.success_metric}</p>
              )}
              {step.depends_on?.length > 0 && (
                <p className="text-[10px] font-body text-[#475569]">Depends on: steps {step.depends_on.join(", ")}</p>
              )}
              <div className="flex items-center gap-1">
                <span className="text-[9px] font-body uppercase tracking-widest" style={{ color: effortColor }}>effort: {step.effort}</span>
              </div>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </motion.div>
  );
};

const PlanPanel = ({ plan, thought, onClose }) => (
  <AnimatePresence>
    {plan && (
      <motion.div {...BACKDROP_ANIM} className="fixed inset-0 z-50 flex items-center justify-center p-6" style={{ background: "rgba(3, 3, 5, 0.88)", backdropFilter: "blur(8px)" }} onClick={(e) => e.target === e.currentTarget && onClose()} data-testid="plan-panel">
        <motion.div {...PANEL_ANIM} className="glass-panel rounded-2xl w-full max-w-xl max-h-[85vh] overflow-hidden flex flex-col" style={{ borderColor: "rgba(16, 185, 129, 0.3)" }}>
          <div className="flex items-center justify-between px-5 py-4 border-b border-[#1E293B] shrink-0">
            <div className="flex items-center gap-2">
              <Map size={16} color="#10B981" style={{ filter: "drop-shadow(0 0 6px #10B981)" }} />
              <div>
                <h2 className="text-sm font-body font-semibold text-[#F8FAFC]">Action Plan</h2>
                <p className="text-[10px] font-body text-[#475569] mt-0.5 truncate max-w-[340px]">{plan.goal || thought}</p>
              </div>
            </div>
            <button onClick={onClose} className="text-[#475569] hover:text-[#F8FAFC] transition-colors" data-testid="close-plan"><X size={16} /></button>
          </div>

          <div className="flex-1 overflow-y-auto scroll-cyber p-4 space-y-3">
            {plan.first_move && (
              <div className="glass-panel rounded-xl p-3 flex items-start gap-2" style={{ borderColor: "#10B98140" }}>
                <Zap size={14} color="#10B981" className="shrink-0 mt-0.5" />
                <div>
                  <div className="text-[9px] font-body uppercase tracking-widest text-[#10B981] mb-0.5">First Move</div>
                  <p className="text-[11px] font-body text-[#CBD5E1]">{plan.first_move}</p>
                </div>
              </div>
            )}

            <div className="space-y-2">
              {(plan.steps || []).map((step, i) => <StepCard key={step.id} step={step} index={i} />)}
            </div>

            {plan.risks?.length > 0 && (
              <div className="glass-panel rounded-xl p-3" style={{ borderColor: "#EF444430" }}>
                <div className="flex items-center gap-1.5 mb-2"><AlertTriangle size={11} color="#EF4444" /><span className="text-[9px] font-body uppercase tracking-widest text-[#EF4444]">Risks</span></div>
                {plan.risks.map((r, i) => <p key={i} className="text-[10px] font-body text-[#64748B] leading-relaxed">· {r}</p>)}
              </div>
            )}
          </div>
        </motion.div>
      </motion.div>
    )}
  </AnimatePresence>
);

export default PlanPanel;
