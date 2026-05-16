import { useEffect, useRef } from "react"; // eslint-disable-line no-unused-vars

const JarvisVoice = ({ audioB64, onEnd }) => {
  const audioRef = useRef(null);

  useEffect(() => {
    if (!audioB64) return;
    const audio = new Audio(`data:audio/mp3;base64,${audioB64}`);
    audioRef.current = audio;
    audio.play().catch(console.error);
    audio.onended = () => {
      if (onEnd) onEnd();
    };
    return () => {
      if (audioRef.current) {
        audioRef.current.pause();
        audioRef.current = null;
      }
    };
  }, [audioB64, onEnd]);

  return null;
};

export default JarvisVoice;
