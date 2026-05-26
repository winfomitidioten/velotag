<script setup>

import { onMounted, ref } from 'vue' //onmounted, da Karte erst nach dem Laden der Seite angezeigt werden soll -- ref, da showModal eine reaktive Variable ist, die den Zustand des Modals steuert
import L from 'leaflet'
import velotagLogo from '@/assets/velotag-logo.png'

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
  L.tileLayer('https://tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 19,
    attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>' //Rechtlicher Hinweis auf Nutzung der OpenStreetMap-Daten
  }).addTo(map)

// Karte aktualisieren, Leaflet zeigt Karte schneller an, als Vue die Karte rendert und die CSS-Datei geladen hat (siehe main.js)
// daher muss die Karte hier manuell aktualisiert werden, damit sie korrekt angezeigt wird
  setTimeout(() => {
    map.invalidateSize()
  }, 100)

})
</script>

<template>
  <div id="map"></div>
  <button class="btn_popup" @click="showModal = true">+</button>
    <div v-if="showModal" class="popup">
      <div class="popup-content">
        <h2>Fahrt hochladen</h2>
        <p>.gpx Datei auswählen</p>
        <div> 
          <button class = "btn_strava_api">Mit Strava verbinden</button>
        </div>
        <div>
          <button class="btn_upload_manual">Datei auswählen</button>
        </div>
        <button class="btn_close_popup" @click="showModal = false">x</button> <!-- mit @click wird die Funktion showModal = false aufgerufen, wenn der Button angeklickt wird, wodurch das Modal geschlossen wird -->
      </div>
    </div>
</template>

<style scoped>
  /* Karte nimmt kompletten Bildschirm ein*/
  #map { 
    height: 100vh; 
    width: 100%;
  }
  /* Upload Button "+" */
  .btn_popup {
    position: absolute;
    bottom: 20px;
    right: 10px;
    z-index: 1000; /* Damit der Button über der Karte liegt */
    color: white;
    font-size: 30px;
    background-color: var(--color-primary);
    height: 50px;
    width: 50px;
    border-radius: 50%;
    border: none;
  }

  /* PopUp Content*/
  .popup-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
    position: relative;
  }

  .btn_close_popup {
  position: absolute;
  top: -15px;   /* Positioniert den Button am oberen Rand */
  right: -15px; /* Positioniert den Button am rechten Rand */
  z-index: 3000;
  color: white;
  font-size: 24px;
  background-color: var(--color-primary, #dc3545); /* Fallback-Farbe hinzugefügt */
  height: 40px;
  width: 40px;
  border-radius: 50%;
  border: none;
  cursor: pointer;
  display: flex;
  justify-content: center;
  align-items: center;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
  }

  /* Upload PopUp*/
  .popup {
    position: fixed;
    bottom: 20px;
    right: 10px;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5); /* Halbtransparenter Hintergrund */
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1001; /* Damit das Popup über dem Button liegt */
  }

</style>