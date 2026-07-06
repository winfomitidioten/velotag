import { watch } from 'vue'
import api from '@/api/api'
import L from 'leaflet'
import { activeLayerId } from '@/composables/useMap.js'

// Dekodiert den komprimierten String zurück in ein [Lat, Lng] Array
const decodePolyline = (encoded) => {
    const coordinates = [];
    let index = 0, len = encoded.length;
    let lat = 0, lng = 0;

    while (index < len) {
        let b, shift = 0, result = 0;
        do {
            b = encoded.charCodeAt(index++) - 63;
            result |= (b & 0x1f) << shift;
            shift += 5;
        } while (b >= 0x20);
        let dlat = ((result & 1) !== 0 ? ~(result >> 1) : (result >> 1));
        lat += dlat;

        shift = 0;
        result = 0;
        do {
            b = encoded.charCodeAt(index++) - 63;
            result |= (b & 0x1f) << shift;
            shift += 5;
        } while (b >= 0x20);
        let dlng = ((result & 1) !== 0 ? ~(result >> 1) : (result >> 1));
        lng += dlng;

        coordinates.push([lat / 1e5, lng / 1e5]);
    }
    return coordinates;
};

let currentFeatureGroup = null
let colorWatchStarted = false

export async function drawUserMap(map) {//async
    const response = await api.get('routes/map/')
    const routes = response.data
    const numberOfRoutes = routes.length
    console.log("Routen aus Django:", routes)//Testausgabe, um API Call zu überprüfenw

    // Bei erneutem Aufruf (z.B. nach einem Strava-Import) alte Routen erst entfernen,
    // sonst werden sie doppelt gezeichnet
    if (currentFeatureGroup) {
        map.removeLayer(currentFeatureGroup)
    }
    const featureGroup = L.featureGroup().addTo(map)
    currentFeatureGroup = featureGroup

    routes.forEach(route => {
        const polylineEncoded = route.polyline_map;
        const coordinates = decodePolyline(polylineEncoded);
        // Initiale Farbe beim ersten Laden ermitteln
        let colourLine = activeLayerId.value === 'hybrid' ? 'blue' : 'red';

        const polyline = L.polyline(coordinates, 
            {color: colourLine,     // Grundfarbe
             weight: 4,            // Breite
             opacity: Math.max(0.03, 1 / numberOfRoutes),//Logik der Heatmap: Addiert sich auf 
             // + relativ anhand der Routenanzahl vom Profil
             lineJoin: 'round',    // Weiche Kurven
             lineCap: 'round'//,     // Abgerundete Enden}
        }).addTo(map);//color: 'blue'
        featureGroup.addLayer(polyline);
        polyline.bindPopup(`<b>${route.strecken_name}</b>`);//Basis für spätere optionale Blog-Ansicht
    });

    // Nur einmal registrieren, sonst sammeln sich bei wiederholtem drawUserMap()-Aufruf
    // (z.B. nach einem Strava-Import) mehrere Watcher an
    if (!colorWatchStarted) {
        colorWatchStarted = true
        watch(activeLayerId, (newLayerId) => {
            // Neue Farbe basierend auf der neuen ID ermitteln
            const newColor = newLayerId === 'hybrid' ? 'blue' : 'red';

            // Immer auf der aktuellen FeatureGroup arbeiten, nicht auf der von der ersten Zeichnung
            currentFeatureGroup?.eachLayer((layer) => {
                layer.setStyle({ color: newColor });
            });
        });
    }
}