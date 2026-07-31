<script setup>
import { computed } from 'vue'
import { decodePolyline } from '@/composables/polyline'

// Zeichnet den Umriss einer Route als SVG (kein Kartenhintergrund, keine eigene Leaflet-Instanz)
// Gedacht für die Vorschau Icons wäre pro Zeile eine echte Karte mit Tiles zu teuer (Netzwerk, Speicher, Rendering) 
const props = defineProps({
  polyline: { type: String, required: true }, // komprimierter Polyline-String (gleiches Format wie in drawUserMap.js)
  size: { type: Number, default: 48 },        // Breite/Höhe des SVG in px (quadratisch)
  padding: { type: Number, default: 4 }       // Innenabstand, damit die Linie nicht am Rand klebt/abgeschnitten wird
})

// computed statt einfacher Funktion: das Ergebnis wird gecacht und läuft nur neu,
// wenn sich polyline/size/padding wirklich ändern (z.B. andere Route in der Liste)
const pathData = computed(() => {
  const coords = decodePolyline(props.polyline) // [[lat, lng], [lat, lng], ...]
  if (coords.length < 2) return '' // Guard: mit 0/1 Punkten lässt sich keine Linie zeichnen

  // Längengrad-Verzerrung grob mit cos(Breitengrad) ausgleichen:
  // 1° Breitengrad (lat) ist überall ca. 111km, aber 1° Längengrad (lng) wird zu den Polen hin
  // immer kürzer. Ohne diese Korrektur würden Routen in unseren Breiten horizontal gestaucht
  // wirken. avgLat als lokale Näherung reicht für ein kleines Vorschau-Icon völlig aus.
  const avgLat = coords.reduce((s, [lat]) => s + lat, 0) / coords.length
  const lngScale = Math.cos(avgLat * Math.PI / 180)

  const xs = coords.map(([, lng]) => lng * lngScale)
  // Y invertieren: geografisch wächst lat nach Norden (= "oben"), aber SVG-Koordinaten
  // wachsen nach unten (y=0 ist oben) - ohne das Minus würde die Route gespiegelt gezeichnet
  const ys = coords.map(([lat]) => -lat)

  // Bounding Box der Route, um sie anschließend ins Icon einzupassen
  const minX = Math.min(...xs), maxX = Math.max(...xs)
  const minY = Math.min(...ys), maxY = Math.max(...ys)
  // Fallback auf 1: verhindert Division durch 0, falls eine Route exakt senkrecht/waagerecht
  // verläuft und spanX oder spanY dadurch 0 wäre
  const spanX = maxX - minX || 1
  const spanY = maxY - minY || 1

  const drawable = props.size - props.padding * 2
  // Math.min: die längere der beiden Dimensionen bestimmt den Maßstab (wie object-fit: contain),
  // damit die Route nie über den Rand hinausragt und das Seitenverhältnis erhalten bleibt
  const scale = Math.min(drawable / spanX, drawable / spanY)

  // Nach dem Skalieren ist die kürzere Dimension kleiner als die Box - hier mittig zentrieren,
  // statt die Route in einer Ecke kleben zu lassen
  const offsetX = (props.size - spanX * scale) / 2
  const offsetY = (props.size - spanY * scale) / 2

  const points = coords.map((_, i) => [
    (xs[i] - minX) * scale + offsetX, // erst auf 0 verschieben, dann skalieren, dann zentrieren
    (ys[i] - minY) * scale + offsetY
  ])

  // SVG-Path-Mini-Language: M (moveto) setzt den Stift auf den ersten Punkt,
  // L (lineto) zieht von dort eine Gerade zu jedem weiteren Punkt.
  // toFixed(1) hält den String kurz (eine Nachkommastelle reicht für die Icon-Größe).
  return 'M ' + points.map(([x, y]) => `${x.toFixed(1)},${y.toFixed(1)}`).join(' L ')
})
</script>

<template>
  <!--
    Reines SVG-Markup, kein Bild/keine Datei: der Browser interpretiert das d-Attribut live
    als Vektorgrafik. viewBox entspricht exakt dem Koordinatensystem, in dem pathData oben
    berechnet wurde (0..size), daher passen die Werte ohne weitere Umrechnung zusammen.
  -->
  <svg :width="size" :height="size" :viewBox="`0 0 ${size} ${size}`">
    <path
      :d="pathData"
      fill="none"
      stroke="currentColor"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
  </svg>
</template>
