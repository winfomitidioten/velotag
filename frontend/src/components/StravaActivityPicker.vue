<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/api'
import GroupSelectionUploadModal from '@/components/GroupSelectionUploadModal.vue'

defineEmits(['close'])

const activities = ref([])
const importing = ref(null)
const loading = ref(true)
// Gilt für alle Aktivitäten, die in dieser Sitzung importiert werden (gleiches Prinzip wie
// beim GPX-Upload in GpxUploadModal.vue)
const selectedGroupIds = ref([])

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
      group_id: selectedGroupIds.value,
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
  <!-- Mobil füllt der Picker den Bildschirm, ab Tablet-Breite wird daraus ein
       zentrierter Dialog auf abgedunkeltem Grund (gleiche Optik wie BaseModal). -->
  <div class="strava-picker">
    <div class="picker-panel">
      <div class="picker-header">
        <div class="picker-heading">
          <h2>Strava-Fahrten importieren</h2>
          <p class="picker-subtitle">Wähle aus, welche Aktivitäten du in velotag übernehmen möchtest.</p>
        </div>
        <button @click="$emit('close')" class="close-button" aria-label="Schließen">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
            <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/>
          </svg>
        </button>
      </div>

      <div class="picker-body">
        <!-- show-header=false: die Komponente bringt sonst eine eigene Trennlinie samt
             Beschriftung mit, die hier neben der Section-Überschrift doppelt wäre. -->
        <div class="group-section">
          <span class="group-section-label">Optional - Gruppenauswahl</span>
          <GroupSelectionUploadModal :show-header="false" @update:selectedGroup="selectedGroupIds = $event" />
        </div>

        <!-- Platzhalter-Kacheln statt reinem Textstatus: die Liste springt beim
             Nachladen dadurch nicht in der Höhe. -->
        <div v-if="loading" class="activity-tiles" aria-hidden="true">
          <div v-for="n in 3" :key="n" class="activity-tile is-skeleton">
            <span class="skeleton-icon"></span>
            <div class="activity-info">
              <span class="skeleton-line skeleton-line--title"></span>
              <span class="skeleton-line skeleton-line--meta"></span>
            </div>
          </div>
        </div>

        <div v-else-if="activities.length === 0" class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
            <path d="M196-160q-82.33 0-139.17-57.17Q0-274.33 0-356.67 0-439 57.52-495.83q57.53-56.84 139.15-56.84 73 0 126.16 45.67Q376-461.33 388-392h42.67L352-613.33h-72V-680h192v66.67h-49.33l22 60.66h212L590-733.33H485.33V-800H586q24.67 0 42.5 12t26.17 34.67l73.33 200h36q81.34 0 138.67 56.99Q960-439.35 960-358.5q0 81.83-56.84 140.17Q846.32-160 764-160q-71.73 0-126.03-47t-67.3-118.33H388q-12 71-65.67 118.16Q268.67-160 196-160Z"/>
          </svg>
          <p>Keine Strava-Aktivitäten gefunden.</p>
        </div>

        <div v-else class="activity-tiles">
          <div
            v-for="activity in activities"
            :key="activity.id"
            class="activity-tile"
            :class="{ 'is-imported': activity.already_imported }"
          >
            <span class="activity-icon" aria-hidden="true">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
                <path d="M196-160q-82.33 0-139.17-57.17Q0-274.33 0-356.67 0-439 57.52-495.83q57.53-56.84 139.15-56.84 73 0 126.16 45.67Q376-461.33 388-392h42.67L352-613.33h-72V-680h192v66.67h-49.33l22 60.66h212L590-733.33H485.33V-800H586q24.67 0 42.5 12t26.17 34.67l73.33 200h36q81.34 0 138.67 56.99Q960-439.35 960-358.5q0 81.83-56.84 140.17Q846.32-160 764-160q-71.73 0-126.03-47t-67.3-118.33H388q-12 71-65.67 118.16Q268.67-160 196-160Zm0-66.67q45.67 0 79.17-28.16 33.5-28.17 45.5-70.5H204V-392h116.67q-12-42-45.84-68-33.83-26-78.16-26-54.34 0-92.17 37.5t-37.83 91.83q0 54.17 37.5 92.09 37.5 37.91 91.83 37.91Zm568 0q54.33 0 91.83-37.91 37.5-37.92 37.5-92.09 0-54.33-37.5-91.83T764-486h-12l39.33 110.67-62.66 22-41.34-110q-26 17-39.33 45.33-13.33 28.33-13.33 61.33 0 54.17 37.5 92.09 37.5 37.91 91.83 37.91Z"/>
              </svg>
            </span>

            <div class="activity-info">
              <div class="activity-title">{{ activity.name }}</div>
              <div class="activity-meta">
                <span class="meta-chip">{{ formatDate(activity.start_date) }}</span>
                <span class="meta-chip">{{ formatDistance(activity.distance) }}</span>
              </div>
            </div>

            <button
              v-if="!activity.already_imported"
              class="import-button"
              :disabled="importing === activity.id"
              @click="importActivity(activity)"
            >
              {{ importing === activity.id ? 'Importiert…' : 'Importieren' }}
            </button>
            <span v-else class="already-imported">
              <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
                <path d="M382-240 154-468l57-57 171 171 367-367 57 57-424 424Z"/>
              </svg>
              Importiert
            </span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.strava-picker {
  position: fixed;
  inset: 0;
  /* Über AppHeader (10000/10001) und den Karten-Controls, damit nichts davon
     in den Picker hineinragt (siehe BaseModal, gleicher Wert). */
  z-index: 10002;
  display: flex;
  flex-direction: column;
  background: var(--color-bg-page);
}

