// Farbverlauf für die Leistungs-Ansicht: Blau (locker) -> Grün/Gelb -> Orange -> Dunkelrot (max. Belastung)
// Rot steht immer für hohe Anstrengung/Geschwindigkeit, unabhängig von der gewählten Metrik.
const COLOR_STOPS = [
  { stop: 0.0, color: [33, 102, 172] },   // Blau - locker
  { stop: 0.35, color: [103, 169, 130] }, // Grün
  { stop: 0.6, color: [230, 195, 55] },   // Gelb
  { stop: 0.8, color: [230, 130, 40] },   // Orange
  { stop: 1.0, color: [178, 24, 24] },    // Dunkelrot - maximale Belastung
]

// Für Tempo speziell: ab dieser Geschwindigkeit wird Lila statt Dunkelrot verwendet, um sehr
// hohe/ungewöhnliche Abschnitte optisch von "nur schnell" abzuheben (unabhängig vom min/max der
// aktuellen Ansicht, da km/h eine absolute, metrik-eigene Bedeutung hat).
const TEMPO_EXTREME_KMH = 90
const EXTREME_COLOR = [147, 51, 234] // Lila

function lerp(a, b, t) {
  return a + (b - a) * t
}

// value auf [0,1] normalisieren und in eine Farbe aus COLOR_STOPS interpolieren
export function intensityColor(value, minValue, maxValue, metric) {
  if (metric === 'tempo' && value != null && value >= TEMPO_EXTREME_KMH) {
    return `rgb(${EXTREME_COLOR.join(',')})`
  }

  if (value == null || minValue == null || maxValue == null || maxValue === minValue) {
    return `rgb(${COLOR_STOPS[0].color.join(',')})`
  }

  const t = Math.min(1, Math.max(0, (value - minValue) / (maxValue - minValue)))

  let lower = COLOR_STOPS[0]
  let upper = COLOR_STOPS[COLOR_STOPS.length - 1]
  for (let i = 0; i < COLOR_STOPS.length - 1; i++) {
    if (t >= COLOR_STOPS[i].stop && t <= COLOR_STOPS[i + 1].stop) {
      lower = COLOR_STOPS[i]
      upper = COLOR_STOPS[i + 1]
      break
    }
  }

  const span = upper.stop - lower.stop
  const localT = span === 0 ? 0 : (t - lower.stop) / span

  const r = Math.round(lerp(lower.color[0], upper.color[0], localT))
  const g = Math.round(lerp(lower.color[1], upper.color[1], localT))
  const b = Math.round(lerp(lower.color[2], upper.color[2], localT))

  return `rgb(${r},${g},${b})`
}

// CSS-Gradient-String für die Legende (gleiche Stops wie oben). Bei Tempo mit min/max wird die
// Lila-Stufe ab TEMPO_EXTREME_KMH proportional mit eingezeichnet, analog zu intensityColor().
export function intensityGradientCss(metric, minValue, maxValue) {
  const baseStops = COLOR_STOPS.map(s => `rgb(${s.color.join(',')}) ${s.stop * 100}%`).join(', ')

  if (metric !== 'tempo' || minValue == null || maxValue == null || maxValue <= minValue || maxValue < TEMPO_EXTREME_KMH) {
    return `linear-gradient(90deg, ${baseStops})`
  }

  const extremePct = Math.min(100, Math.max(0, ((TEMPO_EXTREME_KMH - minValue) / (maxValue - minValue)) * 100))
  const scaledStops = COLOR_STOPS.map(s => `rgb(${s.color.join(',')}) ${(s.stop * extremePct).toFixed(1)}%`).join(', ')
  const purpleRgb = `rgb(${EXTREME_COLOR.join(',')})`
  return `linear-gradient(90deg, ${scaledStops}, ${purpleRgb} ${extremePct.toFixed(1)}%, ${purpleRgb} 100%)`
}

export const METRIC_UNITS = {
  puls: 'bpm',
  tempo: 'km/h',
  watt: 'W',
}
