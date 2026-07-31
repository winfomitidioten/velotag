// Zentrale "Zurück"-Logik, gemeinsam genutzt vom Zurück-Button im AppHeader
// und der Edge-Swipe-Geste (useSwipeBack.js) - beide sollen exakt gleich
// navigieren.
export function goBack(router, route) {
  router.push(route.meta.backTo ?? '/map');
}
