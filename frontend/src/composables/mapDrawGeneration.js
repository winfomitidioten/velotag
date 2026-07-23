// Gemeinsamer Zähler für drawUserMap.js und drawPerformanceMap.js: Da beide Funktionen async
// sind (Backend-Fetch dazwischen), kann eine ältere Zeichenanfrage erst NACH einer neueren
// fertig werden (z.B. schnelles Umschalten Solo -> Puls -> Gruppe). Ohne diese Sperre würde die
// alte, verspätete Anfrage ihre Layer trotzdem noch auf die Karte legen ("stapelt sich").
let currentGeneration = 0

export function startDraw() {
  currentGeneration += 1
  return currentGeneration
}

export function isStaleDraw(generation) {
  return generation !== currentGeneration
}
