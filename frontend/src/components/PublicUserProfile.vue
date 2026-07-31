<script setup>
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import api from '@/api/api'
import RouteOutline from '@/components/RouteOutline.vue'

const route = useRoute()

const loading = ref(true)
const errorMessage = ref('')
const profileData = ref(null)

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
        const response = await api.get(`users/${route.params.id}/profile/`)
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

onMounted(fetchProfile)
</script>

<template>
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
  padding: 4rem 1.5rem 2rem;
  background-color: var(--color-bg-page);
  box-sizing: border-box;
}

.status-text {
  color: var(--color-text-muted);
  text-align: center;
  margin-top: 4rem;
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
