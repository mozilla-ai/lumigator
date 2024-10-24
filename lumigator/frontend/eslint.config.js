import globals from "globals";
import pluginVue from "eslint-plugin-vue";


export default [
  {files: ["**/*.{js,mjs,cjs,vue}"]},
  {languageOptions: { globals: globals.browser }},
  ...pluginVue.configs["flat/essential"],
];