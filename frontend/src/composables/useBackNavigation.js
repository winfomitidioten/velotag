// Zentrale "Zurück"-Logik, gemeinsam genutzt vom Zurück-Button im AppHeader
// und der Edge-Swipe-Geste (useSwipeBack.js) - beide sollen exakt gleich
// navigieren.
export function goBack(router, route) {
  const backTo = route.meta.backTo;
  // backTo kann auch eine Funktion sein, wenn das Ziel von Routen-Params abhängt
  // (z.B. zurück zur Gruppe, aus der die Bearbeiten-Seite geöffnet wurde).
  router.push((typeof backTo === 'function' ? backTo(route) : backTo) ?? '/map');
}
