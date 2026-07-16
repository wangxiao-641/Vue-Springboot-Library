const assert = require('assert')
const { DEFAULT_THEME, readTheme, applyTheme } = require('../src/theme/themeState.cjs')

function storage(initial) {
  const values = new Map(Object.entries(initial || {}))
  return { getItem: (key) => values.has(key) ? values.get(key) : null, setItem: (key, value) => values.set(key, value) }
}

assert.strictEqual(readTheme(storage()), DEFAULT_THEME, 'empty storage defaults to academy')
for (const theme of ['atlas', 'academy', 'command']) {
  const target = storage()
  const root = { dataset: {} }
  assert.strictEqual(applyTheme(target, root, theme), theme, `${theme} is accepted`)
  assert.strictEqual(root.dataset.theme, theme, `${theme} applies immediately`)
  assert.strictEqual(readTheme(target), theme, `${theme} persists`)
}
assert.strictEqual(readTheme(storage({ 'library-theme': 'classic' })), DEFAULT_THEME, 'legacy value falls back')
assert.strictEqual(applyTheme(storage(), { dataset: {} }, 'unknown'), DEFAULT_THEME, 'illegal switch falls back')
console.log('Theme state verification: PASS')
