import { ref, watch } from 'vue'
import api from '@/api/api'
import L from 'leaflet'
import { activeLayerId } from '@/composables/useMap.js'
import { decodePolyline } from './polyline'

// Summiert die Punktabstände einer Polyline in Metern
const calculateRouteDistance = (coordinates) => {
    let distance = 0;
    for (let i=1; i<coordinates.length; i++) {
        distance += L.latLng(coordinates[i - 1]).distanceTo(L.latLng(coordinates[i]));
    }
    return distance;
}

export async function drawUserMap(map) {//async 
    const response = await api.get('routes/map/')
    const routes = response.data
    const numberOfRoutes = routes.length
    console.log("Routen aus Django:", routes)//Testausgabe, um API Call zu überprüfenw
    const featureGroup = L.featureGroup().addTo(map)

    let totalDistanceMeters= 0



    routes.forEach(route => {
        const polylineEncoded = route.polyline_map;
        const coordinates = decodePolyline(polylineEncoded);
        totalDistanceMeters += calculateRouteDistance(coordinates)
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

    watch(activeLayerId, (newLayerId) => {
        // Neue Farbe basierend auf der neuen ID ermitteln
        const newColor = newLayerId === 'hybrid' ? 'blue' : 'red';
        
        // Durch alle gezeichneten Linien in der FeatureGroup iterieren 
        // und die Leaflet-Methode setStyle() aufrufen
        featureGroup.eachLayer((layer) => {
            layer.setStyle({ color: newColor });
        });
    });

    return {
        rideCount: numberOfRoutes,
        totalkm: Math.round(totalDistanceMeters/1000)
    }
}