<script setup>
import { useMap } from '@/composables/useMap'

defineEmits(['close'])

const { availableLayers, activeLayerId, setLayer } = useMap()

const selectLayer = (layerId) => {
  setLayer(layerId)
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