import { ref } from 'vue'
import api from '@/api/api'
import L from 'leaflet'
import { calculateRouteDistance } from '@/composables/polyline'


export function useGPXVerarbeitung() {

  const isDragging = ref(false)
  const errorMessage = ref('')
  const erfolgsMessage = ref('')
  const selectedGroupIds = ref([]) // NEU: Speichert die IDs direkt im Composable

  // --- DIE ELEGANTE LÖSUNG: Der native Polyline-Encoder ---
  // Diese Helfer-Funktion komprimiert das Array, ohne externe Pakete zu brauchen
  const encodePolyline = (coordinates) => {
    let result = '';
    let prevLat = 0;
    let prevLng = 0;

    for (let i = 0; i < coordinates.length; i++) {
      let lat = Math.round(coordinates[i][0] * 1e5);
      let lng = Math.round(coordinates[i][1] * 1e5);
      let dLat = lat - prevLat;
      let dLng = lng - prevLng;
      prevLat = lat;
      prevLng = lng;

      const encodeValue = (value) => {
        value = value < 0 ? ~(value << 1) : (value << 1);
        let encoded = '';
        while (value >= 0x20) {
          encoded += String.fromCharCode((0x20 | (value & 0x1f)) + 63);
          value >>= 5;
        }
        encoded += String.fromCharCode(value + 63);
        return encoded;
      };

      result += encodeValue(dLat) + encodeValue(dLng);
    }
    return result;
  }
  // ---------------------------------------------------------

  const onFileDrop = (event) => { // Parameter für die Gruppe entfernt, wir nehmen direkt die ref
    isDragging.value = false 
    errorMessage.value = '' // Setzt Fehlermeldungen bei neuem Versuch zurück
    erfolgsMessage.value = '' // Setzt Erfolgsmeldungen bei neuem Versuch zurück  
    
    // Nimmt Dateien entweder vom Drag & Drop (dataTransfer) oder vom FileChooser (target)
    const files = event.dataTransfer?.files || event.target?.files;
    
    if (files && files.length > 0) {
      const uploadedFile = files[0];
      
      if (uploadedFile.name.endsWith('.gpx')) {
        console.log("GPX-Datei erkannt:", uploadedFile.name);
        
        const reader = new FileReader();

        reader.onload = async (e) => {
          console.log("Leuchtturm 1: FileReader hat die Datei geöffnet.");
          
          try {
    
            const gpxContent = e.target.result; 
            const parser = new DOMParser();
            const xmlDoc = parser.parseFromString(gpxContent, "text/xml");
            console.log("XML wurde geparst.");
            const activityType = xmlDoc.querySelector('type');
            // Wirft den Fehler, wenn das Tag fehlt ODER der Inhalt NICHT "cycling" ist
            if (!activityType || activityType.textContent !== "cycling") {
              throw new Error("Die hochgeladene GPX-Datei enthält keine Radfahraktivität!");
            }

            const coordinates = [];
            const pulsStream = [];
            const zeitStream = [];
            const wattStream = [];

            const trackPoints = xmlDoc.querySelectorAll('trkpt');
            console.log(`${trackPoints.length} Trackpunkte gefunden.`);

            trackPoints.forEach(pt => {
              const lat = parseFloat(pt.getAttribute('lat'));
              const lon = parseFloat(pt.getAttribute('lon'));
              coordinates.push([lat, lon]);

              const timeNode = pt.querySelector('time');
              zeitStream.push(timeNode ? timeNode.textContent : null);

              const hrNode = pt.getElementsByTagNameNS('*', 'hr')[0];
              pulsStream.push(hrNode ? parseInt(hrNode.textContent) : null);

              const powerNode = pt.querySelector('power') || pt.getElementsByTagNameNS('*', 'power')[0];
              wattStream.push(powerNode ? parseInt(powerNode.textContent) : null);
            });
            console.log("Schleife beendet, extrahiere Geodaten...");

            const distanceMeters = calculateRouteDistance(coordinates);
            const polylineMapString = encodePolyline(coordinates);
            console.log("Polyline komprimiert.");

            const startTime = zeitStream[0] ? new Date(zeitStream[0]).toISOString() : null;
            const endTime = zeitStream[zeitStream.length - 1] ? new Date(zeitStream[zeitStream.length - 1]).toISOString() : null;
            
            const postgisCoordinates = coordinates.map(coord => [coord[1], coord[0]]);//Leaflet nutzt [Lat, Lng], PostGIS erwartet [Lng, Lat]
            
            const payload = {
      
              strecken_name: uploadedFile.name.replace('.gpx', ''), 
              group_id: selectedGroupIds.value, // Die aktuell ausgewählten IDs aus der ref ziehen
              polyline_map: polylineMapString,
              distance_meters: distanceMeters,
              puls_stream: pulsStream,
              zeit_stream: zeitStream,
              watt_stream: wattStream,
              start_time: startTime,
              end_time: endTime,
              coordinates: postgisCoordinates
            };
            console.log("Paket geschnürt. Schicke an Django...", payload);

            // Der eigentliche API-Call
            const response = await api.post('routes/create/', payload);

            console.log("ERFOLG! Antwort von Django:", response.data);            
            //alert("Die Strecke wurde erfolgreich gespeichert!");
            erfolgsMessage.value = "Die Strecke wurde erfolgreich gespeichert!";
            window.location.reload(); // Seite neu laden, damit die neue Route auf der Karte erscheint
            

            
          } catch (error) {
            // Wenn IRGENDWAS zwischen Leuchtturm 1 und 7 schiefgeht, landet es HIER:
            console.error("FATALER FEHLER IM ABLAUF:", error);
            errorMessage.value = "Beim Verarbeiten der GPX-Datei ist ein Fehler aufgetreten. Bitte lade nur Radfahraktivitäten hoch!!";
          }
        };

        reader.readAsText(uploadedFile);

      } else {
        errorMessage.value = "Fehler: Bitte lade nur eine echte .gpx-Datei hoch!";
      }
    }
  }

  return {
    isDragging,
    onFileDrop,
    errorMessage,
    erfolgsMessage,
    selectedGroupIds // NEU: exportieren, damit das Modal die Variable befüllen kann
  }
}