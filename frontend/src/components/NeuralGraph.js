import React, { useEffect, useRef, useState, useCallback } from "react";
import * as d3 from "d3";
import { motion, AnimatePresence } from "framer-motion";

const NODE_COLORS = {
  idea: "#06B6D4",
  question: "#8B5CF6",
  insight: "#F59E0B",
  memory: "#10B981",
};

const CLUSTER_PALETTE = [
  "#06B6D4", "#8B5CF6", "#F59E0B", "#10B981",
  "#EC4899", "#F97316", "#3B82F6", "#14B8A6",
  "#A855F7", "#84CC16",
];

// Stable animation configs
const EMPTY_ANIM = {
  animate: { opacity: [0.3, 0.7, 0.3], scale: [0.98, 1.02, 0.98] },
  transition: { duration: 3, repeat: Infinity },
};
const TOOLTIP_ANIM = { initial: { opacity: 0, y: 5 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0 } };

// ── Pure render function (no hooks, stable reference) ────────────────────────
function renderFrame(ctx, w, h, ts, linksRef, nodesRef, particlesRef, selectedRef, activeRef, hoveredRef, pathRef, clusterMapRef, connSourceRef, mousePosRef) {
  ctx.clearRect(0, 0, w, h);

  // Grid dots
  ctx.fillStyle = "rgba(6, 182, 212, 0.04)";
  for (let x = 0; x < w; x += 48) {
    for (let y = 0; y < h; y += 48) {
      ctx.beginPath();
      ctx.arc(x, y, 1, 0, Math.PI * 2);
      ctx.fill();
    }
  }

  const lns = linksRef.current;
  const nds = nodesRef.current;

  // Draw links
  lns.forEach((link) => {
    const sx = link.source?.x, sy = link.source?.y;
    const tx = link.target?.x, ty = link.target?.y;
    if (!sx || !sy || !tx || !ty) return;

    const grad = ctx.createLinearGradient(sx, sy, tx, ty);
    grad.addColorStop(0, "rgba(6, 182, 212, 0.12)");
    grad.addColorStop(0.5, "rgba(59, 130, 246, 0.22)");
    grad.addColorStop(1, "rgba(6, 182, 212, 0.12)");

    ctx.beginPath();
    ctx.moveTo(sx, sy);
    ctx.lineTo(tx, ty);
    ctx.strokeStyle = grad;
    ctx.lineWidth = (link.strength || 0.5) * 2.5 + 0.5;
    ctx.shadowBlur = 4;
    ctx.shadowColor = "#06B6D4";
    ctx.stroke();
    ctx.shadowBlur = 0;
  });

  // Draw path highlight edges
  const pathIds = pathRef?.current || [];
  if (pathIds.length > 1) {
    for (let i = 0; i < pathIds.length - 1; i++) {
      const fromNode = nds.find((n) => n.id === pathIds[i]);
      const toNode = nds.find((n) => n.id === pathIds[i + 1]);
      if (!fromNode?.x || !toNode?.x) continue;
      ctx.beginPath();
      ctx.moveTo(fromNode.x, fromNode.y);
      ctx.lineTo(toNode.x, toNode.y);
      ctx.strokeStyle = "#FFFFFF";
      ctx.lineWidth = 2.5;
      ctx.shadowBlur = 12;
      ctx.shadowColor = "#FFFFFF";
      ctx.setLineDash([6, 4]);
      ctx.lineDashOffset = -(ts * 0.05) % 10;
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.shadowBlur = 0;
    }
  }

  // Draw pending manual connection line
  const connSrc = connSourceRef?.current;
  const mp = mousePosRef?.current;
  if (connSrc?.x && mp) {
    ctx.beginPath();
    ctx.moveTo(connSrc.x, connSrc.y);
    ctx.lineTo(mp.x, mp.y);
    ctx.strokeStyle = "#06B6D4";
    ctx.lineWidth = 1.5;
    ctx.shadowBlur = 8;
    ctx.shadowColor = "#06B6D4";
    ctx.setLineDash([5, 5]);
    ctx.lineDashOffset = -(ts * 0.06) % 10;
    ctx.stroke();
    ctx.setLineDash([]);
    ctx.shadowBlur = 0;
  }

  // Spawn particles periodically
  if (lns.length > 0 && ts % 900 < 20) {
    const rl = lns[Math.floor(Math.random() * lns.length)];
    if (rl.source?.x && rl.target?.x) {
      particlesRef.current.push({
        link: rl,
        progress: 0,
        speed: 0.006 + Math.random() * 0.008,
        color: NODE_COLORS[rl.source.type] || "#06B6D4",
      });
    }
  }

  // Draw synapse particles
  particlesRef.current = particlesRef.current.filter((p) => {
    p.progress += p.speed;
    if (p.progress > 1) return false;
    const x = p.link.source.x + (p.link.target.x - p.link.source.x) * p.progress;
    const y = p.link.source.y + (p.link.target.y - p.link.source.y) * p.progress;
    const alpha = p.progress < 0.2 ? p.progress * 5 : p.progress > 0.8 ? (1 - p.progress) * 5 : 1;
    ctx.beginPath();
    ctx.arc(x, y, 2.5, 0, Math.PI * 2);
    ctx.fillStyle = p.color + Math.floor(alpha * 255).toString(16).padStart(2, "0");
    ctx.shadowBlur = 10;
    ctx.shadowColor = p.color;
    ctx.fill();
    ctx.shadowBlur = 0;
    return true;
  });

  // Draw nodes
  nds.forEach((node) => {
    if (!node.x || !node.y) return;
    const color = NODE_COLORS[node.type] || "#06B6D4";
    const isSelected = selectedRef.current?.id === node.id;
    const isActive = activeRef.current === node.id;
    const isHovered = hoveredRef.current?.id === node.id;
    const isOnPath = pathIds.includes(node.id);
    const clusterIdx = clusterMapRef?.current?.[node.id];
    const clusterColor = (clusterIdx !== undefined && clusterIdx >= 0)
      ? CLUSTER_PALETTE[clusterIdx % CLUSTER_PALETTE.length]
      : null;
    const r = isSelected ? 22 : isHovered ? 18 : 14;

    const glowR = isActive ? r + 30 : isSelected ? r + 20 : r + 10;
    const aura = ctx.createRadialGradient(node.x, node.y, 0, node.x, node.y, glowR);
    aura.addColorStop(0, color + "55");
    aura.addColorStop(0.4, color + "22");
    aura.addColorStop(1, "transparent");
    ctx.beginPath();
    ctx.arc(node.x, node.y, glowR, 0, Math.PI * 2);
    ctx.fillStyle = aura;
    ctx.fill();

    if (clusterColor && !isSelected) {
      ctx.beginPath();
      ctx.arc(node.x, node.y, r + 3, 0, Math.PI * 2);
      ctx.strokeStyle = clusterColor + "70";
      ctx.lineWidth = 1.5;
      ctx.shadowBlur = 6;
      ctx.shadowColor = clusterColor;
      ctx.stroke();
      ctx.shadowBlur = 0;
    }

    const core = ctx.createRadialGradient(node.x - r * 0.3, node.y - r * 0.3, 0, node.x, node.y, r);
    core.addColorStop(0, color + "FF");
    core.addColorStop(0.5, color + "CC");
    core.addColorStop(1, color + "55");
    ctx.beginPath();
    ctx.arc(node.x, node.y, r, 0, Math.PI * 2);
    ctx.fillStyle = core;
    ctx.shadowBlur = isActive ? 25 : isSelected ? 18 : 10;
    ctx.shadowColor = color;
    ctx.fill();

    ctx.beginPath();
    ctx.arc(node.x, node.y, r, 0, Math.PI * 2);
    ctx.strokeStyle = isSelected ? "#FFFFFF" : color;
    ctx.lineWidth = isSelected ? 2 : 1.5;
    ctx.stroke();
    ctx.shadowBlur = 0;

    if (isOnPath) {
      ctx.beginPath();
      ctx.arc(node.x, node.y, r + 6, 0, Math.PI * 2);
      ctx.strokeStyle = "#FFFFFF";
      ctx.lineWidth = 2;
      ctx.shadowBlur = 15;
      ctx.shadowColor = "#FFFFFF";
      ctx.stroke();
      ctx.shadowBlur = 0;
    }

    if (isActive) {
      const pr = r + 8 + Math.sin(ts * 0.008) * 5;
      ctx.beginPath();
      ctx.arc(node.x, node.y, pr, 0, Math.PI * 2);
      ctx.strokeStyle = color + "60";
      ctx.lineWidth = 1.5;
      ctx.stroke();
      const pr2 = r + 18 + Math.sin(ts * 0.005 + 1) * 5;
      ctx.beginPath();
      ctx.arc(node.x, node.y, pr2, 0, Math.PI * 2);
      ctx.strokeStyle = color + "25";
      ctx.lineWidth = 1;
      ctx.stroke();
    }

    const label = node.content?.length > 22 ? node.content.substring(0, 22) + "..." : node.content;
    ctx.font = "9px JetBrains Mono, monospace";
    ctx.textAlign = "center";
    ctx.fillStyle = isSelected ? "#FFFFFF" : "#94A3B8";
    ctx.shadowBlur = 0;
    ctx.fillText(label, node.x, node.y + r + 14);
  });
}

