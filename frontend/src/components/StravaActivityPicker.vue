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

onMounted(loadActivities)
</script>

<template>
  <div class="popup">
    <div class="popup-content">
      <h2>Strava-Fahrten importieren</h2>

      <p v-if="loading">Aktivitäten werden geladen…</p>
      <p v-else-if="activities.length === 0">Keine Strava-Aktivitäten gefunden.</p>

      <div v-else class="activity-list">
        <div v-for="activity in activities" :key="activity.id" class="activity-row">
          <span class="activity-name">{{ activity.name }} ({{ activity.start_date }})</span>
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

      <button @click="$emit('close')" class="popup-close-button" aria-label="Schließen">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
          <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/>
        </svg>
      </button>
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
  align-items: center;
  z-index: 1001;
}

.popup-content {
  background-color: white;
  padding: 20px;
  border-radius: 8px;
  text-align: left;
  position: relative;
  max-width: 90vw;
  max-height: 80vh;
  overflow-y: auto;
}

.activity-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
  margin-top: 15px;
}

.activity-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 12px;
}

.activity-name {
  font-size: 14px;
}

.import-button {
  background-color: var(--color-primary, #3db897);
  color: white;
  border: none;
  border-radius: 6px;
  padding: 6px 12px;
  cursor: pointer;
  white-space: nowrap;
}

.import-button:disabled {
  opacity: 0.6;
  cursor: default;
}

.already-imported {
  font-size: 13px;
  color: #666;
  white-space: nowrap;
}

.popup-close-button {
  position: absolute;
  top: 16px;
  right: 16px;
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
  z-index: 3000;
}

.popup-close-button:hover {
  background-color: var(--color-primary-dark, #35a684);
}

.popup-close-button svg {
  width: 24px;
  height: 24px;
}
</style>