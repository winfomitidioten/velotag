<script setup>

import { onMounted, ref, computed, watch, shallowRef } from 'vue' //onmounted, da Karte erst nach dem Laden der Seite angezeigt werden soll -- ref, da showModal eine reaktive Variable ist, die den Zustand des Modals steuert
import velotagLogo from '@/assets/velotag-logo.png'
import GpxUploadModal from '@/components/GpxUploadModal.vue'
import { drawUserMap } from '@/composables/drawUserMap.js' //Import der Funktion zum Zeichnen der Karte mit den Strecken des User
import LayersSelectionModal from '@/components/layersSelectionModal.vue'
import { useMap } from '@/composables/useMap.js'
import L from 'leaflet'
import { useFavorite } from '@/composables/useFavorite.js'
import api from '@/api/api';

const showModal = ref(false);//ref packt eine "dumme" HTML Variable in eine "Überwachungsbox", damit Vue weiß, wenn sich der Wert durch Anklicken des Buttons ändert
const showLayers = ref(false);

const { initializeMap, availableLayers, activeLayerId } = useMap();

const isGroupView = ref(false);
const { favoriteGroupId } = useFavorite()

const map = shallowRef(null);//shallowRef überwacht nur .value von Map und nicht alle internen Eigenschaften => Performance

const activeLayerPreview = computed(() => {
  const active = availableLayers.find(l => l.id === activeLayerId.value);
  return active ? active.preview : availableLayers[0].preview;
});

onMounted(() => {
 
  map.value = initializeMap('map');

  const WatermarkControl = L.Control.extend({
    onAdd: function(m) {
      const img = L.DomUtil.create('img');
      img.src = velotagLogo; 
      img.style.width = '80px';
      return img;
    },
    onRemove: function(m) { 
      // Nichts zu tun
    }
  });

  // Logo oben rechts auf die Karte setzen
  new WatermarkControl({ position: 'topright' }).addTo(map.value);

// Karte aktualisieren, Leaflet zeigt Karte schneller an, als Vue die Karte rendert und die CSS-Datei geladen hat (siehe main.js)
// daher muss die Karte hier manuell aktualisiert werden, damit sie korrekt angezeigt wird
  setTimeout(() => {
    map.value.invalidateSize()
  }, 100)

  // Routen aus dem Backend abfragen
  drawUserMap(map.value, isGroupView.value, favoriteGroupId.value) //Übergabe der Karte an die Funktion, damit die Routen darauf gezeichnet werden können
  console.log("übergebene Gruppen-ID in Karte.vue:", favoriteGroupId.value)
})

watch(isGroupView, async (newValue) => {
  console.log("isGroupView geändert:", newValue, favoriteGroupId.value);
  //Hier DB aufruf, um die Routen für die ausgewählte Ansicht zu laden; Problem: favoriteGroupId wird aktuell nicht aus DB geladen
  const response = await api.get('groups/favorite/');
  if (response.status === 200) {
    favoriteGroupId.value = response.data.favorite_group_id;
  } else {
    console.error('Fehler beim Abrufen der Lieblingsgruppe:', response.status);
  }
  drawUserMap(map.value, isGroupView.value, favoriteGroupId.value)
  
});
</script>

<template>
  <div id="map"></div>
  <button class="btn_popup" @click="showModal = true">+</button>

  <GpxUploadModal v-if="showModal" @close="showModal = false" />

  <button class="btn_ebenen_preview" @click="showLayers = true" title="Ebenen auswählen">
    <img :src="activeLayerPreview" alt="Ebenen auswählen" />
  </button>

  <div class="toggle-switch-container" @click="isGroupView = !isGroupView" title="Ansicht wechseln">
    <div class="toggle-option" :class="{ active: !isGroupView }">Solo</div>
    <div class="toggle-option" :class="{ active: isGroupView }">Group</div>
    <div class="toggle-slider" :class="{ 'is-group': isGroupView }"></div>
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

  /* Karte füllt Container komplett aus*/
  #map { 
    height: 100%; 
    width: 100%;
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
    z-index: 1000;
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

  /* --- NEUES STYLING FÜR DEN TOGGLE SWITCH --- */
  .toggle-switch-container {
    position: absolute;
    top: 20px;
    right: 110px; /* Weiter links platziert, damit es nicht mit dem Velotag-Logo überlappt */
    z-index: 9999;
    background-color: white;
    border-radius: 30px;
    display: flex;
    align-items: center;
    padding: 4px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    cursor: pointer;
    width: 160px;
    height: 40px;
    user-select: none;
  }

  .toggle-option {
    flex: 1;
    text-align: center;
    font-size: 14px;
    font-weight: 600;
    color: #555;
    z-index: 2; /* Hält den Text über dem grünen Slider */
    transition: color 0.3s ease;
  }

  .toggle-option.active {
    color: white; /* Schrift wird weiß, wenn der farbige Slider darunter liegt */
  }

  .toggle-slider {
    position: absolute;
    top: 4px;
    left: 4px;
    width: calc(50% - 4px);
    height: calc(100% - 8px);
    background-color: var(--color-primary);
    border-radius: 25px;
    transition: transform 0.3s cubic-bezier(0.4, 0.0, 0.2, 1);
    z-index: 1; /* Bleibt unter dem Text */
  }

  .toggle-slider.is-group {
    /* Verschiebt den Regler nach rechts auf die "Group" Position */
    transform: translateX(100%);
  }
</style>