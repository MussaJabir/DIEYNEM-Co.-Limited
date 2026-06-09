/** @type {import('tailwindcss').Config} */
// Design tokens per build scope §5. Tailwind's default `slate` and `amber`
// already match our neutral/accent values, so we only add `navy`, `volt`, and
// semantic aliases here.
module.exports = {
  content: [
    "./templates/**/*.html",
    "./apps/**/templates/**/*.html",
    "./apps/**/*.py",
  ],
  theme: {
    extend: {
      colors: {
        navy: {
          50: "#EEF4FB",
          100: "#DCE8F5",
          300: "#8FB3DC",
          400: "#5089C6",
          500: "#2766AE",
          600: "#1E4E86",
          700: "#173A66",
          800: "#12294A",
          900: "#0C1B30",
          950: "#08111E",
        },
        volt: { 400: "#FFD400" },
        ok: "#16A34A",
        warn: "#D97706",
        danger: "#DC2626",
        info: "#2563EB",
      },
      fontFamily: {
        sans: ["Inter", "ui-sans-serif", "system-ui", "sans-serif"],
        heading: ["Manrope", "Inter", "ui-sans-serif", "sans-serif"],
        mono: ['"IBM Plex Mono"', "ui-monospace", "monospace"],
      },
    },
  },
  plugins: [],
};
