module.exports = {
  mode: "jit",
  content: ["./src/**/*.{js,jsx,ts,tsx}"],
  theme: {
    extend: {
      backgroundImage: {
        "split-white-black":
          "linear-gradient(to bottom, #111827 60% , white 40%);",
      },
    },
  },
  plugins: [],
};
