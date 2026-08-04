<script setup>

import { onMounted, onUnmounted, ref, computed, watch, shallowRef } from 'vue' //onmounted, da Karte erst nach dem Laden der Seite angezeigt werden soll -- ref, da showModal eine reaktive Variable ist, die den Zustand des Modals steuert
import velotagLogo from '@/assets/velotag-logo.png'
import api from '@/api/api'
import GpxUploadModal from '@/components/GpxUploadModal.vue'
import { drawUserMap } from '@/composables/drawUserMap.js' //Import der Funktion zum Zeichnen der Karte mit den Strecken des User
import { drawPerformanceMap } from '@/composables/drawPerformanceMap.js'
import LayersSelectionModal from '@/components/layersSelectionModal.vue'
import { usePinMode } from '@/composables/usePinMode.js'
import PhotoPinUploadModal from '@/components/PhotoPinUploadModal.vue';
import { drawPhotoPins, activeGalleryPhotos } from '@/composables/drawPhotoPins';
import PhotoPinGalleryModal from '@/components/PhotoPinGalleryModal.vue';
import { useMap } from '@/composables/useMap.js'
import { useStravaImport } from '@/composables/useStravaImport'
import { useFavorite } from '@/composables/useFavorite.js'
import { usePerformanceView } from '@/composables/usePerformanceView.js'
import L from 'leaflet'
//import StreckenView from './StreckenView.vue'
import LascheModal from '@/components/LascheModal.vue'

const showModal = ref(false);//ref packt eine "dumme" HTML Variable in eine "Überwachungsbox", damit Vue weiß, wenn sich der Wert durch Anklicken des Buttons ändert
const showLayers = ref(false);
const showRides= ref(false);

const rideCount= ref(0);
const totalkm = ref(0);
const { showStravaImport } = useStravaImport();

const { initializeMap, availableLayers, activeLayerId, isAttributionVisible, toggleAttribution, closeAttribution, isAttributionTarget } = useMap();
const { isPinMode, setPinMode } = usePinMode();
const pinLatLng = ref(null);
const attributionButton = ref(null); // Template-Ref für Klick-außerhalb-Erkennung

const handleMapClick = (e) => {
  closeAttribution(); // Klick irgendwo auf die Karte schließt den ausgeklappten Kartennachweis
  if (!isPinMode.value) return;
  pinLatLng.value = e.latlng;
  setPinMode(false);
}

const onPhotoPinCreated = () => {
  pinLatLng.value = null;
  if (mapInstance) drawPhotoPins(mapInstance, isGroupView.value, selectedGroupId.value)
}

const onPhotoDeleted = (deletedId) => {
  const remaining = activeGalleryPhotos.value.filter(photo => photo.id !== deletedId);
  // war es das letzte Foto an diesem Punkt, gibt es nichts mehr anzuzeigen -> Modal schließen
  activeGalleryPhotos.value = remaining.length ? remaining : null;
  if (mapInstance) drawPhotoPins(mapInstance, isGroupView.value, selectedGroupId.value);
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

const isGroupView = ref(false);
const { favoriteGroupId } = useFavorite()

const { performanceMetric, performanceRange } = usePerformanceView();

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
  const clickedButton = attributionButton.value && attributionButton.value.contains(event.target);
  const clickedBar = isAttributionTarget(event.target);
  if (isAttributionVisible.value && !clickedButton && !clickedBar) {
    closeAttribution();
  }
};

const map = shallowRef(null);//shallowRef überwacht nur .value von Map und nicht alle internen Eigenschaften => Performance

const loadPerformanceView = async (metric, forceRefresh = false) => {
  performanceRange.value = await drawPerformanceMap(map.value, metric, { forceRefresh });
};

// Karte wird per <keep-alive> am Leben gehalten, onMounted läuft also nur einmal.
// Nach einem Strava-Import (Picker schließt) müssen die neuen Routen daher aktiv nachgeladen werden
watch(showStravaImport, (isOpen, wasOpen) => {
  if (!isOpen && wasOpen && map.value) {
    if (performanceMetric.value) {
      // Neue Route(n) könnten importiert worden sein - zwischengespeicherten Stand verwerfen
      loadPerformanceView(performanceMetric.value, true);
    } else {
      drawUserMap(map.value);
    }
  }
});

