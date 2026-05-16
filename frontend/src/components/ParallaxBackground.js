import { useEffect, useRef } from "react";

const STAR_LAYERS = [
  { count: 80, speed: 0.008, size: 1, opacity: 0.4 },
  { count: 40, speed: 0.016, size: 1.5, opacity: 0.6 },
  { count: 20, speed: 0.028, size: 2, opacity: 0.8 },
];

const ParallaxBackground = () => {
  const canvasRef = useRef(null);
  const mouseRef = useRef({ x: 0, y: 0 });
  const starsRef = useRef([]);
  const frameRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    const ctx = canvas.getContext("2d");

    const initStars = () => {
      starsRef.current = [];
      STAR_LAYERS.forEach((layer, li) => {
        for (let i = 0; i < layer.count; i++) {
          starsRef.current.push({
            x: Math.random() * canvas.width,
            y: Math.random() * canvas.height,
            baseX: Math.random() * canvas.width,
            baseY: Math.random() * canvas.height,
            size: layer.size + Math.random() * 0.5,
            opacity: layer.opacity * (0.5 + Math.random() * 0.5),
            speed: layer.speed,
            layer: li,
            twinkle: Math.random() * Math.PI * 2,
            twinkleSpeed: 0.02 + Math.random() * 0.02,
          });
        }
      });
    };

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initStars();
    };

    const draw = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const bg = ctx.createRadialGradient(
        canvas.width * 0.5, canvas.height * 0.3, 0,
        canvas.width * 0.5, canvas.height * 0.5, canvas.width * 0.8
      );
      bg.addColorStop(0, "#0D0D1A");
      bg.addColorStop(0.4, "#080810");
      bg.addColorStop(1, "#030305");
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const neb = ctx.createRadialGradient(canvas.width * 0.75, canvas.height * 0.25, 0, canvas.width * 0.75, canvas.height * 0.25, canvas.width * 0.35);
      neb.addColorStop(0, "rgba(59, 130, 246, 0.04)");
      neb.addColorStop(0.5, "rgba(139, 92, 246, 0.02)");
      neb.addColorStop(1, "transparent");
      ctx.fillStyle = neb;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const neb2 = ctx.createRadialGradient(canvas.width * 0.2, canvas.height * 0.7, 0, canvas.width * 0.2, canvas.height * 0.7, canvas.width * 0.3);
      neb2.addColorStop(0, "rgba(6, 182, 212, 0.03)");
      neb2.addColorStop(1, "transparent");
      ctx.fillStyle = neb2;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const mx = (mouseRef.current.x / window.innerWidth - 0.5) * 2;
      const my = (mouseRef.current.y / window.innerHeight - 0.5) * 2;

      starsRef.current.forEach((star) => {
        star.twinkle += star.twinkleSpeed;
        const twinkleFactor = 0.6 + Math.sin(star.twinkle) * 0.4;
        const depth = (star.layer + 1) * 18;
        const sx = ((star.baseX + mx * depth) % canvas.width + canvas.width) % canvas.width;
        const sy = ((star.baseY + my * depth) % canvas.height + canvas.height) % canvas.height;

        ctx.beginPath();
        ctx.arc(sx, sy, star.size, 0, Math.PI * 2);
        const isCyan = Math.floor(star.baseX * 7 + star.baseY * 3) % 12 === 0;
        ctx.fillStyle = isCyan
          ? `rgba(6, 182, 212, ${star.opacity * twinkleFactor})`
          : `rgba(220, 230, 255, ${star.opacity * twinkleFactor})`;
        if (star.size > 1.5) {
          ctx.shadowBlur = 4;
          ctx.shadowColor = isCyan ? "#06B6D4" : "#ffffff";
        }
        ctx.fill();
        ctx.shadowBlur = 0;
      });

      frameRef.current = requestAnimationFrame(draw);
    };

    // Store handler ref so we can remove it on cleanup
    const handleMouseMove = (e) => { mouseRef.current = { x: e.clientX, y: e.clientY }; };

    window.addEventListener("resize", resize);
    window.addEventListener("mousemove", handleMouseMove);

    resize();
    frameRef.current = requestAnimationFrame(draw);

    return () => {
      cancelAnimationFrame(frameRef.current);
      window.removeEventListener("resize", resize);
      window.removeEventListener("mousemove", handleMouseMove); // Fixed: was missing before
    };
  }, []); // Intentionally empty — all state accessed via refs; runs once on mount

  return (
    <canvas
      ref={canvasRef}
      className="fixed inset-0 pointer-events-none"
      style={{ zIndex: 0 }}
      data-testid="parallax-background"
    />
  );
};

export default ParallaxBackground;
