import js from '@eslint/js';
import prettier from 'eslint-config-prettier';
import { defineConfig, globalIgnores } from 'eslint/config';
import reactHooks from 'eslint-plugin-react-hooks';
import reactRefresh from 'eslint-plugin-react-refresh';
import globals from 'globals';
import tseslint from 'typescript-eslint';

const RELATIVE_URLS =
  'Use a relative URL: Home Assistant ingress serves the app under a dynamic base path.';

export default defineConfig([
  globalIgnores(['dist', 'src/api/generated', 'test-results', 'playwright-report']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      js.configs.recommended,
      tseslint.configs.strictTypeChecked,
      tseslint.configs.stylisticTypeChecked,
      reactHooks.configs.flat['recommended-latest'],
      reactRefresh.configs.vite,
    ],
    languageOptions: {
      globals: globals.browser,
      parserOptions: { projectService: true, tsconfigRootDir: import.meta.dirname },
    },
    rules: {
      // Guard the ingress invariant: never hardcode a URL that starts with "/".
      'no-restricted-syntax': [
        'error',
        {
          selector: "CallExpression[callee.name='fetch'] > Literal:first-child[value=/^\\//]",
          message: RELATIVE_URLS,
        },
        {
          selector: 'JSXAttribute[name.name=/^(href|src|action)$/] > Literal[value=/^\\//]',
          message: RELATIVE_URLS,
        },
      ],
      '@typescript-eslint/restrict-template-expressions': ['error', { allowNumber: true }],
      // Allows `onClick={() => void save()}` for fire-and-forget handlers.
      '@typescript-eslint/no-confusing-void-expression': ['error', { ignoreVoidOperator: true }],
    },
  },
  {
    files: ['**/*.{js,mjs}'],
    extends: [js.configs.recommended],
    languageOptions: { globals: globals.node },
  },
  prettier,
]);
