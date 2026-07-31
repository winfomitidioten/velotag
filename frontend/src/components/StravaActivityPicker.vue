<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/api'

defineEmits(['close'])

const activities = ref([])
const importing = ref(null)
const loading = ref(true)

const loadActivities = async () => {
  loading.value = true
  const response = await api.get('strava/activities/')
  activities.value = response.data
  loading.value = false
}

const importActivity = async (activity) => {
  importing.value = activity.id
  try {
    await api.post(`strava/activities/${activity.id}/import/`, {
      strecken_name: activity.name,
    })
    activity.already_imported = true
  } finally {
    importing.value = null
  }
}

const formatDate = (isoDate) => new Date(isoDate).toLocaleDateString('de-DE')
const formatDistance = (meters) => `${(meters / 1000).toFixed(1)} km`

onMounted(loadActivities)
</script>

<template>
  <div class="strava-picker">
    <div class="picker-header">
      <h2>Strava-Fahrten importieren</h2>
      <button @click="$emit('close')" class="close-button" aria-label="Schließen">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
          <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/>
        </svg>
      </button>
    </div>

    <div class="picker-body">
      <p v-if="loading">Aktivitäten werden geladen…</p>
      <p v-else-if="activities.length === 0">Keine Strava-Aktivitäten gefunden.</p>

      <div v-else class="activity-tiles">
        <div v-for="activity in activities" :key="activity.id" class="activity-tile">
          <div class="activity-info">
            <div class="activity-title">{{ activity.name }}</div>
            <div class="activity-meta">{{ formatDate(activity.start_date) }} · {{ formatDistance(activity.distance) }}</div>
          </div>

          <button
            v-if="!activity.already_imported"
            class="import-button"
            :disabled="importing === activity.id"
            @click="importActivity(activity)"
          >
            {{ importing === activity.id ? 'Importiert…' : 'Importieren' }}
          </button>
          <span v-else class="already-imported">Bereits importiert</span>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.strava-picker {
  position: fixed;
  inset: 0;
  z-index: 2000;
  background: var(--color-bg-card, #ffffff);
  display: flex;
  flex-direction: column;
}

.picker-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: calc(var(--safe-top, 0px) + 1rem) 1.25rem 1rem;
  flex-shrink: 0;
  border-bottom: 1px solid #f0f2f5;
}

.picker-header h2 {
  margin: 0;
  font-size: 1.1rem;
}

.close-button {
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: var(--radius-lg, 10px);
  background: var(--color-primary, #3db897);
  color: white;
  cursor: pointer;
  transition: background-color 0.15s;
}

.close-button:hover {
  background-color: var(--color-primary-dark, #35a684);
}

.close-button svg {
  width: 20px;
  height: 20px;
}

.picker-body {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 1.25rem calc(var(--safe-bottom, 0px) + 1rem);
}

.activity-tiles {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.activity-tile {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: #f5f7fa;
  border-radius: 12px;
}

.activity-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
  min-width: 0;
}

.activity-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: #1a1a1a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.activity-meta {
  font-size: 0.8rem;
  color: #888;
}

.import-button {
  background-color: var(--color-primary, #3db897);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 8px 14px;
  font-size: 0.85rem;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
}

.import-button:disabled {
  opacity: 0.6;
  cursor: default;
}

.already-imported {
  font-size: 0.8rem;
  color: #888;
  white-space: nowrap;
  flex-shrink: 0;
}
</style>
