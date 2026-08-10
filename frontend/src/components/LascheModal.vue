<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/api'
import RouteOutline from '@/components/RouteOutline.vue'

const props = defineProps({
    open: { type: Boolean, default: false },
    rideCount: { type: [Number, String], default: 0 },
    totalkm: { type: [Number, String], default: 0 },
})
const emit = defineEmits(['update:open'])

const router = useRouter()
const rides = ref([])
const loading = ref(true)

// --- Sheet-Geste -----------------------------------------------------------
// Das Sheet ist immer vollständig gerendert und nur so weit nach unten geschoben,
// dass der Griff herausschaut. Dadurch wird der Inhalt schon während des Ziehens
// sichtbar, statt erst nach dem Loslassen nachgerendert zu werden.
const SNAP_THRESHOLD = 0.3 // ab 30 % Zugweg schnappt das Sheet auf, sonst zu

const sheetEl = ref(null)
const dragging = ref(false)
const openProgress = ref(0) // 0 = nur Griff sichtbar, 1 = ganz offen

let startY = 0
let startProgress = 0
let dragRange = 1 // ziehbare Strecke in px (Sheet-Höhe minus Griff)
let pendingProgress = 0
let raf = null

const sheetStyle = computed(() => ({
    // 100 % = eigene Höhe: bei progress 0 ist alles bis auf den Griff nach unten geschoben
    transform: `translate(-50%, calc((100% - var(--lasche-height)) * ${1 - openProgress.value}))`,
}))

const scrimStyle = computed(() => {
    const visible = openProgress.value > 0.02
    return {
        opacity: openProgress.value * 0.5,
        // Solange das Sheet zu ist, darf der Schleier keine Klicks auf die Karte abfangen
        pointerEvents: openProgress.value > 0.05 ? 'auto' : 'none',
        // Blur nur solange sichtbar - dauerhaft aktiv kostet auf der Karte unnötig GPU-Zeit
        backdropFilter: visible ? `blur(${(openProgress.value * 4).toFixed(1)}px)` : 'none',
        WebkitBackdropFilter: visible ? `blur(${(openProgress.value * 4).toFixed(1)}px)` : 'none',
    }
})

const setOpen = (value) => {
    openProgress.value = value ? 1 : 0
    emit('update:open', value)
}

const onTouchStart = (event) => {
    startY = event.touches[0].clientY
    startProgress = openProgress.value

    // Ziehbare Strecke einmal pro Geste messen: Sheet-Höhe abzüglich des Griffs,
    // der ja auch im geschlossenen Zustand sichtbar bleibt.
    const height = sheetEl.value?.offsetHeight ?? 0
    const grip = parseFloat(getComputedStyle(sheetEl.value).getPropertyValue('--lasche-height')) || 38
    dragRange = Math.max(height - grip, 1)

    dragging.value = true
}

const onTouchMove = (event) => {
    if (!dragging.value) return
    const delta = startY - event.touches[0].clientY // nach oben ziehen = positiv
    pendingProgress = Math.min(Math.max(startProgress + delta / dragRange, 0), 1)

    // touchmove feuert häufiger als der Bildschirm zeichnet - ohne diese Kopplung
    // an den Frame rechnet Vue mehrfach pro Bild neu und die Bewegung wirkt hakelig.
    if (raf === null) {
        raf = requestAnimationFrame(() => {
            openProgress.value = pendingProgress
            raf = null
        })
    }
}

const onTouchEnd = () => {
    if (raf !== null) {
        cancelAnimationFrame(raf)
        raf = null
    }
    dragging.value = false

    // Aus der Ruhelage heraus genügt ein kurzer Zug, von offen aus muss man
    // entsprechend weit zurückziehen - daher die Schwelle relativ zum Start.
    const shouldOpen = startProgress > 0.5
        ? openProgress.value > 1 - SNAP_THRESHOLD
        : openProgress.value > SNAP_THRESHOLD
    setOpen(shouldOpen)
}

const toggle = () => {
    // Nach einer Wischgeste feuert zusätzlich das Klick-Ereignis - dann hat
    // onTouchEnd den Zustand schon gesetzt und der Klick darf nichts mehr tun.
    if (dragging.value) return
    setOpen(openProgress.value < 0.5)
}

// --- Daten -----------------------------------------------------------------
const recentRides = computed(() =>
    [...rides.value]
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 4)
)

const formatDate = (isoString) =>
    new Date(isoString).toLocaleDateString('de-DE', { day: 'numeric', month: 'short', year: 'numeric' })

const formatDuration = (seconds) => {
    if (!seconds) return '—'
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    return `${h}:${String(m).padStart(2, '0')} h`
}

const goToRides = () => {
    // Sheet zuklappen, sonst steht es beim Zurückkehren auf die Karte noch offen
    setOpen(false)
    router.push({ name: 'rides' })
}

const fetchRides = async () => {
    try {
        const response = await api.get('routes/list/')
        rides.value = response.data
    } catch (err) {
        console.error('Fehler beim Laden der Fahrten:', err)
    } finally {
        loading.value = false
    }
}

// Von außen gesteuertes Öffnen/Schließen (v-model) auf die Animation übertragen
watch(() => props.open, (value) => {
    if (value !== (openProgress.value >= 0.5)) openProgress.value = value ? 1 : 0
    if (value) fetchRides() // beim Aufziehen aktualisieren, die Karte lebt per keep-alive weiter
})

onMounted(fetchRides)
</script>

