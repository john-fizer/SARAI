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

    const resize = () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      initStars();
    };

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

    const draw = (ts) => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      // Deep space background
      const bg = ctx.createRadialGradient(
        canvas.width * 0.5, canvas.height * 0.3, 0,
        canvas.width * 0.5, canvas.height * 0.5, canvas.width * 0.8
      );
      bg.addColorStop(0, "#0D0D1A");
      bg.addColorStop(0.4, "#080810");
      bg.addColorStop(1, "#030305");
      ctx.fillStyle = bg;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Nebula hints
      const neb = ctx.createRadialGradient(
        canvas.width * 0.75, canvas.height * 0.25, 0,
        canvas.width * 0.75, canvas.height * 0.25, canvas.width * 0.35
      );
      neb.addColorStop(0, "rgba(59, 130, 246, 0.04)");
      neb.addColorStop(0.5, "rgba(139, 92, 246, 0.02)");
      neb.addColorStop(1, "transparent");
      ctx.fillStyle = neb;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      const neb2 = ctx.createRadialGradient(
        canvas.width * 0.2, canvas.height * 0.7, 0,
        canvas.width * 0.2, canvas.height * 0.7, canvas.width * 0.3
      );
      neb2.addColorStop(0, "rgba(6, 182, 212, 0.03)");
      neb2.addColorStop(1, "transparent");
      ctx.fillStyle = neb2;
      ctx.fillRect(0, 0, canvas.width, canvas.height);

      // Parallax mouse offset
      const mx = (mouseRef.current.x / window.innerWidth - 0.5) * 2;
      const my = (mouseRef.current.y / window.innerHeight - 0.5) * 2;

      // Draw stars
      starsRef.current.forEach((star) => {
        star.twinkle += star.twinkleSpeed;
        const twinkleFactor = 0.6 + Math.sin(star.twinkle) * 0.4;

        // Parallax offset
        const depth = (star.layer + 1) * 18;
        const ox = mx * depth;
        const oy = my * depth;

        const sx = ((star.baseX + ox) % canvas.width + canvas.width) % canvas.width;
        const sy = ((star.baseY + oy) % canvas.height + canvas.height) % canvas.height;

        ctx.beginPath();
        ctx.arc(sx, sy, star.size, 0, Math.PI * 2);

        // Occasional bright stars get a cyan tint
        const isCyan = Math.floor(star.baseX * 7 + star.baseY * 3) % 12 === 0;
        const starColor = isCyan ? `rgba(6, 182, 212, ${star.opacity * twinkleFactor})` : `rgba(220, 230, 255, ${star.opacity * twinkleFactor})`;

        ctx.fillStyle = starColor;
        if (star.size > 1.5) {
          ctx.shadowBlur = 4;
          ctx.shadowColor = isCyan ? "#06B6D4" : "#ffffff";
        }
        ctx.fill();
        ctx.shadowBlur = 0;
      });

      frameRef.current = requestAnimationFrame(draw);
    };

    window.addEventListener("resize", resize);
    window.addEventListener("mousemove", (e) => {
      mouseRef.current = { x: e.clientX, y: e.clientY };
    });

    resize();
    frameRef.current = requestAnimationFrame(draw);

    return () => {
      cancelAnimationFrame(frameRef.current);
      window.removeEventListener("resize", resize);
    };
  }, []);

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
