import { ref } from 'vue'
import api from '@/api/api'
import L from 'leaflet'
import { 
    point, 
    lineString, 
    featureCollection, 
    hexGrid, 
    buffer, 
    booleanIntersects 
} from '@turf/turf';

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

export async function drawUserMap(map) {//async 
    const response = await api.get('routes/read/')
    const routes = response.data
    console.log("Routen aus Django:", routes)//Testausgabe, um API Call zu überprüfen
    const featureGroup = L.featureGroup().addTo(map)



    routes.forEach(route => {
        const polylineEncoded = route.polyline_map;
        const coordinates = decodePolyline(polylineEncoded);
        const polyline = L.polyline(coordinates, 
            {color: 'blue',     // Grundfarbe
             weight: 4,            // Breite
             opacity: 0.05,        // Logik der HeatMap: Addiert sich auf
             lineJoin: 'round',    // Weiche Kurven
             lineCap: 'round'//,     // Abgerundete Enden}
        }).addTo(map);//color: 'blue'
        featureGroup.addLayer(polyline);
        polyline.bindPopup(`<b>${route.strecken_name}</b>`);//Basis für spätere optionale Blog-Ansicht
    });
}