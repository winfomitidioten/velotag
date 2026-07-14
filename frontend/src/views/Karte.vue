<script setup>

import { onMounted, onUnmounted, ref, computed, watch, shallowRef } from 'vue' //onmounted, da Karte erst nach dem Laden der Seite angezeigt werden soll -- ref, da showModal eine reaktive Variable ist, die den Zustand des Modals steuert
import { onMounted, ref, computed, watch } from 'vue' //onmounted, da Karte erst nach dem Laden der Seite angezeigt werden soll -- ref, da showModal eine reaktive Variable ist, die den Zustand des Modals steuert
import velotagLogo from '@/assets/velotag-logo.png'
import GpxUploadModal from '@/components/GpxUploadModal.vue'
import { drawUserMap } from '@/composables/drawUserMap.js' //Import der Funktion zum Zeichnen der Karte mit den Strecken des User
import LayersSelectionModal from '@/components/layersSelectionModal.vue'
import { useMap } from '@/composables/useMap.js'
import { useStravaImport } from '@/composables/useStravaImport'
import L from 'leaflet'
import { useFavorite } from '@/composables/useFavorite.js'
import api from '@/api/api';

const showModal = ref(false);//ref packt eine "dumme" HTML Variable in eine "Überwachungsbox", damit Vue weiß, wenn sich der Wert durch Anklicken des Buttons ändert
const showLayers = ref(false);
const { showStravaImport } = useStravaImport();

const { initializeMap, availableLayers, activeLayerId } = useMap();

const isGroupView = ref(false);
const { favoriteGroupId } = useFavorite()

const groups = ref([]); // Alle Gruppen des Users, für das Dropdown zur Gruppenauswahl
const selectedGroupId = ref(null); // Aktuell auf der Karte angezeigte Gruppe (nur temporäre Auswahl, kein Favorit-Update)
const showGroupDropdown = ref(false);
const groupDropdown = ref(null); // Template-Ref für Klick-außerhalb-Erkennung

// Favorit wird an erster Stelle der Liste angezeigt, damit er schnell auswählbar ist
const sortedGroups = computed(() => {
  return [...groups.value].sort((a, b) => {
    if (a.id === favoriteGroupId.value) return -1;
    if (b.id === favoriteGroupId.value) return 1;
    return 0;
  });
});

const selectedGroupName = computed(() => {
  const selected = groups.value.find(g => g.id === selectedGroupId.value);
  return selected ? selected.name : 'Gruppe wählen';
});

const selectGroup = (groupId) => {
  selectedGroupId.value = groupId;
  showGroupDropdown.value = false;
};

const handleClickOutside = (event) => {
  if (groupDropdown.value && !groupDropdown.value.contains(event.target)) {
    showGroupDropdown.value = false;
  }
};

const map = shallowRef(null);//shallowRef überwacht nur .value von Map und nicht alle internen Eigenschaften => Performance
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

const fetchGroups = async () => {
  try {
    const response = await api.get('groups/');
    groups.value = response.data;
  } catch (err) {
    console.error('Fehler beim Abrufen der Gruppen:', err);
  }
};

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

  fetchGroups(); // Gruppenliste für das Auswahl-Dropdown laden

  document.addEventListener('click', handleClickOutside);
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
})

watch(isGroupView, async (newValue) => {
  console.log("isGroupView geändert:", newValue, favoriteGroupId.value);
  if (newValue) {
    //Hier DB aufruf, um die Routen für die ausgewählte Ansicht zu laden; Problem: favoriteGroupId wird aktuell nicht aus DB geladen
    const response = await api.get('groups/favorite/');
    if (response.status === 200) {
      favoriteGroupId.value = response.data.favorite_group_id;
    } else {
      console.error('Fehler beim Abrufen der Lieblingsgruppe:', response.status);
    }
    // Beim Wechsel in die Gruppenansicht wird standardmäßig der Favorit ausgewählt
    selectedGroupId.value = favoriteGroupId.value;
    drawUserMap(map.value, true, selectedGroupId.value)
  } else {
    drawUserMap(map.value, false)
  }
});

// Auswahl einer anderen Gruppe im Dropdown: nur temporäre Kartenansicht, Favorit bleibt unverändert
watch(selectedGroupId, (newGroupId) => {
  if (isGroupView.value) {
    drawUserMap(map.value, true, newGroupId)
  }
});
</script>

