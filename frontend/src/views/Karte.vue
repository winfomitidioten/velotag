<script setup>

import { onMounted, ref, computed } from 'vue' //onmounted, da Karte erst nach dem Laden der Seite angezeigt werden soll -- ref, da showModal eine reaktive Variable ist, die den Zustand des Modals steuert
import velotagLogo from '@/assets/velotag-logo.png'
import GpxUploadModal from '@/components/GpxUploadModal.vue'
import { drawUserMap } from '@/composables/drawUserMap.js' //Import der Funktion zum Zeichnen der Karte mit den Strecken des User
import LayersSelectionModal from '@/components/layersSelectionModal.vue'
import { useMap } from '@/composables/useMap.js'
import L from 'leaflet'

const showModal = ref(false);//ref packt eine "dumme" HTML Variable in eine "Überwachungsbox", damit Vue weiß, wenn sich der Wert durch Anklicken des Buttons ändert
const showLayers = ref(false);

const { initializeMap, availableLayers, activeLayerId } = useMap();

const activeLayerPreview = computed(() => {
  const active = availableLayers.find(l => l.id === activeLayerId.value);
  return active ? active.preview : availableLayers[0].preview;
});

onMounted(() => {
 
  const map = initializeMap('map');

  const WatermarkControl = L.Control.extend({
    onAdd: function(map) {
      const img = L.DomUtil.create('img');
      img.src = velotagLogo; 
      img.style.width = '80px';
      return img;
    },
    onRemove: function(map) { 
      // Nichts zu tun
    }
  });

  // Logo oben rechts auf die Karte setzen
  //new WatermarkControl({ position: 'topright' }).addTo(map);

// Karte aktualisieren, Leaflet zeigt Karte schneller an, als Vue die Karte rendert und die CSS-Datei geladen hat (siehe main.js)
// daher muss die Karte hier manuell aktualisiert werden, damit sie korrekt angezeigt wird
  setTimeout(() => {
    if (map) {
      map.invalidateSize()
    }
  }, 250)
  
  window.addEventListener('resize', () => {
    map.invalidateSize()
  })

  // Routen aus dem Backend abfragen
  drawUserMap(map) //Übergabe der Karte an die Funktion, damit die Routen darauf gezeichnet werden können

})

</script>

<template>
  <div id="map"></div>
  <button class="btn_popup" @click="showModal = true">+</button>

  <GpxUploadModal v-if="showModal" @close="showModal = false" />

  <button class="btn_ebenen_preview" @click="showLayers = true" title="Ebenen auswählen">
    <img :src="activeLayerPreview" alt="Ebenen auswählen" />
  </button>

  <LayersSelectionModal v-if="showLayers" @close="showLayers = false"/>

</template>

<style scoped>
  /* Wrapper als Container für die Karte*/
  .map-wrapper {
    position: relative; 
    height: 100vh;
    width: 100%;
  }

  /* Karte füllt Container komplett aus*/
  #map {
    height: 100dvh;
    width: 100%;
    height: calc(100vh - env(safe-area-inset-bottom));
  }

  /* Upload Button "+" */
  .btn_popup {
    position: absolute;
    bottom: 20px;
    right: 10px;
    z-index: 9999; /* Button mit höchstem z-Index => garantiert immer sichtbar*/
    color: white;
    font-size: 30px;
    background-color: var(--color-primary);
    height: 50px;
    width: 50px;
    border-radius: 50%;
    border: none;
    cursor: pointer; /* Zeigt die Hand beim Hovern */
  }

  .btn_ebenen_preview {
    position: absolute;
    bottom: 30px;
    left: 10px;
    z-index: 9999;
    padding: 0;
    height: 50px;
    width: 50px;
    border-radius: 8px; /* Moderner Look mit abgerundeten Ecken */
    border: 2px solid var(--color-primary); /* Velotag-Grüner Rahmen um das Bild */
    box-shadow: 0 2px 6px rgba(0,0,0,0.3); 
    cursor: pointer;
    overflow: hidden;
    background-color: white;
  }
  .btn_ebenen_preview img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
  }
</style>