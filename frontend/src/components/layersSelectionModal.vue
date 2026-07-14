<script setup>
import { useMap } from '@/composables/useMap'
import BaseModal from '@/components/BaseModal.vue'

defineEmits(['close'])

const { availableLayers, activeLayerId, setLayer } = useMap()

const selectLayer = (layerId) => {
  setLayer(layerId)
}
</script>

<template>
  <div class="popup" @click.self="$emit('close')">
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
    </div>
  </div>
</template>

<style scoped>
/* Overlay (Bottom-Sheet inkl. slideUp), Box und Schließen-Button kommen aus BaseModal */
.header {
  display: flex;
  justify-content: center;
  align-items: center;
  margin-bottom: 20px;
}

.header h2 {
  margin: 0;
  text-align: center;
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
</style>