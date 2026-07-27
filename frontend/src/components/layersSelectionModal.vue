<script setup>
import { useMap } from '@/composables/useMap'
import { usePerformanceView } from '@/composables/usePerformanceView'
import { intensityGradientCss, METRIC_UNITS } from '@/utils/intensityColor'
import BaseModal from '@/components/BaseModal.vue'

defineEmits(['close'])

const props = defineProps({
  isGroupView: { type: Boolean, default: false }
})

const { availableLayers, activeLayerId, setLayer } = useMap()
const { performanceMetric, performanceRange } = usePerformanceView()

const selectLayer = (layerId) => {
  setLayer(layerId)
}

const performanceOptions = [
  { id: null, name: 'Standard' },
  { id: 'puls', name: 'Puls' },
  { id: 'tempo', name: 'Tempo' },
  { id: 'watt', name: 'Watt' },
]

// Leistungsdaten sind personenbezogen und ergeben in der Gruppen-Schnittmengen-Ansicht keinen Sinn
const isPerformanceOptionDisabled = (option) => props.isGroupView && option.id !== null

const selectPerformanceMode = (metric) => {
  if (props.isGroupView && metric !== null) return
  performanceMetric.value = metric
}
</script>

<template>
  <div class="popup">
    <div class="popup-content">
      <div class="header">
        <h2>Ebenen auswählen</h2>
        <button @click="$emit('close')" class="popup-close-button" aria-label="Schließen">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
            <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/>
          </svg>
        </button>
      </div>
      
      <div class="layers-container">
        <div
          v-for="layer in availableLayers"
          :key="layer.id"
          class="layer-option"
          :class="{ 'active': layer.id === activeLayerId }"
          @click="selectLayer(layer.id)"
        >
          <img :src="layer.preview" :alt="layer.name" class="layer-preview" />
          <span class="layer-name">{{ layer.name }}</span>
        </div>
      </div>

      <h2 class="section-heading">Routendarstellung</h2>
      <div class="performance-options">
        <button
          v-for="option in performanceOptions"
          :key="option.name"
          type="button"
          class="performance-option"
          :class="{ active: performanceMetric === option.id, disabled: isPerformanceOptionDisabled(option) }"
          :disabled="isPerformanceOptionDisabled(option)"
          :title="isPerformanceOptionDisabled(option) ? 'In der Gruppenansicht nicht verfügbar' : ''"
          @click="selectPerformanceMode(option.id)"
        >
          {{ option.name }}
        </button>
      </div>
      <p v-if="isGroupView" class="performance-hint">
        Leistungsdaten sind an dein Profil gebunden und in der Gruppenansicht nicht verfügbar.
      </p>

      <div v-if="performanceMetric" class="performance-legend">
        <template v-if="performanceRange.hasData">
          <span class="performance-legend-label">{{ performanceRange.minValue }}</span>
          <div class="performance-legend-bar" :style="{ background: intensityGradientCss(performanceMetric, performanceRange.minValue, performanceRange.maxValue) }"></div>
          <span class="performance-legend-label">{{ performanceRange.maxValue }} {{ METRIC_UNITS[performanceMetric] }}</span>
        </template>
        <span v-else class="performance-legend-empty">Keine Daten für diese Ansicht (nur GPX-Uploads werden unterstützt).</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
/* Overlay, Box, Radius/Schatten und Schließen-Button kommen aus BaseModal */
.layers-modal-title {
  margin-bottom: 20px;
}

.layers-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
}

.layer-option {
  cursor: pointer;
  border: 2px solid var(--color-border, #ccc);
  border-radius: 8px;
  padding: 8px;
  transition: all 0.2s ease-in-out;
  display: flex;
  flex-direction: column;
  align-items: center;
}

.layer-option:hover {
  border-color: var(--color-primary);
  transform: translateY(-3px);
}

.layer-option.active {
  border-color: var(--color-primary);
  box-shadow: 0 0 10px rgba(61, 184, 151, 0.5);
}

.layer-preview {
  width: 100%;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
  display: block;
  margin-bottom: 8px;
  border: 1px solid var(--color-border, #eee);
}

.layer-name {
  font-weight: 500;
  font-size: 14px;
}

.section-heading {
  margin: 24px 0 12px 0;
  text-align: left;
  font-size: 1rem;
}

.performance-options {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.performance-option {
  cursor: pointer;
  border: 2px solid var(--color-border, #ccc);
  border-radius: 20px;
  padding: 8px 16px;
  background: white;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text, #2c3e50);
  transition: all 0.2s ease-in-out;
}

.performance-option:hover {
  border-color: var(--color-primary);
}

.performance-option.active {
  border-color: var(--color-primary);
  background-color: var(--color-primary);
  color: white;
}

.performance-option.disabled {
  cursor: not-allowed;
  opacity: 0.45;
  border-color: var(--color-border, #ccc);
  background: #f1f5f9;
  color: var(--color-text-muted, #64748b);
}

.performance-option.disabled:hover {
  border-color: var(--color-border, #ccc);
}

.performance-hint {
  margin: 10px 0 0 0;
  text-align: left;
  font-size: 12px;
  color: var(--color-text-muted, #64748b);
}

.performance-legend {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--color-border, #eee);
}

.performance-legend-bar {
  flex: 1;
  height: 8px;
  border-radius: 4px;
}

.performance-legend-label {
  white-space: nowrap;
  font-size: 12px;
  font-weight: 500;
  color: var(--color-text-muted, #64748b);
}

.performance-legend-empty {
  font-size: 12px;
  text-align: left;
  color: var(--color-text-muted, #64748b);
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