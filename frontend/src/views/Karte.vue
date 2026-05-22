<script setup>

import { onMounted } from 'vue'
import L from 'leaflet'
import velotagLogo from '@/assets/velotag-logo.png'

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
</template>

<style scoped>
/* Karte nimmt kompletten Bildschirm ein*/
#map { 
  height: 100vh; 
  width: 100%;
}
</style>