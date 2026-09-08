/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        // Institutional palette — trust, clarity, authority
        brand: {
          50: "#f0f4ff",
          100: "#e0e9ff",
          200: "#c7d7fd",
          300: "#a5bcfb",
          400: "#8098f9",
          500: "#6172f3",
          600: "#444ce7",
          700: "#3538cd",
          800: "#2d31a6",
          900: "#2d3282",
          950: "#1f2261",
        },
        slate: {
          850: "#172033",
        },
        // Evidence confidence levels
        confidence: {
          high: "#16a34a",
          moderate: "#ca8a04",
          limited: "#ea580c",
          insufficient: "#dc2626",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
        mono: ["JetBrains Mono", "Menlo", "monospace"],
      },
    },
  },
  plugins: [],
};
