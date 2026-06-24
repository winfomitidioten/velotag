import { ref, shallowRef } from 'vue'
import L from 'leaflet'
import stravaLogo from '@/assets/api_logo_pwrdBy_strava_horiz_orange.png'
import voyagerPreview from '@/assets/previews_layer/layer1.png'
import hybridPreview from '@/assets/previews_layer/layerHybrid.png'
import greyPreview from '@/assets/previews_layer/layerGrey.png'

// Die Layer-Definitionen als Array von Objekten, wie von dir gewünscht.
const availableLayers = [
    {
        id: 'voyager',
        name: 'Standard',
        url: 'https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png',
        attribution: `&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attributions">CARTO</a> | <img src="${stravaLogo}" height="10"/>`,
        preview: voyagerPreview
    },
    {
        id: 'hybrid', // Hinweis: Diese URL lädt die Standard-OSM-Karte, keinen echten "Hybrid" (Satellit)
        name: 'OpenStreetMap',
        url: 'https://tile.openstreetmap.org/{z}/{x}/{y}.png',
        attribution: `&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors | <img src="${stravaLogo}" height="10"/>`,
        preview: hybridPreview
    },
    {
        id: 'grey',
        name: 'Graustufen',
        url: 'https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png',
        attribution: `&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, &copy; <a href="https://carto.com/attributions">CARTO</a> | <img src="${stravaLogo}" height="10"/>`,
        preview: greyPreview
    }
];

// Globaler Zustand für die Karte, der von allen Komponenten geteilt wird
const mapInstance = shallowRef(null);
const currentTileLayer = shallowRef(null);
export const activeLayerId = ref(availableLayers[0].id); // Standardmäßig der erste Layer

// Diese Funktion stellt sicher, dass der Zustand über die ganze App hinweg geteilt wird.
export function useMap() {

    const initializeMap = (elementId) => {
        if (mapInstance.value) {
            return mapInstance.value;
        }

        const map = L.map(elementId).setView([50.0963, 8.2195], 11);
        mapInstance.value = map;
        
        // Setze den initialen Layer
        setLayer(activeLayerId.value);

        // Füge weitere Steuerelemente hinzu
        L.control.scale({
            metric: true,
            imperial: false,
            position: 'bottomleft'
        }).addTo(map);

        return map;
    };

    const setLayer = (layerId) => {
        const layerConfig = availableLayers.find(l => l.id === layerId);
        if (!layerConfig || !mapInstance.value) {
            console.error("Layer-Konfiguration nicht gefunden oder Karte nicht initialisiert.");
            return;
        }

        if (currentTileLayer.value) {
            mapInstance.value.removeLayer(currentTileLayer.value);
        }

        const newLayer = L.tileLayer(layerConfig.url, {
            maxZoom: 19,
            attribution: layerConfig.attribution
        }).addTo(mapInstance.value);

        currentTileLayer.value = newLayer;
        activeLayerId.value = layerId;
    };

    return {
        initializeMap,
        setLayer,
        availableLayers,
        activeLayerId
    };
}