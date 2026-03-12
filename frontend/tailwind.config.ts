import type { Config } from "tailwindcss";

export default {
  content: ["./index.html", "./src/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        ink: "#16110f",
        sand: "#f5efe8",
        ember: "#d97a3a",
        clay: "#b9562d",
        tide: "#1f6c63",
        mist: "#edf2ef",
      },
      boxShadow: {
        panel: "0 20px 60px rgba(22, 17, 15, 0.12)",
      },
      borderRadius: {
        "4xl": "2rem",
      },
      fontFamily: {
        display: ["'Space Grotesk'", "sans-serif"],
        body: ["'Manrope'", "sans-serif"],
      },
      backgroundImage: {
        grid: "linear-gradient(rgba(22,17,15,0.06) 1px, transparent 1px), linear-gradient(90deg, rgba(22,17,15,0.06) 1px, transparent 1px)",
      },
    },
  },
  plugins: [],
} satisfies Config;
