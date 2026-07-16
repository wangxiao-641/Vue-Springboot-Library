import { createStore } from 'vuex'
const { THEMES, readTheme, applyTheme } = require('../theme/themeState.cjs')
export { THEMES }
const storage = typeof window !== 'undefined' ? window.localStorage : null
const root = typeof document !== 'undefined' ? document.documentElement : null
const initialTheme = applyTheme(storage, root, readTheme(storage))

export default createStore({
  state: {
    theme: initialTheme,
  },
  mutations: {
    setTheme(state, value) {
      state.theme = applyTheme(storage, root, value)
    },
  },
  actions: {
  },
  modules: {
  }
})
