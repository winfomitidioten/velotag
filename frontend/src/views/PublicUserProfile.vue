<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/api'
import RouteOutline from '@/components/RouteOutline.vue'
import { useUserStore } from '@/store/userStore'
import { isMobile } from '@/composables/viewport'

const route = useRoute()
const router = useRouter()
const userStore = useUserStore()

const loading = ref(true)
const errorMessage = ref('')
const profileData = ref(null)

// Ohne :id in der URL (Route /profile) zeigt die Seite das eigene Profil -
// nur dort ist der Zugang zu den Einstellungen sinnvoll.
const isOwnProfile = computed(() => !route.params.id || String(route.params.id) === String(userStore.id))

const formatDate = (isoString) =>
    new Date(isoString).toLocaleDateString('de-DE', { day: 'numeric', month: 'short', year: 'numeric' })

const formatDuration = (seconds) => {
    if (!seconds) return '—'
    const h = Math.floor(seconds / 3600)
    const m = Math.floor((seconds % 3600) / 60)
    return `${h}:${String(m).padStart(2, '0')} h`
}

const fetchProfile = async () => {
    try {
        loading.value = true
        errorMessage.value = ''

        // Beim eigenen Profil steht keine ID in der URL. Der Store wird beim App-Start
        // befüllt, kann bei einem Direktaufruf/Reload auf /profile aber noch leer sein.
        if (!route.params.id && !userStore.id) await userStore.fetchProfile()
        const userId = route.params.id ?? userStore.id

        const response = await api.get(`users/${userId}/profile/`)
        profileData.value = response.data
    } catch (err) {
        if (err.response?.status === 403) {
            errorMessage.value = 'Du hast keine Berechtigung, dieses Profil anzusehen.'
        } else if (err.response?.status === 404) {
            errorMessage.value = 'Dieser Nutzer wurde nicht gefunden.'
        } else {
            errorMessage.value = 'Profil konnte nicht geladen werden.'
        }
        console.error('Fehler beim Laden des Profils:', err)
    } finally {
        loading.value = false
    }
}

// Wechsel zwischen zwei Profilen (z.B. /user/5 -> /profile) tauscht nur die Route,
// die Komponente bleibt bestehen - ohne watch würden die alten Daten stehen bleiben.
watch(() => route.params.id, fetchProfile)

onMounted(fetchProfile)
</script>

<template>
  <!-- Zahnrad im globalen AppHeader: auf dem Desktop führt stattdessen das
       Profil-Dropdown der DesktopNavBar zu den Einstellungen. -->
  <Teleport v-if="isMobile && isOwnProfile" to="#app-header-actions">
    <button type="button" class="settings-btn" @click="router.push('/settings')" aria-label="Einstellungen öffnen">
      <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
        <circle cx="12" cy="12" r="3"/>
        <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
      </svg>
    </button>
  </Teleport>

  <div class="page-container">
    <p v-if="loading" class="status-text">Profil wird geladen...</p>
    <p v-else-if="errorMessage" class="status-text">{{ errorMessage }}</p>

    <template v-else-if="profileData">
      <div class="profile-header">
        <img :src="profileData.profile.profilbild || '/profile_pic.jpg'" alt="Profilbild" class="profile-picture" />
        <h2>{{ profileData.profile.firstname }} {{ profileData.profile.lastname }}</h2>
      </div>

      <div class="stats-row">
        <div class="stat-box">
          <span class="stat-value">{{ profileData.stats.rideCount }}</span>
          <span class="stat-label">Fahrten</span>
        </div>
        <div class="stat-box">
          <span class="stat-value">{{ profileData.stats.totalKm }}</span>
          <span class="stat-label">km gesamt</span>
        </div>
      </div>

      <h3>Letzte Fahrten</h3>
      <p v-if="profileData.recentRides.length === 0" class="status-text">Noch keine Fahrten hochgeladen</p>
      <div v-else class="rides-container">
        <div v-for="ride in profileData.recentRides" :key="ride.strecken_id" class="ride-box">
          <RouteOutline :polyline="ride.polyline_map" :size="80" class="ride-thumb" />
          <span class="ride-name">{{ ride.strecken_name }}</span>
          <div class="ride-meta">
            <span>{{ formatDate(ride.created_at) }}</span>
            <span>{{ formatDuration(ride.duration_seconds) }}</span>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<style scoped>
.page-container {
  min-height: 100vh;
  /* flex-shrink: 0, da #app ein Flex-Container mit fester Höhe ist - sonst würde
     der Container gestaucht und das padding-bottom läge nicht unter dem Inhalt. */
  flex-shrink: 0;
  padding: calc(var(--safe-top, 0px) + var(--app-header-height) + 1.5rem) 1.5rem
           calc(var(--safe-bottom, 0px) + var(--tab-bar-height) + 2rem) 1.5rem;
  background-color: var(--color-bg-page);
  box-sizing: border-box;
}

.status-text {
  color: var(--color-text-muted);
  text-align: center;
  margin-top: 4rem;
}

.settings-btn {
  width: 40px;
  height: 40px;
  padding: 0;
  border: none;
  background: none;
  color: var(--color-text-muted);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
}
.settings-btn:hover {
  background-color: var(--color-bg-page);
}

/* Das SVG bringt nur eine viewBox mit, keine width/height-Attribute - ohne diese
   Regel fällt es auf die Standardgröße eines ersetzten Elements zurück und ist im
   40px-Button nicht als Zahnrad erkennbar. */
.settings-btn svg {
  width: 22px;
  height: 22px;
}

.profile-header {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  margin-bottom: 1.5rem;
}

.profile-picture {
  width: 6rem;
  height: 6rem;
  border-radius: 50%;
  object-fit: cover;
  border: 0.25rem solid var(--color-primary);
}

.profile-header h2 {
  margin: 0;
  color: var(--color-text);
}

.stats-row {
  display: flex;
  gap: 1rem;
  justify-content: center;
  margin-bottom: 2rem;
}

.stat-box {
  display: flex;
  flex-direction: column;
  align-items: center;
  background-color: var(--color-bg-card);
  border-radius: var(--radius-md);
  padding: 1rem 1.5rem;
  min-width: 6rem;
}

.stat-value {
  font-size: 1.4rem;
  font-weight: 700;
  color: var(--color-primary);
}

.stat-label {
  font-size: 0.8rem;
  color: var(--color-text-muted);
}

h3 {
  color: var(--color-text);
  margin-bottom: 1rem;
}

.rides-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
}

.ride-box {
  padding: 12px;
  background-color: var(--color-bg-card, #f7f7f7);
  border-radius: 12px;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.ride-thumb {
  color: var(--color-primary, #3db897);
}

.ride-name {
  font-weight: 600;
  font-size: 0.9rem;
  text-align: center;
  overflow-wrap: break-word;
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
