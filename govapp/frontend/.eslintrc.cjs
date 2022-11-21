module.exports = {
    env: {
        node: true,
    },
    globals: {
        defineProps: 'readonly',
        defineEmits: 'readonly',
        withDefaults: 'readonly',
        $ref: 'readonly',
        $computed: 'readonly',
        $shallowRef: 'readonly',
        $customRef: 'readonly',
        $toRef: 'readonly',
        $: 'readonly',
        $$: 'readonly'
    },
    extends: [
        'eslint:recommended',
        'plugin:vue/vue3-essential',
        'plugin:@typescript-eslint/recommended',
        '@vue/eslint-config-typescript/recommended',
    ],
    rules: {
        'object-curly-spacing': ['error', 'always'],
        'object-curly-newline': [
            'error', {
                'ImportDeclaration': 'never',
                'ExportDeclaration': 'never'
            }
        ],
        "vue/script-indent": [
            "error",
            2,
            { "baseIndent": 1 }
        ],
        "space-before-function-paren": ["error", "always"],
        "comma-dangle": ["error", "never"],
        "quotes": ["error", "double"],
        "semi": ["error", "always"]
    },
    // Stop eslint from linting vue files using the indent rules for ts/js files.
    overrides : [
        {
            files: ["*.vue"],
            rules: {
                indent: "off"
            }
        }
    ]
};
