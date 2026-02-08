const js = require('@eslint/js')
const react = require('eslint-plugin-react')
const reactHooks = require('eslint-plugin-react-hooks')
const tseslint = require('typescript-eslint')

module.exports = tseslint.config(
  js.configs.recommended,
  ...tseslint.configs.recommended,
  {
    ignores: ['dist/**', 'node_modules/**']
  },
  {
    files: ['**/*.{ts,tsx}'],
    plugins: {
      react,
      'react-hooks': reactHooks
    },
    settings: {
      react: {
        version: 'detect'
      }
    },
    rules: {
      ...reactHooks.configs.recommended.rules
    }
  },
  {
    files: ['**/*.js', '**/*.cjs'],
    languageOptions: {
      sourceType: 'script',
      globals: {
        module: 'readonly',
        require: 'readonly',
        __dirname: 'readonly',
        __filename: 'readonly',
        process: 'readonly'
      }
    },
    rules: {
      '@typescript-eslint/no-require-imports': 'off'
    }
  }
)