// Leistungs-Ansicht ist unabhängig vom Solo/Group-Toggle (zeigt immer die eigenen Daten);
// bei Rückkehr zu "Standard" wird wieder die aktuelle Solo-/Gruppen-Ansicht gezeichnet
watch(performanceMetric, (metric) => {
  if (metric) {
    loadPerformanceView(metric);
  } else {
    drawUserMap(map.value, isGroupView.value, isGroupView.value ? selectedGroupId.value : undefined);
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
  mapInstance = map.value;
  map.value.on('click', handleMapClick);

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
    if (map.value) {
      map.value.invalidateSize()
    }
  }, 250)
  
  window.addEventListener('resize', () => {
    map.value.invalidateSize()
  })

  // Routen und Foto-Pins aus dem Backend abfragen
  drawUserMap(map.value, isGroupView.value, favoriteGroupId.value).then(stats => {  //Übergabe der Karte an die Funktion, damit die Routen darauf gezeichnet werden können
    if (stats) {
      rideCount.value = stats.rideCount
      totalkm.value = stats.totalkm
    }
  })
  drawPhotoPins(map.value, isGroupView.value, favoriteGroupId.value)
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
    // Leistungsdaten sind personenbezogen und in der Gruppenansicht nicht verfügbar
    performanceMetric.value = null;
    //Hier DB aufruf, um die Routen für die ausgewählte Ansicht zu laden; Problem: favoriteGroupId wird aktuell nicht aus DB geladen
    const response = await api.get('groups/favorite/');
    if (response.status === 200) {
      favoriteGroupId.value = response.data.favorite_group_id;
    } else {
      console.error('Fehler beim Abrufen der Lieblingsgruppe:', response.status);
    }
    // Beim Wechsel in die Gruppenansicht wird standardmäßig der Favorit ausgewählt
    selectedGroupId.value = favoriteGroupId.value;
    if (!performanceMetric.value) {
      drawUserMap(map.value, true, selectedGroupId.value)
      drawPhotoPins(map.value, true, selectedGroupId.value)
    }
  } else {
    if (!performanceMetric.value) {
      drawUserMap(map.value, false)
      drawPhotoPins(map.value, false)
    }
  }
});

// Auswahl einer anderen Gruppe im Dropdown: nur temporäre Kartenansicht, Favorit bleibt unverändert
watch(selectedGroupId, (newGroupId) => {
  if (isGroupView.value && !performanceMetric.value) {
    drawUserMap(map.value, true, newGroupId)
    drawPhotoPins(map.value, true, newGroupId)
  }
});
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
    :is-group-view="isGroupView"
    @close="activeGalleryPhotos = null"
    @deleted="onPhotoDeleted"
    @updated="onPhotoUpdated"
  />

  <button class="btn_ebenen_preview" @click="showLayers = true" title="Ebenen auswählen">
    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
      <path d="M480-118 120-398l66-50 294 228 294-228 66 50-360 280Zm0-202L120-600l360-280 360 280-360 280Zm0-280Zm0 178 230-178-230-178-230 178 230 178Z"/>
    </svg>
  </button>

  <button
    ref="attributionButton"
    class="btn_map_info"
    :class="{ active: isAttributionVisible }"
    @click="toggleAttribution"
    title="Kartennachweis anzeigen"
    aria-label="Kartennachweis anzeigen"
  >
    <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 -960 960 960" width="18px" fill="currentColor">
      <path d="M440-280h80v-240h-80v240Zm68.5-331.5Q520-623 520-640t-11.5-28.5Q497-680 480-680t-28.5 11.5Q440-657 440-640t11.5 28.5Q463-600 480-600t28.5-11.5ZM480-80q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"/>
    </svg>
  </button>

  <div v-if="!showStravaImport && !showRides && !showLayers" class="map_controls_pill">
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

  <LayersSelectionModal v-if="showLayers" :is-group-view="isGroupView" @close="showLayers = false"/>

  <button v-if="!showRides && !showLayers" class="btn_lasche" @click="showRides = true">{{ rideCount }} Rides · {{ totalkm }} km</button>
  <LascheModal v-if="showRides" @close="showRides = false" />

