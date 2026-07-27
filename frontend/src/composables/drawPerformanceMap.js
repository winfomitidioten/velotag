import api from '@/api/api'
import L from 'leaflet'
import { intensityColor } from '@/utils/intensityColor'
import { clearUserMap } from '@/composables/drawUserMap.js'
import { startDraw, isStaleDraw } from '@/composables/mapDrawGeneration.js'

let currentPerformanceLayer = null

// Backend berechnet Puls/Tempo/Watt in einem Rutsch (siehe RoutePerformanceView) - das Ergebnis
// wird hier zwischengespeichert (nur im Arbeitsspeicher, nicht persistent), damit ein Wechsel
// zwischen den drei Metriken keinen erneuten Request/keine erneute Berechnung braucht.
let cachedData = null
let cachedPromise = null

async function fetchPerformanceData(forceRefresh) {
  if (forceRefresh) {
    cachedData = null
    cachedPromise = null
  }
  if (cachedData) return cachedData
  if (!cachedPromise) {
    cachedPromise = api.get('routes/performance/').then(response => {
      cachedData = response.data
      return cachedData
    }).catch(err => {
      cachedPromise = null
      throw err
    })
  }
  return cachedPromise
}

// Verwirft den zwischengespeicherten Stand, z.B. nachdem eine neue Route hochgeladen wurde
// (Strava-Import, GPX-Upload) - der nächste Aufruf holt dann wieder frische Daten vom Server.
export function invalidatePerformanceCache() {
  cachedData = null
  cachedPromise = null
}

// Zeichnet die räumlich gemittelte Puls-/Tempo-/Watt-Intensität des eingeloggten Users auf der Karte.
// Gibt {minValue, maxValue, hasData} zurück, damit Karte.vue die Legende befüllen kann.
export async function drawPerformanceMap(map, metric, { forceRefresh = false } = {}) {
  const myGeneration = startDraw() // Erkennt veraltete Aufrufe, falls währenddessen umgeschaltet wird
  clearUserMap(map) // Solo-/Group-Ansicht ausblenden, falls gerade aktiv

  const data = await fetchPerformanceData(forceRefresh)

  // Veraltete Anfrage: Während des Fetches wurde bereits eine neuere Zeichenanfrage gestartet
  // (z.B. schnelles Umschalten Solo/Group/Leistung) - nichts mehr an der Karte ändern.
  if (isStaleDraw(myGeneration)) return { minValue: null, maxValue: null, hasData: true }

  if (currentPerformanceLayer) {
    map.removeLayer(currentPerformanceLayer)
    currentPerformanceLayer = null
  }
  currentPerformanceLayer = L.featureGroup([], { renderer: L.canvas() }).addTo(map)

  const { min_value: minValue, max_value: maxValue } = data.metrics[metric]
  let hasData = false

  data.segments.forEach(segment => {
    const metricData = segment[metric]
    if (!metricData) return // dieses Segment hat für die gewählte Metrik keinen gültigen Wert
    hasData = true

    const color = intensityColor(metricData.value, minValue, maxValue, metric)
    const polyline = L.polyline(segment.coordinates, {
      color,
      weight: 5,
      opacity: 0.9,
      lineCap: 'round',
      lineJoin: 'round'
    })
    polyline.bindPopup(`${metricData.value} (${metricData.count} Fahrt${metricData.count === 1 ? '' : 'en'})`)
    currentPerformanceLayer.addLayer(polyline)
  })

  return { minValue, maxValue, hasData }
}

export function clearPerformanceMap(map) {
  if (currentPerformanceLayer) {
    map.removeLayer(currentPerformanceLayer)
    currentPerformanceLayer = null
  }
}
