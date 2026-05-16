import { useState, useCallback, useEffect, useRef } from "react";

const BACKEND = process.env.REACT_APP_BACKEND_URL;

const devLog = (msg, err) => {
  if (process.env.NODE_ENV === "development") console.error(msg, err);
};

export function useGraphData() {
  const [nodes, setNodes] = useState([]);
  const [links, setLinks] = useState([]);
  const [stats, setStats] = useState({ total_thoughts: 0, total_connections: 0, brain_coherence: 0 });
  const [timelineEntries, setTimelineEntries] = useState([]);
  const [status, setStatus] = useState("ONLINE");
  const pollingRef = useRef(null);

  const fetchGraph = useCallback(async () => {
    try {
      const res = await fetch(`${BACKEND}/api/graph`);
      if (res.ok) {
        const { nodes: n, links: l } = await res.json();
        setNodes(n);
        setLinks(l);
      }
    } catch (err) {
      devLog("fetchGraph error:", err);
      setStatus("DEGRADED");
    }
  }, []); // BACKEND is a stable module-level constant

  const fetchStats = useCallback(async () => {
    try {
      const res = await fetch(`${BACKEND}/api/stats`);
      if (res.ok) setStats(await res.json());
    } catch (err) {
      devLog("fetchStats error:", err);
    }
  }, []);

  const fetchTimeline = useCallback(async () => {
    try {
      const res = await fetch(`${BACKEND}/api/timeline`);
      if (res.ok) {
        const { entries } = await res.json();
        setTimelineEntries(entries);
      }
    } catch (err) {
      devLog("fetchTimeline error:", err);
    }
  }, []);

  const refreshAll = useCallback(() => {
    fetchGraph();
    fetchStats();
    fetchTimeline();
  }, [fetchGraph, fetchStats, fetchTimeline]);

  useEffect(() => {
    refreshAll();
    pollingRef.current = setInterval(refreshAll, 8000);
    return () => clearInterval(pollingRef.current);
  }, [refreshAll]);

  return {
    nodes, links, stats, timelineEntries, status,
    fetchGraph, fetchStats, fetchTimeline, refreshAll,
  };
}
