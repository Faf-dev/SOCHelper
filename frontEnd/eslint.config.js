// eslint.config.js
export default [
  {
    files: ["**/*.js"],
    languageOptions: {
      ecmaVersion: 2022,
      sourceType: "module",
    },
    rules: {
      semi: "error",
      quotes: ["error", "double"],
      // Ajoute d'autres règles ici si besoin
    },
  },
];