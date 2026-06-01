import React, { useState, useCallback, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Activity, Clock, Network, Volume2, VolumeX, RefreshCw, Cpu, Upload } from "lucide-react";
import "./index.css";
import { useGraphData } from "./hooks/useGraphData";
import ParallaxBackground from "./components/ParallaxBackground";
import NeuralGraph from "./components/NeuralGraph";
import ThoughtInput from "./components/ThoughtInput";
import AgentChamber from "./components/AgentChamber";
import CognitiveTimeline from "./components/CognitiveTimeline";
import NodeDetail from "./components/NodeDetail";
import RecursiveDashboard from "./components/RecursiveDashboard";
import SearchBar from "./components/SearchBar";
import SimulationPanel from "./components/SimulationPanel";
import PlanPanel from "./components/PlanPanel";
import PredictPanel from "./components/PredictPanel";
import JarvisVoice from "./components/JarvisVoice";
import ImportModal from "./components/ImportModal";

const BACKEND = process.env.REACT_APP_BACKEND_URL;
const API_HEADERS = { "X-API-Key": process.env.REACT_APP_API_KEY || "" };
const devLog = (msg, err) => { if (process.env.NODE_ENV === "development") console.error(msg, err); };

// Stable animation configs (outside component to prevent re-render object creation)
const HEADER_ANIM = { initial: { opacity: 0, y: -20 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.6 } };
const LEFT_PANEL_ANIM = { initial: { opacity: 0, x: -30 }, animate: { opacity: 1, x: 0 }, transition: { duration: 0.6, delay: 0.1 } };
const CENTER_ANIM = { initial: { opacity: 0, scale: 0.97 }, animate: { opacity: 1, scale: 1 }, transition: { duration: 0.7, delay: 0.15 } };
const RIGHT_PANEL_ANIM = { initial: { opacity: 0, x: 30 }, animate: { opacity: 1, x: 0 }, transition: { duration: 0.6, delay: 0.2 } };
const FOOTER_ANIM = { initial: { opacity: 0, y: 30 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.6, delay: 0.3 } };
const EMPTY_PULSE = { animate: { opacity: [0.2, 0.5, 0.2], scale: [0.98, 1.02, 0.98] }, transition: { duration: 3, repeat: Infinity } };
const STATUS_DOT_ANIM = { animate: { opacity: [0.5, 1, 0.5] }, transition: { duration: 1.5, repeat: Infinity } };
const CPU_SPIN_ANIM = { animate: { rotate: 360 }, transition: { duration: 20, repeat: Infinity, ease: "linear" } };
const PROCESSING_SPIN = { animate: { rotate: 360 }, transition: { duration: 1, repeat: Infinity, ease: "linear" } };
const SYNTH_ANIM = { initial: { opacity: 0, y: 10 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0 } };

