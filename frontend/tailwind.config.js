module.exports = {
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      colors: {
        void: "#030305",
        "void-secondary": "#0A0A0F",
        "void-tertiary": "#12121A",
        "neon-cyan": "#06B6D4",
        "neon-blue": "#3B82F6",
        "neon-purple": "#8B5CF6",
        "neon-amber": "#F59E0B",
        "neon-green": "#10B981",
      },
      fontFamily: {
        heading: ["Unbounded", "sans-serif"],
        body: ["JetBrains Mono", "monospace"],
        accent: ["Orbitron", "sans-serif"],
      },
      animation: {
        "pulse-glow": "pulseGlow 2s ease-in-out infinite",
        "scan-line": "scanLine 8s linear infinite",
        "float": "float 6s ease-in-out infinite",
        "synapse": "synapseFlash 0.3s ease-out",
      },
      keyframes: {
        pulseGlow: {
          "0%, 100%": { opacity: "0.6" },
          "50%": { opacity: "1" },
        },
        scanLine: {
          "0%": { transform: "translateY(-100%)" },
          "100%": { transform: "translateY(100vh)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-10px)" },
        },
        synapseFlash: {
          "0%": { opacity: "1", transform: "scale(1.5)" },
          "100%": { opacity: "0", transform: "scale(1)" },
        },
      },
      backdropBlur: {
        xl: "24px",
      },
    },
  },
  plugins: [],
};
