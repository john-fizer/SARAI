import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Brain, Target, Database, AlertTriangle, Heart, ChevronDown, ChevronUp } from "lucide-react";

const AGENT_ICONS = {
  analyst: Brain,
  strategist: Target,
  memory_curator: Database,
  skeptic: AlertTriangle,
  emotional: Heart,
};

const AGENTS = [
  { key: "analyst", name: "Analyst", color: "#06B6D4", desc: "Logic & contradiction" },
  { key: "strategist", name: "Strategist", color: "#3B82F6", desc: "Long-term planning" },
  { key: "memory_curator", name: "Memory Curator", color: "#10B981", desc: "Pattern recognition" },
  { key: "skeptic", name: "Skeptic", color: "#F59E0B", desc: "Adversarial analysis" },
  { key: "emotional", name: "Emotional", color: "#8B5CF6", desc: "Emotional context" },
];

const AgentChamber = ({ agentOutputs, isProcessing, activeAgent }) => {
  const [expanded, setExpanded] = useState(null);

  return (
    <div className="flex flex-col gap-2 h-full" data-testid="agent-chamber">
      {/* Header */}
      <div className="flex items-center gap-2 mb-1">
        <div
          className="w-2 h-2 rounded-full"
          style={{
            background: "#06B6D4",
            boxShadow: isProcessing ? "0 0 10px #06B6D4, 0 0 20px #06B6D4" : "0 0 6px #06B6D4",
          }}
        />
        <span className="text-xs font-body text-[#64748B] tracking-[0.2em] uppercase">Agent Chamber</span>
        {isProcessing && (
          <motion.span
            animate={{ opacity: [0.4, 1, 0.4] }}
            transition={{ duration: 1, repeat: Infinity }}
            className="text-[10px] font-body text-[#06B6D4] ml-auto"
          >
            ACTIVE
          </motion.span>
        )}
      </div>

      {/* Agents list */}
      <div className="flex flex-col gap-1.5 flex-1 overflow-y-auto scroll-cyber">
        {AGENTS.map((agent, i) => {
          const Icon = AGENT_ICONS[agent.key];
          const isActive = isProcessing && (activeAgent === agent.key || Math.floor(Date.now() / 800) % 5 === i);
          const hasOutput = agentOutputs?.[agent.key];
          const isExpanded = expanded === agent.key;

          return (
            <motion.div
              key={agent.key}
              initial={{ opacity: 0, x: -20 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: i * 0.08 }}
              data-testid={`agent-${agent.key}`}
              className={`relative rounded-lg p-2.5 cursor-pointer transition-all duration-300 ${
                hasOutput
                  ? "glass-panel hover:border-opacity-60"
                  : "bg-[#0A0A0F]/60 border border-[#1E293B]"
              }`}
              style={hasOutput ? { borderColor: agent.color + "40" } : {}}
              onClick={() => hasOutput && setExpanded(isExpanded ? null : agent.key)}
            >
              {/* Active pulse ring */}
              {isActive && (
                <motion.div
                  className="absolute inset-0 rounded-lg pointer-events-none"
                  animate={{ opacity: [0.3, 0.8, 0.3] }}
                  transition={{ duration: 1, repeat: Infinity }}
                  style={{ border: `1px solid ${agent.color}`, boxShadow: `0 0 10px ${agent.color}40` }}
                />
              )}

              <div className="flex items-center gap-2">
                {/* Activity indicator */}
                <div className="relative shrink-0">
                  <motion.div
                    animate={isActive ? { scale: [1, 1.2, 1], opacity: [0.7, 1, 0.7] } : {}}
                    transition={{ duration: 0.8, repeat: Infinity }}
                  >
                    <Icon
                      size={14}
                      style={{
                        color: hasOutput ? agent.color : "#334155",
                        filter: hasOutput ? `drop-shadow(0 0 4px ${agent.color})` : "none",
                      }}
                    />
                  </motion.div>
                </div>

                <div className="flex-1 min-w-0">
                  <div
                    className="text-xs font-body font-medium truncate"
                    style={{ color: hasOutput ? agent.color : "#475569" }}
                  >
                    {agent.name}
                  </div>
                  <div className="text-[10px] font-body text-[#334155] truncate">{agent.desc}</div>
                </div>

                {hasOutput && (
                  <div className="shrink-0">
                    {isExpanded ? (
                      <ChevronUp size={12} color="#64748B" />
                    ) : (
                      <ChevronDown size={12} color="#64748B" />
                    )}
                  </div>
                )}
              </div>

              {/* Output */}
              <AnimatePresence>
                {isExpanded && hasOutput && (
                  <motion.div
                    initial={{ opacity: 0, height: 0 }}
                    animate={{ opacity: 1, height: "auto" }}
                    exit={{ opacity: 0, height: 0 }}
                    className="mt-2 pt-2 border-t overflow-hidden"
                    style={{ borderColor: agent.color + "30" }}
                  >
                    <p className="text-[11px] font-body leading-relaxed" style={{ color: "#94A3B8" }}>
                      {agentOutputs[agent.key]?.output || agentOutputs[agent.key]}
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>

              {/* Loading state */}
              {isActive && !hasOutput && (
                <div className="mt-1.5">
                  <div className="shimmer h-0.5 rounded-full" />
                </div>
              )}
            </motion.div>
          );
        })}
      </div>

      {/* Synthesis display */}
      <AnimatePresence>
        {agentOutputs?.synthesis && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="glass-panel rounded-lg p-3 border-[#3B82F6]/30"
            data-testid="synthesis-output"
          >
            <div className="text-[10px] font-body text-[#3B82F6] tracking-widest uppercase mb-1.5">Synthesis</div>
            <p className="text-[11px] font-body text-[#94A3B8] leading-relaxed">{agentOutputs.synthesis}</p>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default AgentChamber;
