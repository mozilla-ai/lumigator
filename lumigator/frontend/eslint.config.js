import globals from "globals";
import pluginJs from "@eslint/js";
import pluginVue from "eslint-plugin-vue";

/** @type {import('eslint').Linter.Config[]} */
export default [
	{ files: ["**/*.{js,mjs,cjs,vue}"] },
	{ files: ["**/*.js"], languageOptions: { sourceType: "commonjs" } },
	{ languageOptions: { globals: globals.browser } },
	pluginJs.configs.recommended,
	...pluginVue.configs["flat/essential"],
	{
		files: ["src/**/*.{js,vue}"],
		rules: {
			"no-console": ["warn", { allow: ["warn", "error"] }],
			"no-debugger": "error",
			"eqeqeq": ["error", "always"],
			"curly": ["error", "all"],
			"no-unused-vars": ["error", { args: "none", ignoreRestSiblings: true }],
			"no-var": "error",
			"prefer-const": ["error", { destructuring: "all" }],
			"vue/multi-word-component-names": "error",
			"vue/no-v-html": "warn",
			"vue/attributes-order": ["error", {
				order: [
					"DEFINITION",
					"LIST_RENDERING",
					"CONDITIONALS",
					"RENDER_MODIFIERS",
					"GLOBAL",
					"UNIQUE",
					"SLOT",
					"TWO_WAY_BINDING",
					"OTHER_DIRECTIVES",
					"OTHER_ATTR",
					"EVENTS",
					"CONTENT"
				]
			}],
			"vue/component-tags-order": ["error", {
				order: ["template", "script", "style"]
			}],
			"vue/padding-line-between-blocks": ["error", "always"],
			"vue/no-unused-components": "error",
			"vue/no-multiple-template-root": "off",
			"vue/html-closing-bracket-newline": ["error", {
				singleline: "never",
				multiline: "always"
			}],
			"vue/max-len": ["error", {
				code: 100,
				template: 100,
				tabWidth: 2,
				ignoreComments: true,
				ignoreTrailingComments: true,
				ignorePattern: ".*(import|console).*"
			}]
		}
	}
];
