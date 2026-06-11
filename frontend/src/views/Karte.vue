<script setup>

import { onMounted, ref } from 'vue' //onmounted, da Karte erst nach dem Laden der Seite angezeigt werden soll -- ref, da showModal eine reaktive Variable ist, die den Zustand des Modals steuert
import L from 'leaflet'
import velotagLogo from '@/assets/velotag-logo.png'
import GpxUploadModal from '@/components/GpxUploadModal.vue'
import stravaLogo from '@/assets/api_logo_pwrdBy_strava_horiz_orange.png'
import { drawUserMap } from '@/composables/drawUserMap.js' //Import der Funktion zum Zeichnen der Karte mit den Strecken des User

const showModal = ref(false);//ref packt eine "dumme" HTML Variable in eine "Überwachungsbox", damit Vue weiß, wenn sich der Wert durch Anklicken des Buttons ändert

onMounted(() => {
 
  const map = L.map('map').setView([50.0963, 8.2195], 11)//const, da Karte nicht verändert wird, nur aktualisiert

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
  new WatermarkControl({ position: 'topright' }).addTo(map);

  
  L.control.scale({
    metric: true, 
    imperial: false, 
    position: 'bottomleft' 
  }).addTo(map);

  
 //Einbinden der OpenStreetMap-Kartenkacheln, damit die Karte angezeigt wird
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', { //https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png // https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png //'https://tile.openstreetmap.org/{z}/{x}/{y}.png'
    maxZoom: 19,
    color: 'black',
    attribution: `&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, © CARTO | <img src="${stravaLogo}" height="10"/>` //Rechtlicher Hinweis auf Nutzung der OpenStreetMap-Daten
  }).addTo(map)

// Karte aktualisieren, Leaflet zeigt Karte schneller an, als Vue die Karte rendert und die CSS-Datei geladen hat (siehe main.js)
// daher muss die Karte hier manuell aktualisiert werden, damit sie korrekt angezeigt wird
  setTimeout(() => {
    map.invalidateSize()
  }, 100)

  // Routen aus dem Backend abfragen
  drawUserMap(map) //Übergabe der Karte an die Funktion, damit die Routen darauf gezeichnet werden können

})

</script>

<template>
  <div id="map"></div>
  <button class="btn_popup" @click="showModal = true">+</button>

  <GpxUploadModal v-if="showModal" @close="showModal = false" />
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
</style>