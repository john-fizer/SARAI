import React, { useRef } from "react";
import { motion } from "framer-motion";
import { Clock } from "lucide-react";

const TYPE_COLORS = {
  idea: "#06B6D4",
  question: "#8B5CF6",
  insight: "#F59E0B",
  memory: "#10B981",
};

const CognitiveTimeline = ({ entries, onSelect, selectedId }) => {
  const scrollRef = useRef(null);

  if (!entries || entries.length === 0) {
    return (
      <div className="flex items-center gap-2 text-[#334155] text-xs font-body py-2" data-testid="timeline-empty">
        <Clock size={12} />
        <span className="tracking-widest uppercase">Timeline initializing...</span>
      </div>
    );
  }

  const formatTime = (iso) => {
    const d = new Date(iso);
    return d.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
  };

  return (
    <div className="flex flex-col gap-1" data-testid="cognitive-timeline">
      {/* Header */}
      <div className="flex items-center gap-2 mb-1">
        <Clock size={10} color="#64748B" />
        <span className="text-[10px] font-body text-[#64748B] tracking-[0.2em] uppercase">Cognitive Timeline</span>
        <span className="text-[10px] font-body text-[#334155] ml-auto">{entries.length} nodes</span>
      </div>

      {/* Horizontal scrollable timeline */}
      <div
        ref={scrollRef}
        className="flex gap-2 overflow-x-auto scroll-cyber pb-1"
        style={{ scrollbarHeight: "thin" }}
        data-testid="timeline-scroll"
      >
        {entries.map((entry, i) => {
          const color = TYPE_COLORS[entry.type] || "#06B6D4";
          const isSelected = entry.id === selectedId;

          return (
            <motion.div
              key={entry.id}
              initial={{ opacity: 0, scale: 0.8 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ delay: i * 0.03 }}
              onClick={() => onSelect && onSelect(entry)}
              data-testid={`timeline-entry-${entry.id}`}
              className={`shrink-0 cursor-pointer rounded-lg p-2 transition-all duration-200 ${
                isSelected ? "glass-panel-active" : "glass-panel hover:border-opacity-50"
              }`}
              style={{
                width: "120px",
                borderColor: isSelected ? color : color + "25",
                boxShadow: isSelected ? `0 0 12px ${color}40` : "none",
              }}
            >
              {/* Time dot */}
              <div className="flex items-center gap-1.5 mb-1.5">
                <div
                  className="w-1.5 h-1.5 rounded-full shrink-0"
                  style={{ background: color, boxShadow: `0 0 4px ${color}` }}
                />
                <span className="text-[9px] font-body" style={{ color: "#475569" }}>
                  {formatTime(entry.created_at)}
                </span>
              </div>

              {/* Content */}
              <p
                className="text-[10px] font-body leading-tight"
                style={{ color: isSelected ? "#F8FAFC" : "#94A3B8" }}
              >
                {entry.summary || entry.content?.substring(0, 40)}
                {(entry.content?.length || 0) > 40 ? "..." : ""}
              </p>

              {/* Type badge */}
              <div
                className="mt-1.5 text-[9px] font-body tracking-wider uppercase"
                style={{ color: color + "CC" }}
              >
                {entry.type}
              </div>
            </motion.div>
          );
        })}
      </div>
    </div>
  );
};

export default CognitiveTimeline;