export default function App() {
  const { nodes, links, stats, timelineEntries, status, refreshAll, fetchGraph, fetchStats, fetchTimeline } = useGraphData();

  const [selectedNode, setSelectedNode] = useState(null);
  const [isProcessing, setIsProcessing] = useState(false);
  const [activeNodeId, setActiveNodeId] = useState(null);
  const [agentOutputs, setAgentOutputs] = useState({});
  const [nodeAgentOutputs, setNodeAgentOutputs] = useState({});
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [ttsEnabled, setTtsEnabled] = useState(true);
  const [audioB64, setAudioB64] = useState(null);
  const [activeTab, setActiveTab] = useState("agents");
  const [simulationResult, setSimulationResult] = useState(null);
  const [simulationThought, setSimulationThought] = useState("");
  const [planResult, setPlanResult] = useState(null);
  const [predictResult, setPredictResult] = useState(null);
  const [improveResult, setImproveResult] = useState(null);
  const [isImproving, setIsImproving] = useState(false);
  const ttsEnabledRef = useRef(ttsEnabled);
  const [pathNodeIds, setPathNodeIds] = useState([]);
  const [clusterMap, setClusterMap] = useState({});
  const [showImport, setShowImport] = useState(false);

  // Keep ref in sync so handleThoughtAdded closure always reads latest value
  const handleTtsToggle = useCallback(() => {
    setTtsEnabled((v) => {
      ttsEnabledRef.current = !v;
      return !v;
    });
  }, []);

  const handleThoughtAdded = useCallback(async (data) => {
    setActiveNodeId(data.id);
    setAgentOutputs({ synthesis: data.synthesis });
    await Promise.all([fetchGraph(), fetchStats(), fetchTimeline()]);
    fetchClusters();

    if (ttsEnabledRef.current && data.synthesis) {
      try {
        const resp = await fetch(`${BACKEND}/api/tts`, {
          method: "POST",
          headers: { "Content-Type": "application/json", ...API_HEADERS },
          body: JSON.stringify({ text: data.synthesis }),
        });
        if (resp.ok) {
          const { audio } = await resp.json();
          setAudioB64(audio);
        }
      } catch (err) {
        devLog("TTS error:", err);
      }
    }
    setTimeout(() => setActiveNodeId(null), 4000);
  }, [fetchGraph, fetchStats, fetchTimeline]);

  const handleAnalyzeNode = useCallback(async (node) => {
    setIsAnalyzing(true);
    setNodeAgentOutputs({});
    try {
      const resp = await fetch(`${BACKEND}/api/agents/analyze`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...API_HEADERS },
        body: JSON.stringify({ content: node.content }),
      });
      if (resp.ok) {
        const data = await resp.json();
        setNodeAgentOutputs(data.agents);
      }
    } catch (err) {
      devLog("analyzeNode error:", err);
    } finally {
      setIsAnalyzing(false);
    }
  }, []);

  const handleDeleteNode = useCallback(async (nodeId) => {
    try {
      await fetch(`${BACKEND}/api/thoughts/${nodeId}`, { method: "DELETE", headers: API_HEADERS });
      setSelectedNode(null);
      await Promise.all([fetchGraph(), fetchStats(), fetchTimeline()]);
    } catch (err) {
      devLog("deleteNode error:", err);
    }
  }, [fetchGraph, fetchStats, fetchTimeline]);

  const handleNodeSelect = useCallback((node) => {
    setSelectedNode(node);
    setNodeAgentOutputs({});
  }, []);

  const handleCloseDetail = useCallback(() => {
    setSelectedNode(null);
    setNodeAgentOutputs({});
  }, []);

  const fetchClusters = useCallback(async () => {
    try {
      const res = await fetch(`${BACKEND}/api/graph/clusters`, { headers: API_HEADERS });
      if (res.ok) {
        const data = await res.json();
        setClusterMap(data.clusters || {});
      }
    } catch (_) {}
  }, []);

  const handleFindPath = useCallback(async (fromNode, toNode) => {
    if (!fromNode?.id || !toNode?.id) return;
    try {
      const res = await fetch(
        `${BACKEND}/api/graph/path?from_id=${fromNode.id}&to_id=${toNode.id}`,
        { headers: API_HEADERS }
      );
      if (res.ok) {
        const data = await res.json();
        if (data.found && data.path) {
          setPathNodeIds(data.path.map((p) => p.id));
          setTimeout(() => setPathNodeIds([]), 8000);
        }
      }
    } catch (_) {}
  }, []);

  const handleSimulate = useCallback(async (node) => {
    try {
      const resp = await fetch(`${BACKEND}/api/simulate`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...API_HEADERS },
        body: JSON.stringify({ content: node.content }),
      });
      if (resp.ok) {
        const data = await resp.json();
        setSimulationResult(data.scenarios);
        setSimulationThought(node.content);
      }
    } catch (err) {
      devLog("simulate error:", err);
    }
  }, []);

  const handlePlan = useCallback(async (node) => {
    try {
      const res = await fetch(`${BACKEND}/api/plan`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...API_HEADERS },
        body: JSON.stringify({ content: node.content }),
      });
      if (res.ok) { const d = await res.json(); setPlanResult(d); }
    } catch (_) {}
  }, []);

  const handlePredict = useCallback(async (node) => {
    try {
      const res = await fetch(`${BACKEND}/api/predict`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...API_HEADERS },
        body: JSON.stringify({ content: node.content }),
      });
      if (res.ok) { const d = await res.json(); setPredictResult(d); }
    } catch (_) {}
  }, []);

  const handleImprove = useCallback(async () => {
    if (isImproving) return;
    setIsImproving(true);
    try {
      const res = await fetch(`${BACKEND}/api/reflect/improve`, { headers: API_HEADERS });
      if (res.ok) { const d = await res.json(); setImproveResult(d); }
    } catch (_) {}
    finally { setIsImproving(false); }
  }, [isImproving]);

  const handleUpdateNode = useCallback((updated) => {
    setSelectedNode((prev) => prev?.id === updated.id ? { ...prev, ...updated } : prev);
    fetchGraph();
  }, [fetchGraph]);

  const handleCreateConnection = useCallback(async (sourceId, targetId) => {
    try {
      await fetch(`${BACKEND}/api/connections`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...API_HEADERS },
        body: JSON.stringify({ source: sourceId, target: targetId, relationship: "manual" }),
      });
      await fetchGraph();
    } catch (err) {
      devLog("createConnection error:", err);
    }
  }, [fetchGraph]);

  const handleTimelineSelect = useCallback((entry) => {
    const node = nodes.find((n) => n.id === entry.id);
    if (node) setSelectedNode(node);
  }, [nodes]);

  const coherenceColor =
    stats.brain_coherence > 70 ? "#10B981" :
    stats.brain_coherence > 40 ? "#F59E0B" : "#06B6D4";

  return (
    <div
      className="scanlines w-screen h-screen overflow-hidden relative flex flex-col"
      style={{ background: "#030305" }}
      data-testid="app-root"
    >
      <ParallaxBackground />
      {showImport && (
        <ImportModal
          onClose={() => setShowImport(false)}
          onImported={() => { setShowImport(false); refreshAll(); }}
        />
      )}
      <SimulationPanel
        scenarios={simulationResult}
        thought={simulationThought}
        onClose={() => setSimulationResult(null)}
      />
      {planResult && (
        <PlanPanel plan={planResult.plan} thought={planResult.thought} onClose={() => setPlanResult(null)} />
      )}
      {predictResult && (
        <PredictPanel result={predictResult} thought={predictResult.thought} onClose={() => setPredictResult(null)} />
      )}
      {audioB64 && <JarvisVoice audioB64={audioB64} onEnd={() => setAudioB64(null)} />}

      <div className="relative z-10 flex flex-col h-full">

        {/* TOP BAR */}
        <motion.header
          {...HEADER_ANIM}
          className="flex items-center justify-between px-6 py-3 glass-panel border-x-0 border-t-0 shrink-0"
          style={{ borderBottomColor: "rgba(6, 182, 212, 0.15)" }}
          data-testid="top-bar"
        >
          <div className="flex items-center gap-3">
            <motion.div {...CPU_SPIN_ANIM} className="relative">
              <Cpu size={22} color="#06B6D4" style={{ filter: "drop-shadow(0 0 8px #06B6D4)" }} />
            </motion.div>
            <div>
              <h1 className="font-heading text-base font-black tracking-widest holo-text">SARAI</h1>
              <div className="text-[10px] font-body text-[#334155] tracking-[0.3em] uppercase -mt-0.5">
                Jarvis 3.0 // Second Brain
              </div>
            </div>
          </div>

          <div className="hidden sm:flex items-center gap-6" data-testid="stats-row">
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

          <div className="flex items-center gap-3">
            <SearchBar onSelectNode={handleNodeSelect} nodes={nodes} />
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => setShowImport(true)}
              data-testid="import-btn"
              className="p-2 rounded-lg border border-[#1E293B] text-[#334155] hover:border-[#06B6D4]/40 hover:text-[#06B6D4] transition-all duration-200"
              title="Bulk Import Thoughts"
            >
              <Upload size={14} />
            </motion.button>
            <motion.button
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={handleTtsToggle}
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
              onClick={refreshAll}
              data-testid="refresh-btn"
              className="p-2 rounded-lg border border-[#1E293B] text-[#334155] hover:border-[#06B6D4]/40 hover:text-[#06B6D4] transition-all duration-200"
              title="Refresh"
            >
              <RefreshCw size={14} />
            </motion.button>

            <div className="flex items-center gap-1.5 px-3 py-1.5 rounded-full border border-[#10B981]/30 bg-[#10B981]/5">
              <motion.div {...STATUS_DOT_ANIM} className="w-1.5 h-1.5 rounded-full bg-[#10B981]" />
              <span className="text-[10px] font-body text-[#10B981] tracking-widest">{status}</span>
            </div>
          </div>
        </motion.header>

        {/* MAIN LAYOUT */}
        <div className="flex flex-1 overflow-hidden gap-0 flex-col md:flex-row">

          {/* LEFT PANEL */}
          <motion.aside
            {...LEFT_PANEL_ANIM}
            className="hidden md:flex w-64 shrink-0 flex-col glass-panel border-y-0 border-l-0"
            style={{ borderRightColor: "rgba(6, 182, 212, 0.1)" }}
            data-testid="left-panel"
          >
            <div className="flex border-b border-[#1E293B] shrink-0">
              {[
                { id: "agents",    icon: <Cpu size={11} />,     label: "Agents" },
                { id: "timeline",  icon: <Clock size={11} />,    label: "Timeline" },
                { id: "dashboard", icon: <Activity size={11} />, label: "Insight" },
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

            <div className="flex-1 overflow-hidden p-3">
              {activeTab === "agents" ? (
                <AgentChamber agentOutputs={agentOutputs} isProcessing={isProcessing} activeAgent={null} />
              ) : activeTab === "timeline" ? (
                <div className="h-full overflow-y-auto scroll-cyber">
                  <CognitiveTimeline
                    entries={timelineEntries}
                    onSelect={handleTimelineSelect}
                    selectedId={selectedNode?.id}
                  />
                </div>
              ) : (
                <RecursiveDashboard
                  nodes={nodes}
                  stats={stats}
                  onImprove={handleImprove}
                  isImproving={isImproving}
                  improveResult={improveResult}
                />
              )}
            </div>
          </motion.aside>

          {/* CENTER — Neural Graph */}
          <motion.main {...CENTER_ANIM} className="flex-1 relative overflow-hidden min-h-[40vh] md:min-h-0" data-testid="graph-main">
            <NeuralGraph
              nodes={nodes}
              links={links}
              selectedNode={selectedNode}
              onNodeSelect={handleNodeSelect}
              activeNodeId={activeNodeId}
              pathNodeIds={pathNodeIds}
              clusterMap={clusterMap}
              onCreateConnection={handleCreateConnection}
            />

            <AnimatePresence>
              {isProcessing && (
                <motion.div
                  initial={{ opacity: 0 }}
                  animate={{ opacity: 1 }}
                  exit={{ opacity: 0 }}
                  className="absolute top-4 left-1/2 -translate-x-1/2 flex items-center gap-2 glass-panel px-4 py-2 rounded-full"
                  data-testid="processing-indicator"
                >
                  <motion.div {...PROCESSING_SPIN}>
                    <Cpu size={12} color="#06B6D4" />
                  </motion.div>
                  <span className="text-xs font-body text-[#06B6D4] tracking-widest">
                    SARAI processing thought...
                  </span>
                </motion.div>
              )}
            </AnimatePresence>
          </motion.main>

          {/* RIGHT PANEL */}
          <motion.aside
            {...RIGHT_PANEL_ANIM}
            className="w-full md:w-72 shrink-0 glass-panel border-y-0 border-r-0 p-3 overflow-hidden md:max-h-full max-h-64"
            style={{ borderLeftColor: "rgba(6, 182, 212, 0.1)" }}
            data-testid="right-panel"
          >
            <AnimatePresence mode="wait">
              {selectedNode ? (
                <NodeDetail
                  key={selectedNode.id}
                  node={selectedNode}
                  onClose={handleCloseDetail}
                  onAnalyze={handleAnalyzeNode}
                  isAnalyzing={isAnalyzing}
                  agentOutputs={nodeAgentOutputs}
                  onDelete={handleDeleteNode}
                  graphLinks={links}
                  onSimulate={handleSimulate}
                  onPlan={handlePlan}
                  onPredict={handlePredict}
                  onFindPath={(pathIds) => { setPathNodeIds(pathIds); setTimeout(() => setPathNodeIds([]), 8000); }}
                  allNodes={nodes}
                  onUpdate={handleUpdateNode}
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
                    {...EMPTY_PULSE}
                    className="text-5xl"
                    style={{ filter: "drop-shadow(0 0 15px #06B6D4)" }}
                  >
                    ◉
                  </motion.div>
                  <div>
                    <p className="text-xs font-body text-[#334155] tracking-widest uppercase">Select a node</p>
                    <p className="text-[11px] font-body text-[#1E293B] mt-1">
                      Click any neural node to inspect and analyze
                    </p>
                  </div>

                  <AnimatePresence>
                    {agentOutputs?.synthesis && (
                      <motion.div
                        {...SYNTH_ANIM}
                        className="glass-panel rounded-xl p-3 w-full mt-2"
                        style={{ borderColor: "#06B6D430" }}
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

        {/* BOTTOM */}
        <motion.footer
          {...FOOTER_ANIM}
          className="shrink-0 px-6 py-3 glass-panel border-x-0 border-b-0"
          style={{ borderTopColor: "rgba(6, 182, 212, 0.1)" }}
          data-testid="bottom-bar"
        >
          {timelineEntries.length > 0 && (
            <div className="mb-3">
              <CognitiveTimeline
                entries={timelineEntries.slice(-10)}
                onSelect={handleTimelineSelect}
                selectedId={selectedNode?.id}
              />
            </div>
          )}
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

const StatPill = ({ icon, label, value, color, testId }) => (
  <div className="flex items-center gap-1.5" data-testid={testId}>
    <span style={{ color }}>{icon}</span>
    <div>
      <div className="text-[10px] font-body text-[#334155] uppercase tracking-widest leading-none">{label}</div>
      <div className="text-sm font-body font-medium" style={{ color }}>{value}</div>
    </div>
  </div>
);
