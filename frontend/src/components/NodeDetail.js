import React, { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { X, Zap, Brain, MessageSquare, Trash2, Link2, Users, GitBranch, Swords, Map, TrendingUp, Route, Pencil, Check } from "lucide-react";
import DebatePanel from "./DebatePanel";

const BACKEND = process.env.REACT_APP_BACKEND_URL;
const API_HEADERS = { "X-API-Key": process.env.REACT_APP_API_KEY || "" };
const devLog = (msg, err) => { if (process.env.NODE_ENV === "development") console.error(msg, err); };

const TYPE_COLORS = {
  idea: "#06B6D4",
  question: "#8B5CF6",
  insight: "#F59E0B",
  memory: "#10B981",
};

// Module-level agent color map — stable, no re-creation on render
const AGENT_COLORS = {
  analyst: "#06B6D4",
  strategist: "#3B82F6",
  memory_curator: "#10B981",
  skeptic: "#F59E0B",
  emotional: "#8B5CF6",
  identity_stabilizer: "#EC4899",
  execution: "#F97316",
};

// Stable animation configs
const PANEL_ANIM = { initial: { opacity: 0, x: 30 }, animate: { opacity: 1, x: 0 }, exit: { opacity: 0, x: 30 } };
const AGENTS_ANIM = { initial: { opacity: 0, height: 0 }, animate: { opacity: 1, height: "auto" } };
const ANALYZE_HOVER = { scale: 1.02 };
const ANALYZE_TAP = { scale: 0.98 };

// Unique message ID generator
let msgCounter = 0;
const makeId = () => `msg-${Date.now()}-${++msgCounter}`;

const NodeDetail = ({ node, onClose, onAnalyze, isAnalyzing, agentOutputs, onDelete, graphLinks, onSimulate, onPlan, onPredict, onFindPath, allNodes, onUpdate }) => {
  const [chatMsg, setChatMsg] = useState("");
  const [chatHistory, setChatHistory] = useState([]);
  const [chatLoading, setChatLoading] = useState(false);
  const [sessionId] = useState(`node-chat-${node.id}`);
  const [isEditing, setIsEditing] = useState(false);
  const [editContent, setEditContent] = useState(node.content);
  const [editType, setEditType] = useState(node.type);
  const [consensusResult, setConsensusResult] = useState(null);
  const [isConsensus, setIsConsensus] = useState(false);
  const [debateResult, setDebateResult] = useState(null);
  const [isDebating, setIsDebating] = useState(false);
  const [pathTarget, setPathTarget] = useState("");
  const [pathResult, setPathResult] = useState(null);
  const [isFindingPath, setIsFindingPath] = useState(false);

  useEffect(() => {
    const loadChat = async () => {
      try {
        const resp = await fetch(`${BACKEND}/api/thoughts/${node.id}/chat`, { headers: API_HEADERS });
        if (resp.ok) {
          const data = await resp.json();
          setChatHistory((data.messages || []).map((m) => ({ ...m, id: makeId() })));
        }
      } catch (err) {
        devLog("loadChat error:", err);
      }
    };
    loadChat();
  }, [node.id]);

  const saveEdit = async () => {
    if (!editContent.trim()) return;
    try {
      const resp = await fetch(`${BACKEND}/api/thoughts/${node.id}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json", ...API_HEADERS },
        body: JSON.stringify({ content: editContent, type: editType }),
      });
      if (resp.ok) {
        const data = await resp.json();
        setIsEditing(false);
        if (onUpdate) onUpdate({ ...node, content: editContent, type: editType, concepts: data.concepts || node.concepts });
      }
    } catch (err) {
      devLog("saveEdit error:", err);
    }
  };

  const color = TYPE_COLORS[isEditing ? editType : node.type] || "#06B6D4";

  const connectionCount = graphLinks?.filter(
    (l) => l.source === node.id || l.target === node.id ||
           l.source?.id === node.id || l.target?.id === node.id
  ).length || 0;

  const sendChat = async () => {
    if (!chatMsg.trim() || chatLoading) return;
    const msg = chatMsg.trim();
    setChatMsg("");
    setChatHistory((prev) => [...prev, { role: "user", text: msg, id: makeId() }]);
    setChatLoading(true);
    try {
      const resp = await fetch(`${BACKEND}/api/chat`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...API_HEADERS },
        body: JSON.stringify({ message: msg, session_id: sessionId, node_id: node.id }),
      });
      if (resp.ok) {
        const data = await resp.json();
        setChatHistory((prev) => [
          ...prev,
          { role: "sarai", text: data.response, model: data.model_used, agent: data.agent, id: makeId() },
        ]);
        // Persist both turns
        const saveMsg = async (role, text, model, agent) => {
          try {
            await fetch(`${BACKEND}/api/thoughts/${node.id}/chat`, {
              method: "POST",
              headers: { "Content-Type": "application/json", ...API_HEADERS },
              body: JSON.stringify({ role, text, model: model || null, agent: agent || null }),
            });
          } catch (e) { devLog("persist chat error:", e); }
        };
        await saveMsg("user", msg, null, null);
        await saveMsg("sarai", data.response, data.model_used, data.agent);
      }
    } catch (err) {
      devLog("sendChat error:", err);
    } finally {
      setChatLoading(false);
    }
  };

  const runConsensus = async () => {
    if (isConsensus) return;
    setIsConsensus(true);
    setConsensusResult(null);
    try {
      const resp = await fetch(`${BACKEND}/api/agents/consensus`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...API_HEADERS },
        body: JSON.stringify({ content: node.content }),
      });
      if (resp.ok) {
        const data = await resp.json();
        setConsensusResult(data.consensus);
      }
    } catch (err) {
      devLog("consensus error:", err);
    } finally {
      setIsConsensus(false);
    }
  };

  const runDebate = async () => {
    if (isDebating) return;
    setIsDebating(true);
    setDebateResult(null);
    try {
      const resp = await fetch(`${BACKEND}/api/agents/debate`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...API_HEADERS },
        body: JSON.stringify({ content: node.content }),
      });
      if (resp.ok) {
        const data = await resp.json();
        setDebateResult(data);
      }
    } catch (err) {
      devLog("debate error:", err);
    } finally {
      setIsDebating(false);
    }
  };

  const findPath = async () => {
    if (!pathTarget || isFindingPath) return;
    setIsFindingPath(true);
    setPathResult(null);
    try {
      const resp = await fetch(
        `${BACKEND}/api/graph/path?from_id=${node.id}&to_id=${pathTarget}`,
        { headers: API_HEADERS }
      );
      if (resp.ok) {
        const data = await resp.json();
        setPathResult(data);
        if (data.found && onFindPath) onFindPath(data.path.map((h) => h.id));
      }
    } catch (err) {
      devLog("findPath error:", err);
    } finally {
      setIsFindingPath(false);
    }
  };

  return (
    <motion.div {...PANEL_ANIM} className="flex flex-col h-full gap-3" data-testid="node-detail-panel">
      {/* Header */}
      <div className="glass-panel rounded-xl p-3 relative" style={{ borderColor: color + "40" }} data-testid="node-detail-header">
        <button onClick={onClose} className="absolute top-2 right-2 text-[#475569] hover:text-[#F8FAFC] transition-colors" data-testid="close-node-detail">
          <X size={14} />
        </button>

        <div
          className="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-[10px] font-body mb-2 uppercase tracking-widest"
          style={{ background: color + "15", color, border: `1px solid ${color}30` }}
        >
          <div className="w-1 h-1 rounded-full" style={{ background: color }} />
          {isEditing ? editType : node.type}
        </div>

        {isEditing ? (
          <div className="pr-4">
            <textarea
              value={editContent}
              onChange={(e) => setEditContent(e.target.value)}
              rows={3}
              autoFocus
              className="w-full bg-[#0A0A0F] border border-[#06B6D4]/40 rounded-lg px-2 py-1.5 text-sm font-body text-[#F8FAFC] outline-none resize-none focus:border-[#06B6D4]/70 transition-colors"
              data-testid="edit-node-textarea"
            />
            <div className="flex gap-1 mt-1.5 flex-wrap">
              {["idea", "question", "insight", "memory"].map((t) => (
                <button
                  key={t}
                  onClick={() => setEditType(t)}
                  className={`px-2 py-0.5 rounded text-[10px] font-body border transition-all ${
                    editType === t
                      ? "bg-[#06B6D4]/20 text-[#06B6D4] border-[#06B6D4]/40"
                      : "text-[#475569] border-[#1E293B] hover:text-[#94A3B8]"
                  }`}
                >{t}</button>
              ))}
            </div>
          </div>
        ) : (
          <p className="text-sm font-body text-[#F8FAFC] leading-relaxed pr-4">{node.content}</p>
        )}

        <div className="flex items-center gap-3 mt-2">
          <div className="flex items-center gap-1 text-[10px] font-body text-[#475569]">
            <Link2 size={10} />
            <span>{connectionCount} links</span>
          </div>
          {node.model_used && !isEditing && (
            <div className="text-[10px] font-body text-[#334155] truncate">
              via {node.model_used?.split("/")[1] || node.model_used}
            </div>
          )}
          {isEditing ? (
            <div className="ml-auto flex gap-1.5">
              <button onClick={saveEdit} className="text-[#10B981] hover:text-[#34D399] transition-colors" data-testid="save-edit-btn">
                <Check size={12} />
              </button>
              <button onClick={() => { setIsEditing(false); setEditContent(node.content); setEditType(node.type); }} className="text-[#475569] hover:text-[#94A3B8] transition-colors" data-testid="cancel-edit-btn">
                <X size={12} />
              </button>
            </div>
          ) : (
            <div className="ml-auto flex gap-2">
              <button onClick={() => { setIsEditing(true); setEditContent(node.content); setEditType(node.type); }} className="text-[#334155] hover:text-[#06B6D4] transition-colors" data-testid="edit-node-btn">
                <Pencil size={11} />
              </button>
              <button onClick={() => onDelete(node.id)} className="text-[#334155] hover:text-red-400 transition-colors" data-testid="delete-node-btn">
                <Trash2 size={11} />
              </button>
            </div>
          )}
        </div>
      </div>

      {/* Reflection */}
      {node.reflection?.evaluation && (
        <div className="glass-panel rounded-xl p-3" style={{ borderColor: "#8B5CF640" }} data-testid="node-reflection">
          <div className="text-[10px] font-body text-[#8B5CF6] tracking-widest uppercase mb-2">Reflection</div>
          {node.reflection.confidence !== undefined && (
            <div className="flex items-center gap-2 mb-2">
              <span className="text-[10px] font-body text-[#64748B]">Confidence</span>
              <div className="flex-1 h-1 rounded-full bg-[#1E293B] overflow-hidden">
                <div
                  className="h-full rounded-full"
                  style={{
                    width: `${Math.round((node.reflection.confidence || 0) * 100)}%`,
                    background: node.reflection.confidence > 0.7 ? "#10B981" : node.reflection.confidence > 0.4 ? "#F59E0B" : "#EF4444",
                  }}
                />
              </div>
              <span className="text-[10px] font-body text-[#94A3B8]">{Math.round((node.reflection.confidence || 0) * 100)}%</span>
            </div>
          )}
          {node.reflection.contradictions?.length > 0 && (
            <div className="mb-2">
              <div className="text-[9px] font-body text-[#EF4444] uppercase tracking-widest mb-1">Contradictions</div>
              {node.reflection.contradictions.slice(0, 2).map((c, i) => (
                <p key={i} className="text-[10px] font-body text-[#64748B] leading-relaxed">· {c}</p>
              ))}
            </div>
          )}
          {node.reflection.revision && (
            <p className="text-[11px] font-body text-[#94A3B8] leading-relaxed italic">"{node.reflection.revision}"</p>
          )}
        </div>
      )}

      {/* Concepts */}
      {node.concepts?.length > 0 && (
        <div className="flex flex-wrap gap-1" data-testid="node-concepts">
          {node.concepts.map((c) => (
            <span key={c} className="px-2 py-0.5 rounded text-[10px] font-body" style={{ background: color + "15", color, border: `1px solid ${color}25` }}>
              {c}
            </span>
          ))}
        </div>
      )}

      {/* Agent analysis + consensus + simulate buttons */}
      <div className="flex gap-1.5">
        <motion.button
          whileHover={ANALYZE_HOVER}
          whileTap={ANALYZE_TAP}
          onClick={() => onAnalyze(node)}
          disabled={isAnalyzing}
          data-testid="analyze-node-btn"
          className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-body transition-all duration-200 ${
            isAnalyzing
              ? "bg-[#1E293B] text-[#475569]"
              : "bg-[#06B6D4]/10 text-[#06B6D4] border border-[#06B6D4]/30 hover:bg-[#06B6D4]/20"
          }`}
        >
          <Brain size={11} className={isAnalyzing ? "animate-spin" : ""} />
          {isAnalyzing ? "Thinking..." : "Analyze"}
        </motion.button>
        <motion.button
          whileHover={ANALYZE_HOVER}
          whileTap={ANALYZE_TAP}
          onClick={runConsensus}
          disabled={isConsensus}
          data-testid="consensus-node-btn"
          className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-body transition-all duration-200 ${
            isConsensus
              ? "bg-[#1E293B] text-[#475569]"
              : "bg-[#3B82F6]/10 text-[#3B82F6] border border-[#3B82F6]/30 hover:bg-[#3B82F6]/20"
          }`}
        >
          <Users size={11} className={isConsensus ? "animate-spin" : ""} />
          {isConsensus ? "..." : "Consensus"}
        </motion.button>
        <motion.button
          whileHover={ANALYZE_HOVER}
          whileTap={ANALYZE_TAP}
          onClick={() => onSimulate && onSimulate(node)}
          data-testid="simulate-node-btn"
          className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-body bg-[#8B5CF6]/10 text-[#8B5CF6] border border-[#8B5CF6]/30 hover:bg-[#8B5CF6]/20 transition-all duration-200"
        >
          <GitBranch size={11} />
          Simulate
        </motion.button>
        <motion.button
          whileHover={ANALYZE_HOVER}
          whileTap={ANALYZE_TAP}
          onClick={runDebate}
          disabled={isDebating}
          data-testid="debate-node-btn"
          className={`flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-body transition-all duration-200 ${
            isDebating
              ? "bg-[#1E293B] text-[#475569]"
              : "bg-[#EF4444]/10 text-[#EF4444] border border-[#EF4444]/30 hover:bg-[#EF4444]/20"
          }`}
        >
          <Swords size={11} className={isDebating ? "animate-spin" : ""} />
          {isDebating ? "..." : "Debate"}
        </motion.button>
      </div>
      <div className="flex gap-1.5">
        <motion.button
          whileHover={ANALYZE_HOVER}
          whileTap={ANALYZE_TAP}
          onClick={() => onPlan && onPlan(node)}
          data-testid="plan-node-btn"
          className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-body bg-[#10B981]/10 text-[#10B981] border border-[#10B981]/30 hover:bg-[#10B981]/20 transition-all duration-200"
        >
          <Map size={11} />
          Plan
        </motion.button>
        <motion.button
          whileHover={ANALYZE_HOVER}
          whileTap={ANALYZE_TAP}
          onClick={() => onPredict && onPredict(node)}
          data-testid="predict-node-btn"
          className="flex-1 flex items-center justify-center gap-1.5 py-2 rounded-lg text-xs font-body bg-[#F59E0B]/10 text-[#F59E0B] border border-[#F59E0B]/30 hover:bg-[#F59E0B]/20 transition-all duration-200"
        >
          <TrendingUp size={11} />
          Predict
        </motion.button>
      </div>

      {/* Agent outputs */}
      <AnimatePresence>
        {agentOutputs && Object.keys(agentOutputs).length > 0 && (
          <motion.div {...AGENTS_ANIM} className="space-y-1.5 flex-1 overflow-y-auto scroll-cyber" data-testid="agent-outputs">
            {Object.entries(agentOutputs).map(([key, val]) => {
              if (key === "synthesis") return null;
              const ac = AGENT_COLORS[key] || "#06B6D4";
              const output = typeof val === "object" ? val.output : val;
              return (
                <div key={key} className="glass-panel rounded-lg p-2.5" style={{ borderColor: ac + "30" }} data-testid={`agent-output-${key}`}>
                  <div className="text-[10px] font-body tracking-widest uppercase mb-1" style={{ color: ac }}>
                    {key.replace("_", " ")}
                  </div>
                  <p className="text-[11px] font-body text-[#94A3B8] leading-relaxed">{output}</p>
                </div>
              );
            })}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Consensus result */}
      <AnimatePresence>
        {consensusResult && (
          <motion.div
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0 }}
            className="glass-panel rounded-xl p-3"
            style={{ borderColor: "#3B82F640" }}
            data-testid="consensus-result"
          >
            <div className="flex items-center justify-between mb-2">
              <div className="text-[10px] font-body text-[#3B82F6] tracking-widest uppercase">Consensus</div>
              {consensusResult.confidence !== undefined && (
                <span className="text-[10px] font-body text-[#64748B]">
                  {Math.round(consensusResult.confidence * 100)}% confidence
                </span>
              )}
            </div>
            <p className="text-[11px] font-body text-[#94A3B8] leading-relaxed mb-2">{consensusResult.consensus}</p>
            {consensusResult.dissent && (
              <p className="text-[10px] font-body text-[#F59E0B] italic">↯ {consensusResult.dissent}</p>
            )}
          </motion.div>
        )}
      </AnimatePresence>

      {/* Find Path */}
      {allNodes && allNodes.length > 1 && (
        <div className="glass-panel rounded-xl p-3" style={{ borderColor: "#14B8A630" }} data-testid="find-path-section">
          <div className="text-[10px] font-body text-[#14B8A6] tracking-widest uppercase mb-2 flex items-center gap-1">
            <Route size={10} />
            <span>Find Path To</span>
          </div>
          <div className="flex gap-1.5">
            <select
              value={pathTarget}
              onChange={(e) => { setPathTarget(e.target.value); setPathResult(null); }}
              className="flex-1 bg-[#0A0A0F] border border-[#1E293B] rounded-lg px-2 py-1.5 text-[11px] font-body text-[#94A3B8] outline-none focus:border-[#14B8A6]/40 transition-colors"
              data-testid="path-target-select"
            >
              <option value="">Select node...</option>
              {(allNodes || []).filter((n) => n.id !== node.id).map((n) => (
                <option key={n.id} value={n.id}>{n.summary || n.content?.slice(0, 40)}</option>
              ))}
            </select>
            <button
              onClick={findPath}
              disabled={!pathTarget || isFindingPath}
              data-testid="find-path-btn"
              className="px-2.5 py-1.5 rounded-lg text-xs bg-[#14B8A6]/10 text-[#14B8A6] border border-[#14B8A6]/30 hover:bg-[#14B8A6]/20 disabled:opacity-30 transition-all"
            >
              {isFindingPath ? "..." : <Route size={11} />}
            </button>
          </div>
          {pathResult && (
            <div className="mt-2 text-[10px] font-body" data-testid="path-result">
              {pathResult.found ? (
                <div>
                  <span className="text-[#14B8A6]">{pathResult.length} hop{pathResult.length !== 1 ? "s" : ""}</span>
                  <span className="text-[#475569]"> · {pathResult.path?.map((h) => h.summary || h.content?.slice(0,20)).join(" → ")}</span>
                </div>
              ) : (
                <span className="text-[#475569]">No path found between these nodes</span>
              )}
            </div>
          )}
        </div>
      )}

      {/* Chat */}
      <div className="mt-auto">
        <div className="text-[10px] font-body text-[#334155] tracking-widest uppercase mb-2 flex items-center gap-1">
          <MessageSquare size={10} />
          <span>Query this node</span>
        </div>

        {chatHistory.length > 0 && (
          <div className="mb-2 space-y-1.5 max-h-32 overflow-y-auto scroll-cyber" data-testid="chat-history">
            {chatHistory.map((msg) => (
              <div
                key={msg.id}
                className={`text-[11px] font-body rounded p-2 ${
                  msg.role === "user"
                    ? "bg-[#1E293B] text-[#CBD5E1] ml-4"
                    : "bg-[#06B6D4]/8 text-[#94A3B8] border border-[#06B6D4]/15"
                }`}
                data-testid={`chat-msg-${msg.id}`}
              >
                {msg.role === "sarai" && (
                  <div className="text-[9px] text-[#06B6D4] mb-0.5 uppercase tracking-widest">
                    SARAI {msg.agent && `· ${msg.agent}`}
                  </div>
                )}
                {msg.text}
              </div>
            ))}
            {chatLoading && <div className="shimmer h-6 rounded" />}
          </div>
        )}

        <div className="flex gap-2">
          <input
            value={chatMsg}
            onChange={(e) => setChatMsg(e.target.value)}
            onKeyDown={(e) => e.key === "Enter" && sendChat()}
            placeholder="Ask about this thought..."
            className="flex-1 bg-[#0A0A0F] border border-[#1E293B] rounded-lg px-3 py-2 text-xs font-body text-[#F8FAFC] placeholder-[#334155] outline-none focus:border-[#06B6D4]/40 transition-colors"
            data-testid="node-chat-input"
          />
          <button
            onClick={sendChat}
            disabled={!chatMsg.trim() || chatLoading}
            data-testid="node-chat-send"
            className="px-3 py-2 rounded-lg text-xs bg-[#06B6D4]/10 text-[#06B6D4] border border-[#06B6D4]/30 hover:bg-[#06B6D4]/20 disabled:opacity-30 transition-all"
          >
            <Zap size={12} />
          </button>
        </div>
      </div>
      {debateResult && (
        <DebatePanel
          debate={debateResult.debate}
          thought={debateResult.thought}
          onClose={() => setDebateResult(null)}
        />
      )}
    </motion.div>
  );
};

export default NodeDetail;