.picker-panel {
  box-sizing: border-box;
  flex: 1;
  min-height: 0; /* erlaubt dem Body, innerhalb des Panels zu scrollen */
  display: flex;
  flex-direction: column;
  background: var(--color-bg-card);
}

.picker-header {
  box-sizing: border-box;
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 1rem;
  padding: calc(var(--safe-top, 0px) + 1.25rem) 1.25rem 1rem;
  flex-shrink: 0;
  border-bottom: 1px solid var(--color-border);
}

.picker-heading {
  min-width: 0;
}

.picker-header h2 {
  margin: 0;
  font-size: 1.15rem;
  font-weight: 700;
  color: var(--color-text);
}

.picker-subtitle {
  margin: 0.25rem 0 0;
  font-size: 0.85rem;
  line-height: 1.35;
  color: var(--color-text-muted);
}

.close-button {
  box-sizing: border-box;
  width: 36px;
  height: 36px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  border-radius: 50%;
  background-color: var(--color-bg-close-btn);
  color: var(--color-text-muted);
  cursor: pointer;
  transition: background-color 0.15s, color 0.15s;
}

.close-button:hover {
  background-color: var(--color-danger-bg);
  color: var(--color-danger);
}

.close-button svg {
  width: 18px;
  height: 18px;
}

.picker-body {
  flex: 1;
  overflow-y: auto;
  padding: 1rem 1.25rem calc(var(--safe-bottom, 0px) + 1.5rem);
}

/* Gruppenauswahl abgesetzt vom Rest: sie gilt für alle Importe dieser Sitzung
   und ist damit eine Einstellung, keine Listenzeile. */
.group-section {
  box-sizing: border-box;
  background: var(--color-bg-input);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: 0.75rem 1rem 1rem;
  margin-bottom: 1.25rem;
}

.group-section-label {
  display: block;
  margin-bottom: 0.5rem;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-text-muted);
}