<template>
  <div id="map"></div>
  <button v-if="!showStravaImport" class="btn_popup" @click="showModal = true">+</button>

  <GpxUploadModal v-if="showModal" @close="showModal = false" />

  <button v-if="!showStravaImport" class="btn_ebenen_preview" @click="showLayers = true" title="Ebenen auswählen">
    <img :src="activeLayerPreview" alt="Ebenen auswählen" />
  </button>

  <div class="toggle-switch-container" @click="isGroupView = !isGroupView" title="Ansicht wechseln">
    <div class="toggle-option" :class="{ active: !isGroupView }">Solo</div>
    <div class="toggle-option" :class="{ active: isGroupView }">Group</div>
    <div class="toggle-slider" :class="{ 'is-group': isGroupView }"></div>
  </div>

  <div v-if="isGroupView" class="group-dropdown" ref="groupDropdown">
    <button
      type="button"
      class="group-dropdown-trigger"
      :class="{ open: showGroupDropdown }"
      @click="showGroupDropdown = !showGroupDropdown"
      title="Gruppe auswählen"
    >
      <svg v-if="selectedGroupId === favoriteGroupId" class="star-icon" viewBox="0 -960 960 960">
        <path d="m233-120 65-281L80-590l288-25 112-265 112 265 288 25-218 189 65 281-247-149-247 149Z"/>
      </svg>
      <span class="group-dropdown-label">{{ selectedGroupName }}</span>
      <svg class="chevron-icon" :class="{ rotated: showGroupDropdown }" viewBox="0 0 24 24">
        <path d="M7 10l5 5 5-5z"/>
      </svg>
    </button>

    <ul v-if="showGroupDropdown" class="group-dropdown-list">
      <li
        v-for="group in sortedGroups"
        :key="group.id"
        class="group-dropdown-item"
        :class="{ selected: group.id === selectedGroupId }"
        @click="selectGroup(group.id)"
      >
        <svg v-if="group.id === favoriteGroupId" class="star-icon" viewBox="0 -960 960 960">
          <path d="m233-120 65-281L80-590l288-25 112-265 112 265 288 25-218 189 65 281-247-149-247 149Z"/>
        </svg>
        <span>{{ group.name }}</span>
      </li>
    </ul>
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

  .btn_ebenen_preview {
    position: absolute;
    bottom: calc(var(--safe-bottom) + 15px);
    left: 10px;
    z-index: 500;
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

  /* Dropdown zur Gruppenauswahl, erscheint direkt unter dem Toggle-Switch */
  .group-dropdown {
    position: absolute;
    top: 68px;
    right: 110px;
    z-index: 9999;
    width: 170px;
  }

  .group-dropdown-trigger {
    display: flex;
    align-items: center;
    width: 100%;
    height: 40px;
    padding: 0 10px;
    gap: 6px;
    background-color: white;
    border: none;
    border-radius: 20px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    font-size: 13px;
    font-weight: 600;
    color: var(--color-text, #2c3e50);
    cursor: pointer;
    transition: border-radius 0.15s ease;
  }

  .group-dropdown-trigger.open {
    border-radius: 16px 16px 0 0;
  }

  .group-dropdown-label {
    flex: 1;
    text-align: left;
    overflow: hidden;
    text-overflow: ellipsis;
    white-space: nowrap;
  }

  .chevron-icon {
    width: 18px;
    height: 18px;
    flex-shrink: 0;
    fill: #94a3b8;
    transition: transform 0.2s ease;
  }

  .chevron-icon.rotated {
    transform: rotate(180deg);
  }

  .star-icon {
    width: 15px;
    height: 15px;
    flex-shrink: 0;
    fill: #f59e0b;
  }

  .group-dropdown-list {
    position: absolute;
    top: 40px;
    left: 0;
    width: 100%;
    max-height: 220px;
    overflow-y: auto;
    margin: 0;
    padding: 4px 0;
    list-style: none;
    background-color: white;
    border-radius: 0 0 16px 16px;
    box-shadow: 0 6px 14px rgba(0,0,0,0.25);
  }

  .group-dropdown-item {
    display: flex;
    align-items: center;
    gap: 6px;
    padding: 8px 10px;
    font-size: 13px;
    font-weight: 500;
    color: var(--color-text, #2c3e50);
    cursor: pointer;
    transition: background-color 0.15s ease;
  }

  .group-dropdown-item:hover {
    background-color: #f1f5f9;
  }

  .group-dropdown-item.selected {
    background-color: #e8f7f3;
    color: var(--color-primary);
    font-weight: 600;
  }
</style>