<template>
  <!-- Abdunkelnder Schleier, dessen Deckkraft dem Zugweg folgt -->
  <div class="sheet-scrim" :class="{ 'is-dragging': dragging }" :style="scrimStyle" @click="setOpen(false)"></div>

  <div
    ref="sheetEl"
    class="rides-sheet"
    :class="{ 'is-dragging': dragging }"
    :style="sheetStyle"
  >
    <button
      type="button"
      class="sheet-handle"
      @click="toggle"
      @touchstart.passive="onTouchStart"
      @touchmove.passive="onTouchMove"
      @touchend="onTouchEnd"
      @touchcancel="onTouchEnd"
    >
      <span class="sheet-grip" aria-hidden="true"></span>
      <span class="sheet-handle-text">{{ rideCount }} Rides · {{ totalkm }} km</span>
    </button>

    <div class="sheet-body">
      <h2 class="sheet-title">Deine letzten Fahrten</h2>

      <p v-if="loading" class="status-text">Fahrten werden geladen...</p>
      <p v-else-if="recentRides.length === 0" class="status-text">Noch keine Fahrten hochgeladen</p>

      <div v-else class="rides-container">
        <div v-for="ride in recentRides" :key="ride.strecken_id" class="ride-box">
            <RouteOutline :polyline="ride.polyline_map" :size="80" class="ride-thumb" />
            <span class="ride-name">{{ ride.strecken_name }}</span>
            <div class="ride-meta">
              <span class="ride-date">{{ formatDate(ride.created_at) }}</span>
              <span class="ride-duration">{{ formatDuration(ride.duration_seconds) }}</span>
            </div>
        </div>
      </div>

      <button class="btn_show_all" @click="goToRides">Alle Fahrten ansehen</button>
    </div>
  </div>
</template>

<style scoped>
.sheet-scrim {
  position: fixed;
  inset: 0;
  background-color: rgba(0, 0, 0, 1);
  /* Liegt über sämtlichen Karten-Controls (z-index < 9998) und blendet sie
     zusammen mit der Karte weich aus. Die Blur-Stärke wächst mit dem Zugweg
     und wird im Script gesetzt. */
  z-index: 9998;
  transition: opacity 0.32s cubic-bezier(0.16, 1, 0.3, 1),
              backdrop-filter 0.32s cubic-bezier(0.16, 1, 0.3, 1);
}

.rides-sheet {
  position: fixed;
  left: 50%;
  bottom: calc(var(--safe-bottom) + var(--tab-bar-height));
  z-index: 9999;
  width: min(600px, calc(100% - 24px));
  max-height: 70vh;

  display: flex;
  flex-direction: column;

  /* Deckende Fläche wie die übrigen Karten-Controls - kein transparenter Tint */
  background-color: var(--color-bg-card);
  color: var(--color-text);
  border: 1.5px solid var(--color-primary);
  border-bottom: none; /* untere Kante sitzt auf der TabBar auf */
  border-radius: 20px 20px 0 0;
  box-shadow: 0 -2px 12px rgba(0, 0, 0, 0.25);

  /* Die vertikale Geste gehört dem Sheet, nicht Leaflet */
  touch-action: none;
  will-change: transform;
  transition: transform 0.32s cubic-bezier(0.16, 1, 0.3, 1);
}

/* Am Finger darf nichts nachlaufen, solange gezogen wird */
.rides-sheet.is-dragging,
.sheet-scrim.is-dragging {
  transition: none;
}

.sheet-handle {
  flex-shrink: 0;
  height: var(--lasche-height);
  width: 100%;
  padding: 0;
  border: none;
  background: none;
  color: var(--color-primary);
  font-size: 15px;
  font-weight: 600;

  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 3px;

  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition: filter 0.15s ease;
}

/* Einheitliche Fläche, nur abgedunkelt - funktioniert in beiden Themes,
   ohne die Farbe halbtransparent zu machen */
.sheet-handle:active,
.rides-sheet.is-dragging .sheet-handle {
  filter: brightness(0.88);
}
@media (hover: hover) {
  .sheet-handle:hover {
    filter: brightness(0.94);
  }
}

.sheet-grip {
  width: 32px;
  height: 3px;
  border-radius: 999px;
  background-color: var(--color-primary);
  opacity: 0.5;
  flex-shrink: 0;
}

.sheet-body {
  flex: 1;
  min-height: 0;
  overflow-y: auto;
  padding: 4px 24px 24px 24px;
  text-align: center;
}

.sheet-title {
  margin: 0 0 20px 0;
  font-size: 1.25rem;
  font-weight: 700;
  color: var(--color-text);
}

.status-text {
  color: var(--color-text-muted);
  font-size: 0.95rem;
  margin: 1rem 0;
}

.btn_show_all {
  width: 100%;
  padding: 12px;
  border: none;
  border-radius: 999px;
  background-color: var(--color-primary);
  color: var(--color-on-primary);
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: background-color 0.15s;
}

.btn_show_all:hover {
  background-color: var(--color-primary-dark);
}

.ride-thumb {
  flex-shrink: 0;
  color: var(--color-primary);
}

.rides-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.ride-box {
  padding: 12px;
  /* Bewusst --color-bg-page: das Sheet selbst ist --color-bg-card, sonst
     hätten die Kacheln keinen Kontrast zum Hintergrund. */
  background-color: var(--color-bg-page);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.ride-name {
  font-weight: 600;
  font-size: 0.9rem;
  text-align: center;
  overflow-wrap: break-word;
  text-overflow: ellipsis;
  max-width: 100%;
  margin-top: 8px;
}

.ride-meta {
  display: flex;
  flex-direction: column;
  align-items: center;
  color: var(--color-text-muted);
  font-size: 0.75rem;
  margin-top: 4px;
}
</style>