</template>

<style scoped>
  /* Karte füllt den vom Flex-Container (#app) verbleibenden Platz exakt aus.
     flex:1 statt fester 100dvh/100vh vermeidet die Höhen-Diskrepanz, die sonst
     rechts/unten Scroll-Leisten erzeugt hat; overflow:hidden fängt Rest-Überlauf ab.
     (Der AppHeader ist position:fixed und belegt daher keinen Flex-Platz.) */
  #map {
    flex: 1;
    min-height: 0;
    width: 100%;
    overflow: hidden;
  }
  

  /* Maßstabsleiste (L.control.scale, unten links): nur während des Zoomens sichtbar
     (Ein-/Ausblenden siehe useMap.js), liegt oberhalb des Info-Buttons/Kartennachweises,
     zeigt nur noch den Text als abgerundete Pille statt sich als Lineal zu verbreitern.
     :deep(), da Leaflet dieses Element dynamisch selbst ins DOM einfügt */
  :deep(.map-scale-control) {
    margin-bottom: calc(var(--safe-bottom) + var(--tab-bar-height) + 68px) !important;
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
    background: rgba(var(--color-bg-card-rgb), 0.92) !important; /* !important gegen Leaflets eigene .leaflet-control-attribution-Regel (gleiche Spezifität) */
    padding: 4px 10px;
    font-size: 12px;
    font-weight: 600;
    color: var(--color-text) !important;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.15);
  }

  /* Kartennachweis (L.control.attribution): standardmäßig unsichtbar, umschließt den
     Info-Button (.btn_map_info) am linken Ende wie eine Pille - der Button liegt optisch
     "in" der Leiste (linkes Padding = Buttonbreite, Button selbst per z-index obenauf) und
     die Leiste expandiert beim Anklicken seitlich nach rechts aus ihm heraus.
     :deep(), da Leaflet dieses Element dynamisch selbst ins DOM einfügt */
  :deep(.map-attribution-control) {
    position: fixed !important;
    left: 10px !important; /* identisch mit .btn_map_info, damit die linke Kante zusammenfällt */
    bottom: calc(var(--safe-bottom) + var(--tab-bar-height) + 28px) !important; /* gleiche Zeile wie .btn_map_info */
    margin: 0 !important;
    box-sizing: border-box;
    height: 34px; /* exakt so hoch wie .btn_map_info, statt größer/versetzt zu wirken */
    width: fit-content;
    max-width: calc(100vw - 20px); /* nie über den Bildschirmrand hinaus, aber sonst textbreit */
    display: flex;
    align-items: center;
    background: var(--color-bg-card) !important; /* !important gegen Leaflets eigene .leaflet-control-attribution-Regel (gleiche Spezifität) */
    color: var(--color-text-muted) !important;
    font-size: 12px;
    padding: 0 16px 0 42px; /* links Platz für den Button (34px + 8px Abstand), vertikal zentriert per flex */
    border-radius: 17px; /* halbe Höhe = Pillenform, passend zur 34px-Höhe */
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
    /* Eine Zeile, die exakt in die 34px-Höhe passt, statt bei Umbruch die Box höher zu
       machen als den Button. !important gegen Leaflets eigenes nowrap/Ladereihenfolge-Zufall */
    white-space: nowrap !important;
    word-spacing: 0.15em;
    letter-spacing: 0.01em;
    overflow: hidden; /* verhindert Text-Reste außerhalb der Pille, v.a. beim Zuklappen */
    z-index: 499; /* knapp unter dem Button (500/1001), damit der optisch obenauf/"in" der Leiste liegt */
    opacity: 0;
    transform-origin: left center; /* wächst von der dem Button zugewandten Kante nach rechts */
    transform: scaleX(0);
    pointer-events: none;
    transition: opacity 0.25s ease, transform 0.25s ease;
  }
  :deep(.map-attribution-control.is-visible) {
    opacity: 1;
    transform: scaleX(1);
    pointer-events: auto;
  }
  :deep(.map-attribution-control a) {
    color: var(--color-primary);
    font-weight: 600;
    text-decoration: none;
    margin: 0 2px;
  }
  :deep(.map-attribution-control img) {
    vertical-align: middle;
    margin-left: 4px;
  }

  /* Glow-Effekt für die personalisierte Standard-Heatmap (drawUserMap.js) - Klasse wird nur
     dort vergeben, nie in der Puls/Tempo/Watt-Ansicht, bleibt also sauber auf sie beschränkt.
     Farbe kommt aus --heatmap-glow-color (per Element gesetzt), da Leaflet nur `stroke` setzt
     und `currentColor` daher nicht die Linienfarbe träfe. */
  :deep(.heatmap-glow) {
    filter: drop-shadow(0 0 3.2px var(--heatmap-glow-color, #ff0000))
            drop-shadow(0 0 6.4px var(--heatmap-glow-color, #ff0000));
  }

  :deep(.photo-pin-dot) {
    position: relative;
    width: 32px;
    height: 32px;
    border-radius: 50%;
    background-color: var(--color-primary);
    color: var(--color-on-primary);
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.35);
    border: 2px solid var(--color-bg-card);
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
    background-color: var(--color-danger);
    color: var(--color-on-primary);
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
  /* Muss unter dem Solo/Group-Toggle (top: app-header-height + 12px, height: 40px)
     durchrutschen, sonst überlappen sich beide - gleicher Versatz wie beim
     .group-dropdown, das direkt unter dem Toggle sitzt. */
  top: calc(var(--safe-top) + var(--app-header-height) + 75px);
  left: 50%;
  transform: translateX(-50%);
  max-width: calc(100% - 140px);
  z-index: 900;
  display: flex;
  align-items: center;
  gap: 10px;
  background-color: var(--color-primary);
  color: var(--color-on-primary);
  padding: 10px 14px;
  border-radius: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.25);
  font-size: 13px;
  }

  /* Auf dem Handy darf der Banner näher an die Bildschirmränder gehen als auf
     Desktop-Breite (dort bleibt der größere Rand von 140px erhalten) */
  @media (max-width: 767px) {
    .pin-mode-banner {
      max-width: calc(100% - 32px);
    }
  }

  .pin-mode-banner-close {
    flex-shrink: 0;
    width: 22px;
    height: 22px;
    border: none;
    border-radius: 50%;
    background-color: rgba(255, 255, 255, 0.25);
    color: var(--color-on-primary);
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
    bottom: calc(var(--safe-bottom) + var(--tab-bar-height) + 32px);
    right: 10px;
    z-index: 500;
    display: flex;
    flex-direction: column;
    align-items: center;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    background-color: var(--color-bg-card);
    border: 1.5px solid var(--color-primary);
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
    background-color: var(--color-bg-card);
    color: var(--color-primary);
    transition: color 0.2s ease;
  }

  .btn_ebenen_preview {
    bottom: calc(var(--safe-bottom) + var(--tab-bar-height) + 138px);
    right: 10px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    border: 1.5px solid var(--color-primary);
  }

  /* Info-Button für den Kartennachweis: unten links, unterhalb der Maßstabsanzeige,
     dezent (kleiner + blasser als die übrigen Karten-Buttons) */
  .btn_map_info {
    position: absolute;
    bottom: calc(var(--safe-bottom) + var(--tab-bar-height) + 28px);
    left: 10px;
    /* Muss über Leaflets eigenem Ecken-Container liegen: .leaflet-bottom.leaflet-left
       (in dem die Attribution-Leiste steckt) hat per Leaflet-Standard-CSS z-index:1000 -
       das schlägt jedes kleinere z-index hier, unabhängig vom z-index der Leiste selbst */
    z-index: 1001;
    width: 34px;
    height: 34px;
    border: 1.5px solid var(--color-primary);
    outline: none;
    appearance: none;
    -webkit-appearance: none;
    border-radius: 50%;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    background-color: rgba(var(--color-bg-card-rgb), 0.92);
    color: var(--color-text-muted);
    box-shadow: 0 2px 6px rgba(0, 0, 0, 0.25);
    transition: background-color 0.25s ease, color 0.25s ease, transform 0.25s ease;
  }

  .btn_map_info:active {
    transform: scale(0.92);
  }

  .btn_map_info.active {
    background-color: var(--color-primary);
    color: var(--color-on-primary);
    box-shadow: 0 2px 10px rgba(var(--color-primary-rgb), 0.5);
  }

  .pill-divider {
    width: 24px;
    height: 1px;
    background: var(--color-border);
  }

  .btn_pin_mode.active {
    color: var(--color-text-muted);
  }

  /* --- NEUES STYLING FÜR DEN TOGGLE SWITCH --- */
  .toggle-switch-container {
    position: absolute;
    top: calc(var(--safe-top) + var(--app-header-height) + 12px); /* unter dem fixierten AppHeader */
    right: 10px; /* Ganz am rechten Bildschirmrand, wie die übrigen Karten-Buttons */
    z-index: 9999;
    background-color: var(--color-bg-card);
    border-radius: 30px;
    border: 1.5px solid var(--color-primary);
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
    color: var(--color-text-muted);
    z-index: 2; /* Hält den Text über dem grünen Slider */
    transition: color 0.3s ease;
  }

  .toggle-option.active {
    color: var(--color-on-primary); /* Schrift wird weiß, wenn der farbige Slider darunter liegt */
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
    top: calc(var(--safe-top) + var(--app-header-height) + 60px); /* direkt unter dem Toggle-Switch */
    right: 10px;
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
    background-color: var(--color-bg-card);
    border: none;
    border-radius: 20px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.3);
    font-size: 13px;
    font-weight: 600;
    color: var(--color-text);
    cursor: pointer;
    transition: border-radius 0.15s ease;
  }

  /* Übersichtslasche "^" */
  .btn_lasche {
    position: absolute;
    bottom: 0px;
    z-index: 9999; /* Button mit höchstem z-Index => garantiert immer sichtbar */
    left: 50%;
    transform: translateX(-50%);
    
    color: #e8e8e8;
    font-size: 16px;
    font-weight: 600;
    
    background-color: var(--color-primary);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px 16px 0 0;
    
    height: 34px;
    width: calc(100% - 1000px);
    
    display: flex;
    align-items: center;
    justify-content: center;
    
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    transition: background-color 0.15s ease;
  }

  @media (max-width: 480px) {
      .btn_lasche {
        width: calc(100% - 100px);
        font-size: 14px;
        height: 32px;
    }
  }

  .btn_lasche:hover {
    background-color: var(--color-primary-dark);
  }

  .btn_lasche:active {
    background-color: var(--color-primary);
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
    fill: var(--color-text-muted);
    transition: transform 0.2s ease;
  }

  .chevron-icon.rotated {
    transform: rotate(180deg);
  }

  .star-icon {
    width: 15px;
    height: 15px;
    flex-shrink: 0;
    fill: var(--color-warning);
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
    background-color: var(--color-bg-card);
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
    color: var(--color-text);
    cursor: pointer;
    transition: background-color 0.15s ease;
  }

  /* Übersichtslasche "^" */
  .btn_lasche {
    position: absolute;
    bottom: 0px;
    z-index: 9999; /* Button mit höchstem z-Index => garantiert immer sichtbar */
    left: 50%;
    transform: translateX(-50%);
    
    color: #e8e8e8;
    font-size: 16px;
    font-weight: 600;
    
    background-color: var(--color-primary);
    border: 1px solid rgba(255, 255, 255, 0.08);
    border-radius: 16px 16px 0 0;
    
    height: 34px;
    width: calc(100% - 1000px);
    
    display: flex;
    align-items: center;
    justify-content: center;
    
    cursor: pointer;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.3);
    transition: background-color 0.15s ease;
  }

  @media (max-width: 480px) {
      .btn_lasche {
        width: calc(100% - 100px);
        font-size: 14px;
        height: 32px;
    }
  }

  .btn_lasche:hover {
    background-color: var(--color-primary-dark);
  }

  .btn_lasche:active {
    background-color: var(--color-primary);
  }
  .group-dropdown-item:hover {
    background-color: var(--color-bg-hover);
  }

  .group-dropdown-item.selected {
    background-color: var(--color-primary-soft);
    color: var(--color-primary);
    font-weight: 600;
  }

</style>