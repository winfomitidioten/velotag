<script setup>

import { onMounted, ref, computed, watch } from 'vue' //onmounted, da Karte erst nach dem Laden der Seite angezeigt werden soll -- ref, da showModal eine reaktive Variable ist, die den Zustand des Modals steuert
import velotagLogo from '@/assets/velotag-logo.png'
import GpxUploadModal from '@/components/GpxUploadModal.vue'
import { drawUserMap } from '@/composables/drawUserMap.js' //Import der Funktion zum Zeichnen der Karte mit den Strecken des User
import LayersSelectionModal from '@/components/layersSelectionModal.vue'
import { usePinMode } from '@/composables/usePinMode.js'
import { useMap } from '@/composables/useMap.js'
import { useStravaImport } from '@/composables/useStravaImport'
import L from 'leaflet'

const showModal = ref(false);//ref packt eine "dumme" HTML Variable in eine "Überwachungsbox", damit Vue weiß, wenn sich der Wert durch Anklicken des Buttons ändert
const showLayers = ref(false);
const { showStravaImport } = useStravaImport();

const { initializeMap, availableLayers, activeLayerId } = useMap();
const { isPinMode, setPinMode } = usePinMode();

let mapInstance = null;

// Karte wird per <keep-alive> am Leben gehalten, onMounted läuft also nur einmal.
// Nach einem Strava-Import (Picker schließt) müssen die neuen Routen daher aktiv nachgeladen werden
watch(showStravaImport, (isOpen, wasOpen) => {
  if (!isOpen && wasOpen && mapInstance) {
    drawUserMap(mapInstance);
  }
});

const activeLayerPreview = computed(() => {
  const active = availableLayers.find(l => l.id === activeLayerId.value);
  return active ? active.preview : availableLayers[0].preview;
});

onMounted(() => {

  const map = initializeMap('map');
  mapInstance = map;

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
  <button v-if="!showStravaImport" class="btn_popup" @click="showModal = true">
    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
      <path d="M440-440H200v-80h240v-240h80v240h240v80H520v240h-80v-240Z"/>
    </svg>
  </button>

  <GpxUploadModal v-if="showModal" @close="showModal = false" />

  <div v-if="!showStravaImport" class="map_controls_pill">
    <button class="btn_ebenen_preview" @click="showLayers = true" title="Ebenen auswählen">
      <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
        <path d="M480-118 120-398l66-50 294 228 294-228 66 50-360 280Zm0-202L120-600l360-280 360 280-360 280Zm0-280Zm0 178 230-178-230-178-230 178 230 178Z"/>
      </svg>
    </button>

    <div class="pill-divider"></div>

    <button class="btn_pin_mode" :class="{ active: isPinMode }" @click="setPinMode(!isPinMode)" title="Foto anpinnen">
      <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
        <path d="M440-440ZM120-120q-33 0-56.5-23.5T40-200v-480q0-33 23.5-56.5T120-760h126l74-80h240v80H355l-73 80H120v480h640v-360h80v360q0 33-23.5 56.5T760-120H120Zm640-560v-80h-80v-80h80v-80h80v80h80v80h-80v80h-80ZM440-260q75 0 127.5-52.5T620-440q0-75-52.5-127.5T440-620q-75 0-127.5 52.5T260-440q0 75 52.5 127.5T440-260Zm0-80q-42 0-71-29t-29-71q0-42 29-71t71-29q42 0 71 29t29 71q0 42-29 71t-71 29Z"/>
      </svg>
    </button>
  </div>

  <LayersSelectionModal v-if="showLayers" @close="showLayers = false"/>

</template>

<style scoped>
  /* Wrapper als Container für die Karte*/
  .map-wrapper {
    position: relative; 
    height: 100vh;
    width: 100%;
  }

  /* Karte füllt Container komplett aus, bis an den unteren Bildschirmrand
     (kein Abzug von safe-area-inset-bottom mehr - die Buttons haben ihren eigenen
     Sicherheitsabstand schon über --safe-bottom, die Karte selbst darf bis ganz unten laufen) */
  #map {
    height: 100dvh;
    width: 100%;
  }

  /* Maßstabsleiste (L.control.scale, unten links): nur während des Zoomens sichtbar
     (Ein-/Ausblenden siehe useMap.js), sitzt über dem Ebenen-Button statt am Kartenrand,
     zeigt nur noch den Text als abgerundete Pille statt sich als Lineal zu verbreitern.
     :deep(), da Leaflet dieses Element dynamisch selbst ins DOM einfügt */
  :deep(.map-scale-control) {
    margin-bottom: calc(var(--safe-bottom) + 75px) !important;
    margin-left: 10px;
    opacity: 0;
    pointer-events: none;
    transition: opacity 0.25s ease;
  }
  :deep(.map-scale-control.is-visible) {
    opacity: 1;
  }
  :deep(.map-scale-control .leaflet-control-scale-line) {
    width: auto !important; /* ignoriert Leaflets dynamische Breite, die den "Lineal"-Effekt erzeugt */
    border: none;
    border-radius: 12px;
    background: rgba(255, 255, 255, 0.92);
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
    color: var(--color-text, #1a1a1a);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  }

  /* Upload Button "+"
     z-index 500: über der Karte/Leaflet-Controls, aber unter allen Modals (>=1001),
     damit er beim Öffnen des Ebenen- oder Upload-Modals dahinter verschwindet */
  .btn_popup {
    position: absolute;
    bottom: calc(var(--safe-bottom) + 15px);
    right: 10px;
    z-index: 500;
    color: white;
    font-size: 30px;
    background-color: var(--color-primary);
    height: 50px;
    width: 50px;
    border-radius: 50%;
    border: none;
    cursor: pointer; /* Zeigt die Hand beim Hovern */
  }

  .map_controls_pill {
    position: absolute;
    bottom: calc(var(--safe-bottom) + 15px);
    left: 10px;
    z-index: 500;
    display: flex;
    flex-direction: column;
    align-items: center;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    background-color: white;
  }

  .btn_ebenen_preview,
  .btn_pin_mode {
    height: 50px;
    width: 50px;
    border: none;
    outline: none;
    appearance: none;
    -webkit-appearance: none;
    box-shadow: none;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    background-color: white;
    color: var(--color-primary);
    transition: color 0.2s ease;
  }
  
  .pill-divider {
    width: 24px;
    height: 1px;
    background: rgba(0,0,0,0.12);
  }

  .btn_pin_mode.active {
    color: #9a9a9a;
  }

</style>