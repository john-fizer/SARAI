import React, { useMemo } from "react";
import { motion } from "framer-motion";
import { AlertOctagon, TrendingUp, Eye, Activity, Sparkles } from "lucide-react";

const Section = ({ icon, title, color, children }) => (
  <div className="mb-4">
    <div className="flex items-center gap-1.5 mb-2">
      <span style={{ color }}>{icon}</span>
      <span className="text-[10px] font-body tracking-widest uppercase" style={{ color }}>{title}</span>
    </div>
    {children}
  </div>
);

const Tag = ({ label, color, count }) => (
  <div
    className="inline-flex items-center gap-1 px-2 py-0.5 rounded border text-[10px] font-body mr-1 mb-1"
    style={{ borderColor: color + "40", color, background: color + "10" }}
  >
    {label}{count > 1 && <span className="opacity-60">×{count}</span>}
  </div>
);

const RecursiveDashboard = ({ nodes, stats, onImprove, isImproving, improveResult }) => {
  const analysis = useMemo(() => {
    if (!nodes?.length) return null;

    // Concept frequency map
    const conceptCount = {};
    nodes.forEach((n) => {
      (n.concepts || []).forEach((c) => {
        conceptCount[c] = (conceptCount[c] || 0) + 1;
      });
    });

    // Recurring patterns — top 8 concepts appearing 2+ times
    const patterns = Object.entries(conceptCount)
      .filter(([, count]) => count >= 2)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8);

    // Blind spots — concepts appearing exactly once
    const blindSpots = Object.entries(conceptCount)
      .filter(([, count]) => count === 1)
      .map(([c]) => c)
      .slice(0, 10);

    // Contradictions — high-emotion nodes sharing concepts with low-emotion nodes
    const highEmotion = nodes.filter((n) => (n.emotional_weight || 0) > 0.7);
    const lowEmotion = nodes.filter((n) => (n.emotional_weight || 0) < 0.3);
    const contradictions = [];
    highEmotion.forEach((h) => {
      const hSet = new Set(h.concepts || []);
      lowEmotion.forEach((l) => {
        const shared = (l.concepts || []).filter((c) => hSet.has(c));
        if (shared.length > 0 && contradictions.length < 4) {
          contradictions.push({
            a: h.summary || h.content?.slice(0, 40),
            b: l.summary || l.content?.slice(0, 40),
            shared,
          });
        }
      });
    });

    return { patterns, blindSpots, contradictions };
  }, [nodes]);

  const coherence = stats?.brain_coherence || 0;
  const coherenceColor = coherence > 70 ? "#10B981" : coherence > 40 ? "#F59E0B" : "#06B6D4";

  return (
    <div className="h-full overflow-y-auto scroll-cyber pr-1" data-testid="recursive-dashboard">

      {/* Brain Health */}
      <Section icon={<Activity size={11} />} title="Brain Health" color={coherenceColor}>
        <div className="glass-panel rounded-lg p-2.5" style={{ borderColor: coherenceColor + "30" }}>
          <div className="flex justify-between items-center mb-1.5">
            <span className="text-[10px] font-body text-[#64748B]">Coherence</span>
            <span className="text-xs font-body font-medium" style={{ color: coherenceColor }}>{coherence}%</span>
          </div>
          <div className="h-1.5 rounded-full bg-[#1E293B] overflow-hidden">
            <motion.div
              className="h-full rounded-full"
              style={{ background: coherenceColor, boxShadow: `0 0 6px ${coherenceColor}` }}
              initial={{ width: 0 }}
              animate={{ width: `${Math.min(coherence, 100)}%` }}
              transition={{ duration: 1, ease: "easeOut" }}
            />
          </div>
          <div className="flex justify-between mt-1.5 text-[9px] font-body text-[#334155]">
            <span>{stats?.total_thoughts || 0} nodes</span>
            <span>{stats?.total_connections || 0} synapses</span>
          </div>
        </div>
      </Section>

      {/* Self-Improvement */}
      <Section icon={<Sparkles size={11} />} title="Self-Improve" color="#8B5CF6">
        <motion.button
          whileHover={{ scale: 1.02 }}
          whileTap={{ scale: 0.98 }}
          onClick={onImprove}
          disabled={isImproving || !onImprove}
          className={`w-full py-2 rounded-lg text-[10px] font-body tracking-widest uppercase transition-all duration-200 ${
            isImproving
              ? "bg-[#1E293B] text-[#475569]"
              : "bg-[#8B5CF6]/10 text-[#8B5CF6] border border-[#8B5CF6]/30 hover:bg-[#8B5CF6]/20"
          }`}
          data-testid="self-improve-btn"
        >
          {isImproving ? "Analyzing..." : "Run Self-Analysis"}
        </motion.button>
        {improveResult?.recommendation && (
          <motion.div initial={{ opacity: 0, y: 4 }} animate={{ opacity: 1, y: 0 }} className="mt-2 glass-panel rounded-lg p-2.5" style={{ borderColor: "#8B5CF630" }}>
            <div className="text-[9px] font-body text-[#8B5CF6] uppercase tracking-widest mb-1">Recommendation</div>
            <p className="text-[10px] font-body text-[#94A3B8] leading-relaxed">{improveResult.recommendation}</p>
            {improveResult.cognitive_health && (
              <p className="text-[9px] font-body text-[#64748B] mt-1 italic">{improveResult.cognitive_health}</p>
            )}
          </motion.div>
        )}
      </Section>

      {!analysis ? (
        <p className="text-[11px] font-body text-[#334155] text-center mt-8">
          Add thoughts to activate analysis
        </p>
      ) : (
        <>
          {/* Contradictions */}
          <Section icon={<AlertOctagon size={11} />} title="Contradictions" color="#EF4444">
            {analysis.contradictions.length === 0 ? (
              <p className="text-[10px] font-body text-[#334155]">No contradictions detected</p>
            ) : (
              analysis.contradictions.map((c, i) => (
                <div key={i} className="glass-panel rounded-lg p-2 mb-1.5" style={{ borderColor: "#EF444430" }}>
                  <p className="text-[10px] font-body text-[#94A3B8] leading-relaxed">
                    <span className="text-[#EF4444]">↑</span> {c.a}
                  </p>
                  <p className="text-[10px] font-body text-[#94A3B8] leading-relaxed">
                    <span className="text-[#06B6D4]">↓</span> {c.b}
                  </p>
                  <div className="flex flex-wrap mt-1">
                    {c.shared.map((s) => <Tag key={s} label={s} color="#EF4444" count={1} />)}
                  </div>
                </div>
              ))
            )}
          </Section>

          {/* Recurring Patterns */}
          <Section icon={<TrendingUp size={11} />} title="Recurring Patterns" color="#3B82F6">
            {analysis.patterns.length === 0 ? (
              <p className="text-[10px] font-body text-[#334155]">No patterns yet</p>
            ) : (
              <div className="flex flex-wrap">
                {analysis.patterns.map(([concept, count]) => (
                  <Tag key={concept} label={concept} color="#3B82F6" count={count} />
                ))}
              </div>
            )}
          </Section>

          {/* Blind Spots */}
          <Section icon={<Eye size={11} />} title="Blind Spots" color="#8B5CF6">
            {analysis.blindSpots.length === 0 ? (
              <p className="text-[10px] font-body text-[#334155]">No blind spots</p>
            ) : (
              <div className="flex flex-wrap">
                {analysis.blindSpots.map((c) => (
                  <Tag key={c} label={c} color="#8B5CF6" count={1} />
                ))}
              </div>
            )}
          </Section>
        </>
      )}
    </div>
  );
};

export default RecursiveDashboard;
