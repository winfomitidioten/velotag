import { watch } from 'vue'
import api from '@/api/api'
import L from 'leaflet'
import { activeLayerId } from '@/composables/useMap.js'
import { clearPerformanceMap } from '@/composables/drawPerformanceMap.js'
import { startDraw, isStaleDraw } from '@/composables/mapDrawGeneration.js'
import { useHeatmapStyleStore } from '@/store/heatmapStyleStore.js'

// Ermittelt die aktuell wirksame Linienfarbe: eigene Wahl des Nutzers hat Vorrang,
// sonst greift die bisherige Auto-Logik (Blau auf Hybrid ist am besten sichtbar, sonst Rot)
function resolveHeatmapColor(customColor, layerId) {
    return customColor ?? (layerId === 'hybrid' ? 'blue' : 'red')
}

// Überträgt Farbe/Glow auf das erzeugte SVG-Element - rekursiv, da eine L.GeoJSON-Ebene
// (Gruppenansicht) selbst keinen eigenen DOM-Knoten hat, sondern eine Gruppe von Pfaden ist.
// CSS-Custom-Property statt currentColor, da Leaflet nur `stroke` setzt, nicht `color`.
function applyHeatmapPathStyle(layer, color, glowOn) {
    const el = layer.getElement?.()
    if (el) {
        el.style.setProperty('--heatmap-glow-color', color)
        el.classList.toggle('heatmap-glow', glowOn)
    } else if (typeof layer.eachLayer === 'function') {
        layer.eachLayer((sub) => applyHeatmapPathStyle(sub, color, glowOn))
    }
}

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

let currentFeatureGroup = null;
let colorWatchStarted = false;

export function clearUserMap(map) {
    if (currentFeatureGroup) {
        map.removeLayer(currentFeatureGroup);
        currentFeatureGroup = null;
    }
}

export async function drawUserMap(map, isGroupViewStatus, groupId = null) {//async
    const myGeneration = startDraw(); // Erkennt veraltete Aufrufe, falls währenddessen umgeschaltet wird
    clearPerformanceMap(map); // Leistungs-Ansicht ausblenden, falls gerade aktiv

    const heatmapStyle = useHeatmapStyleStore();

    let routes = [];
    let numberOfRoutes = 0;
    let geoJsonLayer = null;

    const colourLine = resolveHeatmapColor(heatmapStyle.heatmapColor, activeLayerId.value);
    const glowOn = heatmapStyle.heatmapGlowEnabled;

    if(isGroupViewStatus === false) {//Solo Ansicht
        const response = await api.get('routes/map/');
        routes = response.data; // Kiste mit Solo-Routen befüllen
        numberOfRoutes = routes.length;
        console.log("Routen aus Django (Solo):", routes);
    }

    else if (isGroupViewStatus === true) {
        if (!groupId) {
            console.error("Gruppenansicht aktiv, aber keine group_id übergeben!");
            clearUserMap(map); // Sonst blieben die Solo-Routen der vorigen Ansicht stehen
            return;
        }

        try {
            const response = await api.get(`routes/intersections/${groupId}/`);
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
            clearUserMap(map); // Sonst blieben die Solo-Routen der vorigen Ansicht stehen
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
        applyHeatmapPathStyle(geoJsonLayer, colourLine, glowOn);
    }

    routes.forEach(route => {
        const polylineEncoded = route.polyline_map;
        const coordinates = decodePolyline(polylineEncoded);

        const polyline = L.polyline(coordinates,
            {color: colourLine,     // Grundfarbe
             weight: 4,            // Breite
             opacity: Math.max(0.03, 1 / numberOfRoutes),//Logik der Heatmap: Addiert sich auf
             // + relativ anhand der Routenanzahl vom Profil
             lineJoin: 'round',    // Weiche Kurven
             lineCap: 'round'//,     // Abgerundete Enden}
        }).addTo(map);//color: 'blue'
        currentFeatureGroup.addLayer(polyline);
        applyHeatmapPathStyle(polyline, colourLine, glowOn);
        polyline.bindPopup(`<b>${route.strecken_name}</b>`);//Basis für spätere optionale Blog-Ansicht
    });

    // Nur einmal registrieren, sonst sammeln sich bei wiederholtem drawUserMap()-Aufruf
    // (z.B. nach einem Strava-Import) mehrere Watcher an
    if (!colorWatchStarted) {
        colorWatchStarted = true
        watch(
            [activeLayerId, () => heatmapStyle.heatmapColor, () => heatmapStyle.heatmapGlowEnabled],
            ([newLayerId, customColor, newGlowOn]) => {
                const newColor = resolveHeatmapColor(customColor, newLayerId);

                // Immer auf der aktuellen FeatureGroup arbeiten, nicht auf der von der ersten Zeichnung
                currentFeatureGroup?.eachLayer((layer) => {
                    layer.setStyle({ color: newColor });
                    applyHeatmapPathStyle(layer, newColor, newGlowOn);
                });
            }
        );
    }
}