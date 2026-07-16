const THEMES = Object.freeze({
  atlas: { label: '馆藏运营台', short: 'Atlas' },
  academy: { label: '书院阅读风', short: 'Academy' },
  command: { label: '数字指挥舱', short: 'Command' }
})
const THEME_KEY = 'library-theme'
const DEFAULT_THEME = 'academy'

function normalizeTheme(value) {
  return Object.prototype.hasOwnProperty.call(THEMES, value) ? value : DEFAULT_THEME
}

function readTheme(storage) {
  return normalizeTheme(storage && storage.getItem(THEME_KEY))
}

function persistTheme(storage, value) {
  const theme = normalizeTheme(value)
  if (storage) storage.setItem(THEME_KEY, theme)
  return theme
}

function applyTheme(storage, root, value) {
  const theme = persistTheme(storage, value)
  if (root) root.dataset.theme = theme
  return theme
}

module.exports = { THEMES, THEME_KEY, DEFAULT_THEME, normalizeTheme, readTheme, persistTheme, applyTheme }
