<script setup>

import { onMounted, ref, computed, watch } from 'vue' //onmounted, da Karte erst nach dem Laden der Seite angezeigt werden soll -- ref, da showModal eine reaktive Variable ist, die den Zustand des Modals steuert
import velotagLogo from '@/assets/velotag-logo.png'
import GpxUploadModal from '@/components/GpxUploadModal.vue'
import { drawUserMap } from '@/composables/drawUserMap.js' //Import der Funktion zum Zeichnen der Karte mit den Strecken des User
import LayersSelectionModal from '@/components/layersSelectionModal.vue'
import { usePinMode } from '@/composables/usePinMode.js'
import PhotoPinUploadModal from '@/components/PhotoPinUploadModal.vue';
import { drawPhotoPins, activeGalleryPhotos } from '@/composables/drawPhotoPins';
import PhotoPinGalleryModal from '@/components/PhotoPinGalleryModal.vue';
import { useMap } from '@/composables/useMap.js'
import { useStravaImport } from '@/composables/useStravaImport'
import L from 'leaflet'

const showModal = ref(false);//ref packt eine "dumme" HTML Variable in eine "Überwachungsbox", damit Vue weiß, wenn sich der Wert durch Anklicken des Buttons ändert
const showLayers = ref(false);
const { showStravaImport } = useStravaImport();

const { initializeMap, availableLayers, activeLayerId } = useMap();
const { isPinMode, setPinMode } = usePinMode();
const pinLatLng = ref(null);

const handleMapClick = (e) => {
  if (!isPinMode.value) return;
  pinLatLng.value = e.latlng;
  setPinMode(false);
}

const onPhotoPinCreated = () => {
  pinLatLng.value = null;
  if (mapInstance) drawPhotoPins(mapInstance)
}

const onPhotoDeleted = (deletedId) => {
  const remaining = activeGalleryPhotos.value.filter(photo => photo.id !== deletedId);
  // war es das letzte Foto an diesem Punkt, gibt es nichts mehr anzuzeigen -> Modal schließen
  activeGalleryPhotos.value = remaining.length ? remaining : null;
  if (mapInstance) drawPhotoPins(mapInstance);
};

const onPhotoUpdated = (updatedPhoto) => {
  activeGalleryPhotos.value = activeGalleryPhotos.value.map(
    photo => photo.id === updatedPhoto.id ? updatedPhoto : photo
  );
};

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
  map.on('click', handleMapClick);

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
  drawPhotoPins(map)

})

</script>

