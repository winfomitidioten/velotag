<script setup>
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import api from '@/api/api'
import RouteOutline from '@/components/RouteOutline.vue'


defineEmits(['close'])

const router = useRouter()
const rides = ref([])
const loading = ref(true)

const lastThreeRides = computed(() =>
    [...rides.value]
        .sort((a, b) => new Date(b.created_at) - new Date(a.created_at))
        .slice(0, 3)
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
    router.push({ name: 'rides' })
}

onMounted(async () => {
    try {
        const response = await api.get('routes/list/')
        rides.value = response.data
    } catch (err) {
        console.error('Fehler beim Laden der Fahrten:', err)
    } finally {
        loading.value = false
    }
})

</script>

<template>
  <div class="popup">
    <div class="popup-content">
      <div class="header">
        <h2>Deine letzten Fahrten</h2>
        <button @click="$emit('close')" class="popup-close-button" aria-label="Schließen">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
            <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/>
          </svg>
        </button>
      </div>
      
      <p v-if="loading" class="status-text">Fahrten werden geladen...</p>
      <p v-else-if="lastThreeRides.length === 0" class="status-text">Noch keine Fahrten hochgeladen</p>

      <div v-else class="rides-container">
        <div v-for="ride in lastThreeRides" :key="ride.strecken_id" class="ride-box">
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
.popup {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: flex-end; /* Element ganz nach unten setzen */
  z-index: 1001;
  animation: fadeIn 0.2s ease-out; /* Weiches Einblenden des Hintergrunds */
}

.popup-content {
  background: white;
  padding: 24px 24px 40px 24px; /* Mehr Platz unten, z.B. für Wischgesten auf dem Smartphone */
  border-radius: 24px 24px 0 0; /* Nur die oberen Ecken abrunden */
  text-align: center;
  width: 100%;
  max-width: 600px; /* Begrenzt die Breite auf großen Bildschirmen */
  box-sizing: border-box;
  box-shadow: 0 -5px 15px rgba(0,0,0,0.2); /* Schattenverlauf nach oben gerichtet */
  animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards; /* Fährt von unten hoch */
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  position: relative;
}

.header h2 {
  margin: 0;
  text-align: center;
  flex-grow: 1;
}

.popup-close-button {
  position: absolute;
  top: -5px;
  right: -5px; /* Etwas eingerückt, damit es bei 100% Breite nicht übersteht */
  background-color: var(--color-primary, #3db897);
  border: none;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  cursor: pointer;
  color: white;
  border-radius: 50%;
  transition: background-color 0.15s;
}

.popup-close-button:hover {
  background-color: var(--color-primary-dark, #35a684);
}

.popup-close-button svg {
  width: 24px;
  height: 24px;
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
  background-color: var(--color-primary, #3db897);
  color: white;
  font-weight: 600;
  font-size: 15px;
  cursor: pointer;
  transition: background-color 0.15s;
}

.btn_show_all:hover {
  background-color: var(--color-primary-dark, #35a684);
}

.ride-thumb {
  flex-shrink: 0;
  color: var(--color-primary, #3db897);
}

.rides-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
  margin-bottom: 20px;
}

.ride-box {
  padding: 12px;
  background-color: var(--color-bg-card, #f7f7f7);
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

/* Animation für das Hochfahren */
@keyframes slideUp {
  from {
    transform: translateY(100%);
  }
  to {
    transform: translateY(0);
  }
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}
</style>