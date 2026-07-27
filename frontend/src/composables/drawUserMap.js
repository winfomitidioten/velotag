import { watch } from 'vue'
import api from '@/api/api'
import L from 'leaflet'
import { activeLayerId } from '@/composables/useMap.js'
import { decodePolyline } from './polyline'
import { clearPerformanceMap } from '@/composables/drawPerformanceMap.js'
import { startDraw, isStaleDraw } from '@/composables/mapDrawGeneration.js'

// Summiert die Punktabstände einer Polyline in Metern
const calculateRouteDistance = (coordinates) => {
    let distance = 0;
    for (let i=1; i<coordinates.length; i++) {
        distance += L.latLng(coordinates[i - 1]).distanceTo(L.latLng(coordinates[i]));
    }
    return distance;
}

let currentFeatureGroup = null;
let unwatchColor = null;
let colorWatchStarted = false;

    let totalDistanceMeters= 0

export function clearUserMap(map) {
    if (currentFeatureGroup) {
        map.removeLayer(currentFeatureGroup);
        currentFeatureGroup = null;
    }
}

export async function drawUserMap(map, isGroupViewStatus, groupId = null) {//async
    const myGeneration = startDraw(); // Erkennt veraltete Aufrufe, falls währenddessen umgeschaltet wird
    clearPerformanceMap(map); // Leistungs-Ansicht ausblenden, falls gerade aktiv

    let routes = [];
    let numberOfRoutes = 0;
    let geoJsonLayer = null;

    const colourLine = activeLayerId.value === 'hybrid' ? 'blue' : 'red';

    if(isGroupViewStatus === false) {//Solo Ansicht
        const response = await api.get('routes/map/');
        routes = response.data; // Kiste mit Solo-Routen befüllen
        numberOfRoutes = routes.length;
        console.log("Routen aus Django (Solo):", routes);
    }

    else if (isGroupViewStatus === true) {
        if (!groupId) {
            console.error("Gruppenansicht aktiv, aber keine group_id übergeben!");
            return;
        }

        try {
            const response = await api.get(`groups/${groupId}/intersections/`);
            const geojsonData = response.data;
            console.log(`Schnittmengen aus Django (Gruppe ${groupId}):`, geojsonData);

            const numberOfGroupRoutes = (geojsonData.features && geojsonData.features.length) 
                ? geojsonData.features.length 
                : 1;

            geoJsonLayer = L.geoJSON(geojsonData, {
                style: {
                    color: colourLine,
                    weight: 4,          // Zeichnet genau EINE 4px dicke Linie in der Mitte!
                    opacity: Math.max(0.05, 1 / numberOfGroupRoutes),
                    lineJoin: 'round',
                    lineCap: 'round'
                },
                onEachFeature: (feature, layer) => {
                    if (feature.properties && feature.properties.date) {
                        layer.bindPopup(`<b>Gemeinsame Gruppenroute</b><br>Datum: ${feature.properties.date}`);
                    }
                }
            });
        } catch (err) {
            console.error("Fehler beim Laden der Gruppen-Schnittmengen:", err);
            return;
        }
    }

    // Veraltete Anfrage: Während des Fetches wurde bereits eine neuere Zeichenanfrage gestartet
    // (z.B. schnelles Umschalten Solo/Group/Leistung) - nichts mehr an der Karte ändern.
    if (isStaleDraw(myGeneration)) return;

    if (currentFeatureGroup) {
        map.removeLayer(currentFeatureGroup);//Entfernt alte Routen bevor neue geladen werden
    }
    currentFeatureGroup = L.featureGroup().addTo(map);

    if (geoJsonLayer) {
        currentFeatureGroup.addLayer(geoJsonLayer);
    }

    routes.forEach(route => {
        const polylineEncoded = route.polyline_map;
        const coordinates = decodePolyline(polylineEncoded);
        totalDistanceMeters += calculateRouteDistance(coordinates)
        // Initiale Farbe beim ersten Laden ermitteln
        //let colourLine = activeLayerId.value === 'hybrid' ? 'blue' : 'red';

        const polyline = L.polyline(coordinates, 
            {color: colourLine,     // Grundfarbe
             weight: 4,            // Breite
             opacity: Math.max(0.03, 1 / numberOfRoutes),//Logik der Heatmap: Addiert sich auf 
             // + relativ anhand der Routenanzahl vom Profil
             lineJoin: 'round',    // Weiche Kurven
             lineCap: 'round'//,     // Abgerundete Enden}
        }).addTo(map);//color: 'blue'
        currentFeatureGroup.addLayer(polyline);
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
    });

    return {
        rideCount: numberOfRoutes,
        totalkm: Math.round(totalDistanceMeters/1000)
    }
}