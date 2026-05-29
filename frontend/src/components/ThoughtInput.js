import React, { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Zap, Mic, MicOff, Loader } from "lucide-react";

const BACKEND = process.env.REACT_APP_BACKEND_URL;
const API_HEADERS = { "X-API-Key": process.env.REACT_APP_API_KEY || "" };
const devLog = (msg, err) => { if (process.env.NODE_ENV === "development") console.error(msg, err); };

// Stable animation configs (module-level prevents inline object re-creation)
const PANEL_ENTRANCE = { initial: { opacity: 0, y: 40 }, animate: { opacity: 1, y: 0 }, transition: { duration: 0.6, delay: 0.3 } };
const REC_STATUS_ANIM = { initial: { opacity: 0, y: 5 }, animate: { opacity: 1, y: 0 }, exit: { opacity: 0 } };
const REC_INDICATOR_ANIM = { initial: { opacity: 0 }, animate: { opacity: 1 }, exit: { opacity: 0 } };
const REC_DOT_ANIM = { animate: { scale: [1, 1.3, 1], opacity: [1, 0.5, 1] }, transition: { duration: 0.8, repeat: Infinity } };
const MIC_HOVER = { scale: 1.1 };
const MIC_TAP = { scale: 0.95 };
const SUBMIT_HOVER = { scale: 1.05 };
const SUBMIT_TAP = { scale: 0.95 };

