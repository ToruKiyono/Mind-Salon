import type { Config } from "tailwindcss";

const config: Config = {
  content: ["./app/**/*.{ts,tsx}", "./components/**/*.{ts,tsx}"],
  theme: {
    extend: {
      colors: {
        salon: {
          bg: "rgb(var(--salon-bg) / <alpha-value>)",
          panel: "rgb(var(--salon-panel) / <alpha-value>)",
          soft: "rgb(var(--salon-soft) / <alpha-value>)",
          line: "rgb(var(--salon-line) / <alpha-value>)",
          text: "rgb(var(--salon-text) / <alpha-value>)",
          sub: "rgb(var(--salon-sub) / <alpha-value>)",
          primary: "rgb(var(--salon-primary) / <alpha-value>)",
          accent: "rgb(var(--salon-accent) / <alpha-value>)",
          success: "rgb(var(--salon-success) / <alpha-value>)",
          warn: "rgb(var(--salon-warn) / <alpha-value>)",
          danger: "rgb(var(--salon-danger) / <alpha-value>)",
          glow: "rgb(var(--salon-glow) / <alpha-value>)"
        }
      },
      borderRadius: {
        xs2: "var(--radius-xs)",
        sm2: "var(--radius-sm)",
        md2: "var(--radius-md)",
        lg2: "var(--radius-lg)",
        xl2: "var(--radius-xl)"
      },
      boxShadow: {
        soft: "var(--shadow-soft)",
        float: "var(--shadow-float)",
        glow: "var(--shadow-glow)"
      },
      fontFamily: {
        display: "var(--font-display)",
        body: "var(--font-body)"
      },
      spacing: {
        4.5: "1.125rem",
        18: "4.5rem",
        22: "5.5rem",
        30: "7.5rem"
      },
      transitionDuration: {
        fast: "var(--motion-fast)",
        base: "var(--motion-base)",
        slow: "var(--motion-slow)"
      }
    }
  },
  plugins: []
};

export default config;