.activity-tiles {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.activity-tile {
  box-sizing: border-box;
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 14px;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  transition: border-color 0.15s, box-shadow 0.15s;
}

@media (hover: hover) {
  .activity-tile:not(.is-skeleton):hover {
    border-color: rgba(var(--color-primary-rgb), 0.5);
    box-shadow: 0 2px 10px rgba(0, 0, 0, 0.06);
  }
}

.activity-tile.is-imported {
  background: var(--color-bg-page);
}

.activity-icon {
  box-sizing: border-box;
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  background: var(--color-primary-soft);
  color: var(--color-primary);
}

.activity-icon svg {
  width: 22px;
  height: 22px;
}

.activity-info {
  display: flex;
  flex-direction: column;
  gap: 6px;
  min-width: 0;
  flex: 1;
}

.activity-title {
  font-size: 0.95rem;
  font-weight: 600;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.activity-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
}

.meta-chip {
  box-sizing: border-box;
  padding: 2px 8px;
  border-radius: 999px;
  background: var(--color-bg-hover);
  font-size: 0.75rem;
  color: var(--color-text-muted);
  white-space: nowrap;
}

.import-button {
  box-sizing: border-box;
  background-color: var(--color-primary);
  color: var(--color-on-primary);
  border: none;
  border-radius: 999px;
  padding: 9px 16px;
  font-size: 0.85rem;
  font-weight: 600;
  cursor: pointer;
  white-space: nowrap;
  flex-shrink: 0;
  transition: background-color 0.15s;
}

.import-button:hover:not(:disabled) {
  background-color: var(--color-primary-dark);
}

.import-button:disabled {
  opacity: 0.6;
  cursor: default;
}

.already-imported {
  display: flex;
  align-items: center;
  gap: 5px;
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-success-text);
  white-space: nowrap;
  flex-shrink: 0;
}

.already-imported svg {
  width: 15px;
  height: 15px;
}

.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  padding: 3rem 1rem;
  color: var(--color-text-muted);
  text-align: center;
}

.empty-state svg {
  width: 44px;
  height: 44px;
  opacity: 0.4;
}

.empty-state p {
  margin: 0;
  font-size: 0.9rem;
}

/* Platzhalter während des Ladens */
.activity-tile.is-skeleton {
  pointer-events: none;
}

.skeleton-icon,
.skeleton-line {
  display: block;
  background: var(--color-bg-hover);
  animation: skeleton-pulse 1.4s ease-in-out infinite;
}

.skeleton-icon {
  width: 40px;
  height: 40px;
  flex-shrink: 0;
  border-radius: 50%;
}

.skeleton-line {
  height: 12px;
  border-radius: 6px;
}

.skeleton-line--title {
  width: 60%;
}

.skeleton-line--meta {
  width: 35%;
  height: 10px;
}

@keyframes skeleton-pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.45; }
}

/* Ab Tablet-Breite: freischwebender Dialog statt Vollbild */
@media (min-width: 768px) {
  .strava-picker {
    background-color: rgba(15, 23, 42, 0.6);
    backdrop-filter: blur(4px);
    -webkit-backdrop-filter: blur(4px);
    align-items: center;
    justify-content: center;
    padding: 2rem;
    animation: picker-fade-in 0.2s ease-out;
  }

  .picker-panel {
    flex: 0 1 auto;
    width: 100%;
    max-width: 640px;
    max-height: 85vh;
    border-radius: 20px;
    overflow: hidden; /* hält Header/Body innerhalb der runden Ecken */
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.2), 0 8px 10px -6px rgba(0, 0, 0, 0.15);
    animation: picker-zoom-in 0.2s cubic-bezier(0.16, 1, 0.3, 1);
  }

  .picker-header {
    padding: 1.5rem 1.75rem 1.25rem;
  }

  .picker-body {
    padding: 1.25rem 1.75rem 1.75rem;
  }

  /* Schlanke, runde Scrollbar passend zu den runden Panel-Ecken (wie BaseModal) */
  .picker-body::-webkit-scrollbar {
    width: 8px;
  }
  .picker-body::-webkit-scrollbar-track {
    background: transparent;
  }
  .picker-body::-webkit-scrollbar-thumb {
    background-color: var(--color-border);
    border-radius: 8px;
  }
  .picker-body::-webkit-scrollbar-thumb:hover {
    background-color: var(--color-text-muted);
  }
}

@keyframes picker-fade-in {
  from { opacity: 0; }
  to { opacity: 1; }
}

@keyframes picker-zoom-in {
  from { opacity: 0; transform: translateY(12px) scale(0.98); }
  to { opacity: 1; transform: translateY(0) scale(1); }
}
</style>