const ThoughtInput = ({ onThoughtAdded, isProcessing, setIsProcessing }) => {
  const [value, setValue] = useState("");
  const [recording, setRecording] = useState(false);
  const [recStatus, setRecStatus] = useState("");
  const mediaRecRef = useRef(null);
  const chunksRef = useRef([]);
  const textareaRef = useRef(null);

  const handleSubmit = async () => {
    if (!value.trim() || isProcessing) return;
    setIsProcessing(true);
    try {
      const resp = await fetch(`${BACKEND}/api/thoughts`, {
        method: "POST",
        headers: { "Content-Type": "application/json", ...API_HEADERS },
        body: JSON.stringify({ content: value.trim() }),
      });
      if (resp.ok) {
        const data = await resp.json();
        onThoughtAdded(data);
        setValue("");
      }
    } catch (err) {
      devLog("submitThought error:", err);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const startRecording = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const rec = new MediaRecorder(stream, { mimeType: "audio/webm" });
      chunksRef.current = [];
      rec.ondataavailable = (e) => chunksRef.current.push(e.data);
      rec.onstop = async () => {
        stream.getTracks().forEach((t) => t.stop());
        const blob = new Blob(chunksRef.current, { type: "audio/webm" });
        const form = new FormData();
        form.append("file", blob, "voice.webm");
        setRecStatus("Transcribing...");
        try {
          const res = await fetch(`${BACKEND}/api/stt`, { method: "POST", headers: API_HEADERS, body: form });
          if (res.ok) {
            const { text } = await res.json();
            setValue((prev) => prev ? prev + " " + text : text);
          }
        } catch (err) {
          devLog("STT error:", err);
        } finally {
          setRecStatus("");
        }
      };
      rec.start();
      mediaRecRef.current = rec;
      setRecording(true);
    } catch (err) {
      devLog("Mic error:", err);
      setRecStatus("Mic access denied");
      setTimeout(() => setRecStatus(""), 2000);
    }
  };

  const stopRecording = () => {
    if (mediaRecRef.current && mediaRecRef.current.state !== "inactive") {
      mediaRecRef.current.stop();
    }
    setRecording(false);
  };

  const toggleRecording = () => (recording ? stopRecording() : startRecording());

  // Auto-resize textarea — textareaRef is a stable ref, safe to omit from deps
  useEffect(() => {
    const el = textareaRef.current;
    if (el) {
      el.style.height = "auto";
      el.style.height = Math.min(el.scrollHeight, 120) + "px";
    }
  }, [value]); // eslint-disable-line react-hooks/exhaustive-deps

  return (
    <motion.div {...PANEL_ENTRANCE} className="w-full" data-testid="thought-input-panel">
      <AnimatePresence>
        {recStatus && (
          <motion.div {...REC_STATUS_ANIM} className="text-center text-xs text-[#06B6D4] font-body mb-2 tracking-widest">
            {recStatus}
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence>
        {recording && (
          <motion.div {...REC_INDICATOR_ANIM} className="flex items-center gap-2 justify-center mb-2">
            <motion.div {...REC_DOT_ANIM} className="w-2 h-2 rounded-full bg-red-500" />
            <span className="text-xs text-red-400 font-body tracking-widest">RECORDING — SPEAK NOW</span>
          </motion.div>
        )}
      </AnimatePresence>

      <div
        className={`glass-panel rounded-2xl p-4 transition-all duration-300 ${isProcessing ? "border-[#3B82F6]/40" : "border-[#06B6D4]/20 hover:border-[#06B6D4]/40"}`}
        data-testid="thought-input-container"
      >
        <div className="flex items-end gap-3">
          <div className="text-[#06B6D4] font-accent text-sm pb-1 shrink-0 neon-text select-none">&gt;_</div>

          <textarea
            ref={textareaRef}
            data-testid="thought-textarea"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Feed a thought to the neural cortex... (Enter to transmit, Shift+Enter for newline)"
            disabled={isProcessing}
            rows={1}
            className="flex-1 bg-transparent text-[#F8FAFC] font-body text-sm placeholder-[#334155] resize-none outline-none leading-relaxed"
            style={{ minHeight: "28px", maxHeight: "120px" }}
          />

          <div className="flex items-center gap-2 shrink-0 pb-1">
            <motion.button
              whileHover={MIC_HOVER}
              whileTap={MIC_TAP}
              onClick={toggleRecording}
              disabled={isProcessing}
              data-testid="voice-input-btn"
              className={`p-2 rounded-lg transition-all duration-200 ${
                recording
                  ? "bg-red-500/20 text-red-400 border border-red-500/50"
                  : "text-[#64748B] hover:text-[#06B6D4] hover:bg-[#06B6D4]/10 border border-transparent"
              }`}
            >
              {recording ? <MicOff size={16} /> : <Mic size={16} />}
            </motion.button>

            <motion.button
              whileHover={SUBMIT_HOVER}
              whileTap={SUBMIT_TAP}
              onClick={handleSubmit}
              disabled={!value.trim() || isProcessing}
              data-testid="submit-thought-btn"
              className={`flex items-center gap-1.5 px-4 py-2 rounded-lg text-sm font-body font-medium transition-all duration-200 ${
                value.trim() && !isProcessing
                  ? "bg-[#06B6D4]/15 text-[#06B6D4] border border-[#06B6D4]/50 hover:bg-[#06B6D4]/25 hover:shadow-[0_0_20px_rgba(6,182,212,0.3)]"
                  : "text-[#334155] border border-[#1E293B] cursor-not-allowed"
              }`}
            >
              {isProcessing ? (
                <><Loader size={14} className="animate-spin" /><span>Processing</span></>
              ) : (
                <><Zap size={14} /><span>Transmit</span></>
              )}
            </motion.button>
          </div>
        </div>

        {isProcessing && (
          <div className="mt-3 h-0.5 rounded-full overflow-hidden">
            <div className="shimmer h-full w-full" />
          </div>
        )}
      </div>

      <div className="flex items-center justify-center gap-4 mt-2">
        {["idea", "question", "insight", "memory"].map((type) => (
          <button
            key={type}
            className="text-[10px] font-body text-[#334155] hover:text-[#64748B] tracking-widest uppercase transition-colors"
            data-testid={`type-hint-${type}`}
          >
            {type}
          </button>
        ))}
      </div>
    </motion.div>
  );
};

export default ThoughtInput;
