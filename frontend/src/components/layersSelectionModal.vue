<script setup>
import { computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useMap } from '@/composables/useMap'
import { usePerformanceView } from '@/composables/usePerformanceView'
import { useHeatmapStyleStore } from '@/store/heatmapStyleStore'
import { intensityGradientCss, METRIC_UNITS } from '@/utils/intensityColor'
import BaseModal from '@/components/BaseModal.vue'

defineEmits(['close'])

const props = defineProps({
  isGroupView: { type: Boolean, default: false }
})

const { availableLayers, activeLayerId, setLayer } = useMap()
const { performanceMetric, performanceRange } = usePerformanceView()
const { heatmapColor, heatmapGlowEnabled } = storeToRefs(useHeatmapStyleStore())

// Gleiche Auto-Logik wie in drawUserMap.js: Blau auf Hybrid ist am besten sichtbar, sonst Rot -
// wird als Vorschau angezeigt, solange der Nutzer noch keine eigene Farbe gewählt hat (null)
const autoHeatmapColor = computed(() => activeLayerId.value === 'hybrid' ? '#0000ff' : '#ff0000')
const displayedHeatmapColor = computed(() => heatmapColor.value ?? autoHeatmapColor.value)

const onHeatmapColorInput = (event) => {
  heatmapColor.value = event.target.value
}

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
  <BaseModal variant="sheet" width="min(560px, 90vw)" @close="$emit('close')">
    <h2>Ebenen auswählen</h2>

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

      <h2 class="section-heading">Heatmap-Personalisierung</h2>
      <div class="heatmap-style-options" :class="{ disabled: performanceMetric !== null }">
        <label class="heatmap-color-picker">
          <span>Linienfarbe</span>
          <input type="color" :value="displayedHeatmapColor" :disabled="performanceMetric !== null" @input="onHeatmapColorInput" />
        </label>
        <label class="heatmap-glow-toggle">
          <span>Glow-Effekt</span>
          <input type="checkbox" v-model="heatmapGlowEnabled" :disabled="performanceMetric !== null" />
        </label>
      </div>
      <p v-if="performanceMetric" class="performance-hint">
        Gilt nur für die Standardansicht (Puls/Tempo/Watt nutzen einen festen Farbverlauf).
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
  </BaseModal>
</template>

<style scoped>
/* Overlay, Box, Radius/Schatten und Schließen-Button kommen aus BaseModal */
.layers-container {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 15px;
  margin-top: 20px;
}

.layer-option {
  cursor: pointer;
  border: 2px solid var(--color-border);
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
  box-shadow: 0 0 10px rgba(var(--color-primary-rgb), 0.5);
}

.layer-preview {
  width: 100%;
  height: 80px;
  object-fit: cover;
  border-radius: 4px;
  display: block;
  margin-bottom: 8px;
  border: 1px solid var(--color-border);
}

.layer-name {
  font-weight: 500;
  font-size: 14px;
}

/* .layers-container ist ein Grid für die Ebenen-Vorschaukarten - alles ab hier sind eigene
   Abschnitte (Überschrift + Inhalt), die jeweils die volle Breite einnehmen und sich
   untereinander stapeln sollen, statt vom Grid-Auto-Placement in Kartenspalten gequetscht zu werden */
.section-heading,
.performance-options,
.performance-hint,
.heatmap-style-options,
.performance-legend {
  grid-column: 1 / -1;
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
  border: 2px solid var(--color-border);
  border-radius: 20px;
  padding: 8px 16px;
  background: var(--color-bg-card);
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
  transition: all 0.2s ease-in-out;
}

.performance-option:hover {
  border-color: var(--color-primary);
}

.performance-option.active {
  border-color: var(--color-primary);
  background-color: var(--color-primary);
  color: var(--color-on-primary);
}

.performance-option.disabled {
  cursor: not-allowed;
  opacity: 0.45;
  border-color: var(--color-border);
  background: var(--color-bg-hover);
  color: var(--color-text-muted);
}

.performance-option.disabled:hover {
  border-color: var(--color-border);
}

.performance-hint {
  margin: 10px 0 0 0;
  text-align: left;
  font-size: 12px;
  color: var(--color-text-muted);
}

.heatmap-style-options {
  display: flex;
  flex-wrap: wrap;
  gap: 20px;
  transition: opacity 0.2s ease-in-out;
}

.heatmap-style-options.disabled {
  opacity: 0.45;
}

.heatmap-style-options.disabled .heatmap-color-picker,
.heatmap-style-options.disabled .heatmap-glow-toggle,
.heatmap-style-options.disabled input {
  cursor: not-allowed;
}

.heatmap-color-picker,
.heatmap-glow-toggle {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 14px;
  font-weight: 500;
  color: var(--color-text);
  cursor: pointer;
}

.heatmap-color-picker input[type="color"] {
  width: 36px;
  height: 36px;
  padding: 0;
  border: 2px solid var(--color-border);
  border-radius: 8px;
  cursor: pointer;
  background: none;
}

.heatmap-glow-toggle input[type="checkbox"] {
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--color-primary);
}

.performance-legend {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 14px;
  padding-top: 14px;
  border-top: 1px solid var(--color-border);
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
  color: var(--color-text-muted);
}

.performance-legend-empty {
  font-size: 12px;
  text-align: left;
  color: var(--color-text-muted);
}
</style>