const NeuralGraph = ({ nodes, links, selectedNode, onNodeSelect, activeNodeId, pathNodeIds, clusterMap, onCreateConnection }) => {
  const canvasRef = useRef(null);
  const simulationRef = useRef(null);
  const nodesRef = useRef([]);
  const linksRef = useRef([]);
  const particlesRef = useRef([]);
  const hoveredRef = useRef(null);
  const frameRef = useRef(null);
  const selectedRef = useRef(null);
  const activeRef = useRef(null);
  const pathRef = useRef([]);
  const clusterMapRef = useRef({});
  const connSourceRef = useRef(null);
  const mousePosRef = useRef(null);
  const [tooltip, setTooltip] = useState(null);
  const [connectSource, setConnectSource] = useState(null);

  // Keep refs in sync with props
  useEffect(() => { selectedRef.current = selectedNode; }, [selectedNode]);
  useEffect(() => { activeRef.current = activeNodeId; }, [activeNodeId]);
  useEffect(() => { pathRef.current = pathNodeIds || []; }, [pathNodeIds]);
  useEffect(() => { clusterMapRef.current = clusterMap || {}; }, [clusterMap]);

  // Init canvas + render loop — runs once on mount
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const parent = canvas.parentElement;

    const resize = () => {
      canvas.width = parent.clientWidth;
      canvas.height = parent.clientHeight;
    };
    resize();
    const ro = new ResizeObserver(resize);
    ro.observe(parent);

    const ctx = canvas.getContext("2d");
    const sim = d3
      .forceSimulation([])
      .force("link", d3.forceLink([]).id((d) => d.id).distance(160))
      .force("charge", d3.forceManyBody().strength(-450))
      .force("center", d3.forceCenter(canvas.width / 2, canvas.height / 2))
      .force("collision", d3.forceCollide().radius(38))
      .alphaDecay(0.015);

    simulationRef.current = sim;

    const loop = (ts) => {
      renderFrame(ctx, canvas.width, canvas.height, ts, linksRef, nodesRef, particlesRef, selectedRef, activeRef, hoveredRef, pathRef, clusterMapRef, connSourceRef, mousePosRef);
      frameRef.current = requestAnimationFrame(loop);
    };
    frameRef.current = requestAnimationFrame(loop);

    return () => {
      cancelAnimationFrame(frameRef.current);
      sim.stop();
      ro.disconnect();
    };
  }, []); // Intentionally empty — canvas setup runs once; all state read via refs

  // Update simulation when data changes
  useEffect(() => {
    const sim = simulationRef.current;
    if (!sim) return;

    const existingPos = new Map(nodesRef.current.map((n) => [n.id, { x: n.x, y: n.y, vx: n.vx, vy: n.vy }]));
    const d3Nodes = nodes.map((n) => {
      const ep = existingPos.get(n.id);
      return ep ? { ...n, ...ep } : { ...n };
    });
    const d3Links = links.map((l) => ({ ...l }));

    nodesRef.current = d3Nodes;
    linksRef.current = d3Links;

    sim
      .nodes(d3Nodes)
      .force("link", d3.forceLink(d3Links).id((d) => d.id).distance(160))
      .alpha(nodes.length > 0 ? 0.4 : 0)
      .restart();
  }, [nodes, links]);

  // Mouse hover — stable since it only reads canvasRef/nodesRef/hoveredRef (all refs)
  const handleMouseMove = useCallback((e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    mousePosRef.current = { x: mx, y: my };
    const found = nodesRef.current.find((n) => n.x && n.y && Math.hypot(n.x - mx, n.y - my) < 22);
    hoveredRef.current = found || null;
    if (connSourceRef.current) {
      canvas.style.cursor = found && found.id !== connSourceRef.current.id ? "cell" : "crosshair";
    } else {
      canvas.style.cursor = found ? "pointer" : "default";
    }
    if (found) {
      setTooltip({ node: found, x: e.clientX, y: e.clientY });
    } else {
      setTooltip(null);
    }
  }, []); // canvasRef, nodesRef, hoveredRef are stable refs

  // Click handler — depends on onNodeSelect prop
  const handleClick = useCallback((e) => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const rect = canvas.getBoundingClientRect();
    const mx = e.clientX - rect.left;
    const my = e.clientY - rect.top;
    const clicked = nodesRef.current.find((n) => n.x && n.y && Math.hypot(n.x - mx, n.y - my) < 22);
    if (connSourceRef.current) {
      if (clicked && clicked.id !== connSourceRef.current.id) {
        if (onCreateConnection) onCreateConnection(connSourceRef.current.id, clicked.id);
      }
      connSourceRef.current = null;
      setConnectSource(null);
      canvas.style.cursor = "default";
      return;
    }
    if (clicked) onNodeSelect(clicked);
  }, [onNodeSelect, onCreateConnection]);

  // Drag — runs once, reads simulation via ref
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    let dragging = null;

    const getNode = (mx, my) =>
      nodesRef.current.find((n) => n.x && n.y && Math.hypot(n.x - mx, n.y - my) < 22);

    const onDown = (e) => {
      const r = canvas.getBoundingClientRect();
      dragging = getNode(e.clientX - r.left, e.clientY - r.top);
      if (dragging && simulationRef.current) {
        simulationRef.current.alphaTarget(0.3).restart();
        dragging.fx = dragging.x;
        dragging.fy = dragging.y;
      }
    };
    const onMove = (e) => {
      if (!dragging) return;
      const r = canvas.getBoundingClientRect();
      dragging.fx = e.clientX - r.left;
      dragging.fy = e.clientY - r.top;
    };
    const onUp = () => {
      if (dragging && simulationRef.current) {
        simulationRef.current.alphaTarget(0);
        dragging.fx = null;
        dragging.fy = null;
      }
      dragging = null;
    };

    const onContextMenu = (e) => {
      e.preventDefault();
      const r = canvas.getBoundingClientRect();
      const node = getNode(e.clientX - r.left, e.clientY - r.top);
      if (node) {
        connSourceRef.current = node;
        setConnectSource(node);
        canvas.style.cursor = "crosshair";
      }
    };

    const onKeyDown = (e) => {
      if (e.key === "Escape" && connSourceRef.current) {
        connSourceRef.current = null;
        setConnectSource(null);
        canvas.style.cursor = "default";
      }
    };

    canvas.addEventListener("mousedown", onDown);
    canvas.addEventListener("contextmenu", onContextMenu);
    window.addEventListener("mousemove", onMove);
    window.addEventListener("mouseup", onUp);
    window.addEventListener("keydown", onKeyDown);
    return () => {
      canvas.removeEventListener("mousedown", onDown);
      canvas.removeEventListener("contextmenu", onContextMenu);
      window.removeEventListener("mousemove", onMove);
      window.removeEventListener("mouseup", onUp);
      window.removeEventListener("keydown", onKeyDown);
    };
  }, []); // Intentionally empty — drag uses only refs (simulationRef, nodesRef)

  return (
    <div className="relative w-full h-full" data-testid="neural-graph-container">
      <canvas
        ref={canvasRef}
        className="w-full h-full"
        onMouseMove={handleMouseMove}
        onClick={handleClick}
        data-testid="neural-graph-canvas"
      />

      {nodes.length === 0 && (
        <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
          <motion.div {...EMPTY_ANIM} className="text-center">
            <div className="text-6xl mb-6 opacity-20" style={{ filter: "drop-shadow(0 0 20px #06B6D4)" }}>◎</div>
            <p className="text-[#64748B] font-body text-sm tracking-widest uppercase">
              Neural cortex awaiting first thought
            </p>
            <p className="text-[#06B6D4] font-body text-xs mt-2 opacity-60">
              Feed a thought below to initialize the network
            </p>
          </motion.div>
        </div>
      )}

      <AnimatePresence>
        {tooltip && (
          <motion.div
            key="tooltip"
            {...TOOLTIP_ANIM}
            className="fixed pointer-events-none z-50 glass-panel rounded-lg px-3 py-2 max-w-[200px]"
            style={{ left: tooltip.x + 12, top: tooltip.y - 40 }}
          >
            <div className="text-xs text-[#CBD5E1] font-body">{tooltip.node.content}</div>
            <div className="flex gap-1 mt-1 flex-wrap">
              {(tooltip.node.concepts || []).slice(0, 3).map((c) => (
                <span key={c} className="text-[10px] text-[#06B6D4] border border-[#06B6D4]/30 px-1 rounded">{c}</span>
              ))}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {connectSource && (
          <motion.div
            key="connect-badge"
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            className="absolute top-3 left-1/2 -translate-x-1/2 glass-panel rounded-lg px-3 py-1.5 flex items-center gap-2 pointer-events-none z-10"
            style={{ borderColor: "#06B6D480" }}
          >
            <div className="w-1.5 h-1.5 rounded-full bg-[#06B6D4] animate-pulse" />
            <span className="text-[11px] font-body text-[#06B6D4]">
              Connecting from <span className="text-[#F8FAFC]">{connectSource.content?.slice(0, 20)}…</span>
            </span>
            <span className="text-[10px] text-[#475569]">click target · ESC to cancel</span>
          </motion.div>
        )}
      </AnimatePresence>

      <div className="absolute bottom-3 left-3 flex gap-3 pointer-events-none">
        {Object.entries(NODE_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center gap-1">
            <div className="w-2 h-2 rounded-full" style={{ background: color, boxShadow: `0 0 6px ${color}` }} />
            <span className="text-[10px] font-body" style={{ color: "#64748B" }}>{type}</span>
          </div>
        ))}
      </div>
    </div>
  );
};

export default NeuralGraph;