<template>
  <div id="map" :class="{ 'pin-mode-active': isPinMode }"></div>

  <div v-if="isPinMode" class="pin-mode-banner">
    <span>Du befindest dich im Foto-Pin-Modus - tippe auf die Karte, um einen Ort für dein Foto auszuwählen</span>
    <button class="pin-mode-banner-close" @click="setPinMode(false)" aria-label="Foto-Pin-Modus verlassen">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
          <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/>
        </svg>
    </button>
  </div>

  <PhotoPinUploadModal
    v-if="pinLatLng"
    :latitude="pinLatLng.lat"
    :longitude="pinLatLng.lng"
    @close="pinLatLng = null"
    @created="onPhotoPinCreated"
  />

  <PhotoPinGalleryModal
    v-if="activeGalleryPhotos"
    :photos="activeGalleryPhotos"
    @close="activeGalleryPhotos = null"
    @deleted="onPhotoDeleted"
    @updated="onPhotoUpdated"
  />

  <button class="btn_ebenen_preview" @click="showLayers = true" title="Ebenen auswählen">
    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
      <path d="M480-118 120-398l66-50 294 228 294-228 66 50-360 280Zm0-202L120-600l360-280 360 280-360 280Zm0-280Zm0 178 230-178-230-178-230 178 230 178Z"/>
    </svg>
  </button>

  <div v-if="!showStravaImport" class="map_controls_pill">
    <button class="btn_pin_mode" :class="{ active: isPinMode }" @click="setPinMode(!isPinMode)" title="Foto anpinnen">
      <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
        <path d="M440-440ZM120-120q-33 0-56.5-23.5T40-200v-480q0-33 23.5-56.5T120-760h126l74-80h240v80H355l-73 80H120v480h640v-360h80v360q0 33-23.5 56.5T760-120H120Zm640-560v-80h-80v-80h80v-80h80v80h80v80h-80v80h-80ZM440-260q75 0 127.5-52.5T620-440q0-75-52.5-127.5T440-620q-75 0-127.5 52.5T260-440q0 75 52.5 127.5T440-260Zm0-80q-42 0-71-29t-29-71q0-42 29-71t71-29q42 0 71 29t29 71q0 42-29 71t-71 29Z"/>
      </svg>
    </button>

    <div class="pill-divider"></div>

    <button class="btn_popup" @click="showModal = true">
      <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
        <path d="M440-440H200v-80h240v-240h80v240h240v80H520v240h-80v-240Z"/>
      </svg>
    </button>

    <GpxUploadModal v-if="showModal" @close="showModal = false" />
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

  :deep(.photo-pin-dot) {
    position: relative;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: var(--color-primary, #3db897);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.35);
    border: 2px solid white;
    cursor: pointer;
  }

  :deep(.photo-pin-count) {
    position: absolute;
    top: -4px;
    right: -4px;
    min-width: 16px;
    height: 16px;
    padding: 0 3px;
    border-radius: 8px;
    background-color: #e53e3e;
    color: white;
    font-size: 10px;
    font-weight: 700;
    display: flex;
    align-items: center;
    justify-content: center;
    line-height: 1;
  }

  /* Upload Button "+"
     z-index 500: über der Karte/Leaflet-Controls, aber unter allen Modals (>=1001),
     damit er beim Öffnen des Ebenen- oder Upload-Modals dahinter verschwindet */
  /* .btn_popup {
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
    cursor: pointer; // Zeigt die Hand beim Hovern
  } **/

  /* Pin-Modus: cursor: copy zeigt in den meisten Browsern automatisch
   ein kleines "+" am Mauszeiger - passendes Signal für "hier etwas hinzufügen" */
  #map.pin-mode-active {
    cursor: copy;
  }

  /* Im Pin-Modus dürfen die Routen-Polylines keine Klicks mehr schlucken,
     sonst öffnet sich ihr Popup statt den Foto-Pin zu setzen.
     Muss direkt auf den path-Elementen sitzen: Leaflet setzt dort selbst
     pointer-events: auto, was ein none auf dem Pane wieder aufheben würde */
  #map.pin-mode-active :deep(.leaflet-overlay-pane path) {
    pointer-events: none;
  }

  /* Gleiches gilt für bestehende Foto-Pins - so kann man auch direkt auf einem
     vorhandenen Pin ein weiteres Foto anlegen */
  #map.pin-mode-active :deep(.photo-pin-marker) {
    pointer-events: none;
  }


  .pin-mode-banner {
  position: fixed;
  top: calc(var(--safe-top) + 0.75rem);
  left: 50%;
  transform: translateX(-50%);
  max-width: calc(100% - 140px);
  z-index: 900;
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: var(--color-primary, #3db897);
  color: white;
  padding: 10px 14px;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
  font-size: 13px;
  }

  .pin-mode-banner-close {
    flex-shrink: 0;
    width: 22px;
    height: 22px;
    border: none;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.25);
    color: white;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    padding: 0;
  }

  .pin-mode-banner-close svg {
    width: 14px;
    height: 14px;
  }

  .btn_ebenen_preview,
  .map_controls_pill {
    position: absolute;
    bottom: calc(var(--safe-bottom) + 15px);
    right: 10px;
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
  .btn_popup,
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

  .btn_ebenen_preview {
    bottom: calc(var(--safe-bottom) + 125px);
    right: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
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