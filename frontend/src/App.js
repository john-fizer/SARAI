import React, { useState, useEffect, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, Clock, Network, Volume2, VolumeX, RefreshCw, Cpu } from "lucide-react";
import "./index.css";
import ParallaxBackground from "./components/ParallaxBackground";
import NeuralGraph from "./components/NeuralGraph";
import ThoughtInput from "./components/ThoughtInput";
import AgentChamber from "./components/AgentChamber";
import CognitiveTimeline from "./components/CognitiveTimeline";
import NodeDetail from "./components/NodeDetail";
import JarvisVoice from "./components/JarvisVoice";

const BACKEND = process.env.REACT_APP_BACKEND_URL;

export default function App() {
  const [nodes, setNodes] = useState([]);
  const [links, setLinks] = useState([]);
  const [selectedNode, setSelectedNode] = useState(null);
  const [stats, setStats] = useState({ total_thoughts: 0, total_connections: 0, brain_coherence: 0 });
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeNodeId, setActiveNodeId] = useState(null);
  const [agentOutputs, setAgentOutputs] = useState({});
  const [nodeAgentOutputs, setNodeAgentOutputs] = useState({});
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [timelineEntries, setTimelineEntries] = useState([]);
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [audioB64, setAudioB64] = useState(null);
  const [activeTab, setActiveTab] = useState("agents"); // 'agents' | 'timeline'
  const [status, setStatus] = useState("ONLINE");
  const pollingRef = useRef(null);

  // Fetch graph
  const fetchGraph = useCallback(async () => {
    try {
      const res = await fetch(`${BACKEND}/api/graph`);
      if (res.ok) {
        const { nodes: n, links: l } = await res.json();
        setNodes(n);
        setLinks(l);
      }
    } catch (err) {
      setStatus("DEGRADED");
    }
  }, []);

  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch(`${BACKEND}/api/stats`);
      if (res.ok) setStats(await res.json());
    } catch (err) {}
  }, []);

  const fetchTimeline = useCallback(async () => {
    try {
      const res = await fetch(`${BACKEND}/api/timeline`);
      if (res.ok) {
        const { entries } = await res.json();
        setTimelineEntries(entries);
      }
    } catch (err) {}
  }, []);

  // Initial load + polling
  useEffect(() => {
    fetchGraph();
    fetchStats();
    fetchTimeline();
    pollingRef.current = setInterval(() => {
      fetchGraph();
      fetchStats();
      fetchTimeline();
    }, 8000);
    return () => clearInterval(pollingRef.current);
  }, [fetchGraph, fetchStats, fetchTimeline]);

  // Handle new thought
  const handleThoughtAdded = useCallback(async (data) => {
    setActiveNodeId(data.id);
    setAgentOutputs({ synthesis: data.synthesis });

    // Refresh graph
    await fetchGraph();
    await fetchStats();
    await fetchTimeline();

    // TTS synthesis
    if (ttsEnabled && data.synthesis) {
      try {
        const resp = await fetch(`${BACKEND}/api/tts`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text: data.synthesis }),
        });
        if (resp.ok) {
          const { audio } = await resp.json();
          setAudioB64(audio);
        }
      } catch (err) {
        console.error("TTS error:", err);
      }
    }

    // Clear active node after animation
    setTimeout(() => setActiveNodeId(null), 4000);
  }, [fetchGraph, fetchStats, fetchTimeline, ttsEnabled]);

  // Handle agent analysis for a node
  const handleAnalyzeNode = useCallback(async (node) => {
    setIsAnalyzing(true);
    setNodeAgentOutputs({});
    try {
      const resp = await fetch(`${BACKEND}/api/agents/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ content: node.content }),
      });
      if (resp.ok) {
        const data = await resp.json();
        setNodeAgentOutputs(data.agents);
      }
    } catch (err) {
      console.error(err);
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  // Handle node deletion
  const handleDeleteNode = useCallback(async (nodeId) => {
    try {
      await fetch(`${BACKEND}/api/thoughts/${nodeId}`, { method: "DELETE" });
      setSelectedNode(null);
      await fetchGraph();
      await fetchStats();
      await fetchTimeline();
    } catch (err) {
      console.error(err);
    }
  }, [fetchGraph, fetchStats, fetchTimeline]);

  const coherenceColor =
    stats.brain_coherence > 70 ? "#10B981" :
    stats.brain_coherence > 40 ? "#F59E0B" : "#06B6D4";

  return (
    <div className="scanlines w-screen h-screen overflow-hidden relative flex flex-col" style={{ background: "#030305" }} data-testid="app-root">
      {/* Parallax star background */}
      <ParallaxBackground />

      {/* TTS player */}
      {audioB64 && (
        <JarvisVoice audioB64={audioB64} onEnd={() => setAudioB64(null)} />
      )}

      {/* Main content above background */}
      <div className="relative z-10 flex flex-col h-full">

        {/* ── TOP BAR ─────────────────────────────────────────────── */}
        <motion.header
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6 }}
          className="flex items-center justify-between px-6 py-3 glass-panel border-x-0 border-t-0 shrink-0"
          style={{ borderBottomColor: "rgba(6, 182, 212, 0.15)" }}
          data-testid="top-bar"
        >
          {/* Logo */}
          <div className="flex items-center gap-3">
            <motion.div
              animate={{ rotate: 360 }}
              transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
              className="relative"
            >
              <Cpu size={22} color="#06B6D4" style={{ filter: "drop-shadow(0 0 8px #06B6D4)" }} />
            </motion.div>
            <div>
              <h1 className="font-heading text-base font-black tracking-widest holo-text">
                SARAI
              </h1>
              <div className="text-[10px] font-body text-[#334155] tracking-[0.3em] uppercase -mt-0.5">
                Jarvis 3.0 // Second Brain
              </div>
            </div>
          </div>

          {/* Stats */}
          <div className="flex items-center gap-6" data-testid="stats-row">
            <StatPill icon={<Network size={11} />} label="Nodes" value={stats.total_thoughts} color="#06B6D4" testId="stat-nodes" />
            <StatPill icon={<Activity size={11} />} label="Synapses" value={stats.total_connections} color="#3B82F6" testId="stat-synapses" />
            <StatPill
              icon={<div className="w-2 h-2 rounded-full" style={{ background: coherenceColor }} />}
              label="Coherence"
              value={`${stats.brain_coherence}%`}
              color={coherenceColor}
              testId="stat-coherence"
            />
          </div>

          {/* Controls */}
          <div className="flex items-center gap-3">
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setTtsEnabled((v) => !v)}
              data-testid="tts-toggle-btn"
              className={`p-2 rounded-lg border transition-all duration-200 ${
                ttsEnabled
                  ? "border-[#06B6D4]/40 text-[#06B6D4] bg-[#06B6D4]/10"
                  : "border-[#1E293B] text-[#334155]"
              }`}
              title={ttsEnabled ? "Disable Jarvis Voice" : "Enable Jarvis Voice"}
            >
              {ttsEnabled ? <Volume2 size={14} /> : <VolumeX size={14} />}
            </motion.button>

            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => { fetchGraph(); fetchStats(); fetchTimeline(); }}
              data-testid="refresh-btn"
              className="p-2 rounded-lg border border-[#1E293B] text-[#334155] hover:border-[#06B6D4]/40 hover:text-[#06B6D4] transition-all duration-200"
              title="Refresh"
            >
              <RefreshCw size={14} />
            </motion.button>

            {/* Status indicator */}
            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-[#10B981]/30 bg-[#10B981]/5">
              <motion.div
                animate={{ opacity: [0.5, 1, 0.5] }}
                transition={{ duration: 1.5, repeat: Infinity }}
                className="w-1.5 h-1.5 rounded-full bg-[#10B981]"
              />
              <span className="text-[10px] font-body text-[#10B981] tracking-widest">{status}</span>
            </div>
          </div>
        </motion.header>

        {/* ── MAIN LAYOUT ─────────────────────────────────────────── */}
        <div className="flex flex-1 overflow-hidden gap-0">

          {/* LEFT PANEL — Agent Chamber + Timeline */}
          <motion.aside
            initial={{ opacity: 0, x: -30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.1 }}
            className="w-64 shrink-0 flex flex-col glass-panel border-y-0 border-l-0"
            style={{ borderRightColor: "rgba(6, 182, 212, 0.1)" }}
            data-testid="left-panel"
          >
            {/* Tab switcher */}
            <div className="flex border-b border-[#1E293B] shrink-0">
              {[
                { id: "agents", icon: <Cpu size={11} />, label: "Agents" },
                { id: "timeline", icon: <Clock size={11} />, label: "Timeline" },
              ].map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  data-testid={`tab-${tab.id}`}
                  className={`flex-1 flex items-center justify-center gap-1.5 py-2.5 text-[10px] font-body tracking-widest uppercase transition-all duration-200 ${
                    activeTab === tab.id
                      ? "text-[#06B6D4] border-b border-[#06B6D4] -mb-px"
                      : "text-[#334155] hover:text-[#64748B]"
                  }`}
                >
                  {tab.icon}
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab content */}
            <div className="flex-1 overflow-hidden p-3">
              {activeTab === "agents" ? (
                <AgentChamber
                  agentOutputs={agentOutputs}
                  isProcessing={isProcessing}
                  activeAgent={null}
                />
              ) : (
                <div className="h-full overflow-y-auto scroll-cyber">
                  <CognitiveTimeline
                    entries={timelineEntries}
                    onSelect={(entry) => {
                      const node = nodes.find((n) => n.id === entry.id);
                      if (node) setSelectedNode(node);
                    }}
                    selectedId={selectedNode?.id}
                  />
                </div>
              )}
            </div>
          </motion.aside>

          {/* CENTER — Neural Graph */}
          <motion.main
            initial={{ opacity: 0, scale: 0.97 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.7, delay: 0.15 }}
            className="flex-1 relative overflow-hidden"
            data-testid="graph-main"
          >
            <NeuralGraph
              nodes={nodes}
              links={links}
              selectedNode={selectedNode}
              onNodeSelect={(node) => {
                setSelectedNode(node);
                setNodeAgentOutputs({});
              }}
              activeNodeId={activeNodeId}
            />

            {/* Processing overlay */}
            <AnimatePresence>
              {isProcessing && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="absolute top-4 left-1/2 -translate-x-1/2 flex items-center gap-2 glass-panel px-4 py-2 rounded-full"
                  data-testid="processing-indicator"
                >
                  <motion.div
                    animate={{ rotate: 360 }}
                    transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                  >
                    <Cpu size={12} color="#06B6D4" />
                  </motion.div>
                  <span className="text-xs font-body text-[#06B6D4] tracking-widest">
                    SARAI processing thought...
                  </span>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.main>

          {/* RIGHT PANEL — Node Detail */}
          <motion.aside
            initial={{ opacity: 0, x: 30 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="w-72 shrink-0 glass-panel border-y-0 border-r-0 p-3 overflow-hidden"
            style={{ borderLeftColor: "rgba(6, 182, 212, 0.1)" }}
            data-testid="right-panel"
          >
            <AnimatePresence mode="wait">
              {selectedNode ? (
                <NodeDetail
                  key={selectedNode.id}
                  node={selectedNode}
                  onClose={() => { setSelectedNode(null); setNodeAgentOutputs({}); }}
                  onAnalyze={handleAnalyzeNode}
                  isAnalyzing={isAnalyzing}
                  agentOutputs={nodeAgentOutputs}
                  onDelete={handleDeleteNode}
                  graphLinks={links}
                />
              ) : (
                <motion.div
                  key="empty-right"
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="h-full flex flex-col items-center justify-center gap-4 text-center"
                  data-testid="right-panel-empty"
                >
                  <motion.div
                    animate={{ opacity: [0.2, 0.5, 0.2], scale: [0.98, 1.02, 0.98] }}
                    transition={{ duration: 3, repeat: Infinity }}
                    className="text-5xl"
                    style={{ filter: "drop-shadow(0 0 15px #06B6D4)" }}
                  >
                    ◉
                  </motion.div>
                  <div>
                    <p className="text-xs font-body text-[#334155] tracking-widest uppercase">
                      Select a node
                    </p>
                    <p className="text-[11px] font-body text-[#1E293B] mt-1">
                      Click any neural node to inspect and analyze
                    </p>
                  </div>

                  {/* Recent synthesis */}
                  <AnimatePresence>
                    {agentOutputs?.synthesis && (
                      <motion.div
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0 }}
                        className="glass-panel rounded-xl p-3 w-full mt-2"
                        style={{ borderColor: "#06B6D4" + "30" }}
                        data-testid="last-synthesis"
                      >
                        <div className="text-[10px] font-body text-[#06B6D4] tracking-widest uppercase mb-1.5">
                          Last Synthesis
                        </div>
                        <p className="text-[11px] font-body text-[#94A3B8] leading-relaxed">
                          {agentOutputs.synthesis}
                        </p>
                      </motion.div>
                    )}
                  </AnimatePresence>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.aside>
        </div>

        {/* ── BOTTOM — Thought Input + Timeline ────────────────────── */}
        <motion.footer
          initial={{ opacity: 0, y: 30 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.6, delay: 0.3 }}
          className="shrink-0 px-6 py-3 glass-panel border-x-0 border-b-0"
          style={{ borderTopColor: "rgba(6, 182, 212, 0.1)" }}
          data-testid="bottom-bar"
        >
          {/* Timeline strip */}
          {timelineEntries.length > 0 && (
            <div className="mb-3">
              <CognitiveTimeline
                entries={timelineEntries.slice(-10)}
                onSelect={(entry) => {
                  const node = nodes.find((n) => n.id === entry.id);
                  if (node) setSelectedNode(node);
                }}
                selectedId={selectedNode?.id}
              />
            </div>
          )}

          {/* Input */}
          <ThoughtInput
            onThoughtAdded={handleThoughtAdded}
            isProcessing={isProcessing}
            setIsProcessing={setIsProcessing}
          />
        </motion.footer>
      </div>
    </div>
  );
}

// Small stat pill component
const StatPill = ({ icon, label, value, color, testId }) => (
  <div className="flex items-center gap-1.5" data-testid={testId}>
    <span style={{ color }}>{icon}</span>
    <div>
      <div className="text-[10px] font-body text-[#334155] uppercase tracking-widest leading-none">{label}</div>
      <div className="text-sm font-body font-medium" style={{ color }}>{value}</div>
    </div>
  </div>
);
