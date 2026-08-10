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

// Fallback, falls dem User (noch) kein Standort hinterlegt ist - identisch zum
// Fallback in initializeMap, damit "Heimatposition" überall dasselbe meint
export const DEFAULT_CENTER = [50.0963, 8.2195];

// Kartennachweis: standardmäßig ausgeblendet, wird erst über den Info-Button in Karte.vue eingeblendet
const isAttributionVisible = ref(false);
let attributionContainer = null; // rohes Leaflet-DOM-Element, kein Vue-Ref nötig

// Diese Funktion stellt sicher, dass der Zustand über die ganze App hinweg geteilt wird.
export function useMap() {

    const initializeMap = (elementId, center) => {
        if (mapInstance.value) {
            return mapInstance.value;
        }

        // Standardmäßig Wiesbaden - Fallback für den Fall, dass dem User (noch) kein
        // Standort hinterlegt ist (z.B. Datenmigrationslücken)
        const startCenter = center ?? DEFAULT_CENTER;

        const map = L.map(elementId, {
            zoomControl: false, // <--- Hier schalten wir die Buttons aus
            attributionControl: false // eigene Attribution unten links statt Leaflets Standard-Ecke unten rechts (kollidiert sonst mit den Karten-Buttons)
            }).setView(startCenter, 11);
        mapInstance.value = map;

        // Setze den initialen Layer
        setLayer(activeLayerId.value);

        // Füge weitere Steuerelemente hinzu
        const scaleControl = L.control.scale({
            metric: true,
            imperial: false,
            position: 'bottomleft'
        }).addTo(map);

        // Kartennachweis (OSM/CARTO-Lizenzpflicht) direkt auf der Karte statt im (inzwischen entfernten) Menü -
        // standardmäßig unsichtbar, wird über den Info-Button in Karte.vue ein-/ausgeblendet (siehe toggleAttribution)
        const attributionControl = L.control.attribution({ position: 'bottomleft' }).addTo(map);
        attributionContainer = attributionControl.getContainer();
        attributionContainer.classList.add('map-attribution-control');

        // Maßstabsleiste nur während des Zoomens einblenden, danach wieder ausblenden
        // (Styling/Positionierung dafür siehe Karte.vue, :deep(.map-scale-control))
        const scaleContainer = scaleControl.getContainer();
        scaleContainer.classList.add('map-scale-control');

        let scaleHideTimeout = null;
        map.on('zoomstart zoom', () => {
            clearTimeout(scaleHideTimeout);
            scaleContainer.classList.add('is-visible');
        });
        map.on('zoomend', () => {
            scaleHideTimeout = setTimeout(() => {
                scaleContainer.classList.remove('is-visible');
            }, 1200);
        });

        return map;
    };

    // Die Karten-Instanz lebt modulweit und überlebt damit einen Remount von Karte.vue
    // (z.B. nach einem Account-Wechsel, siehe sessionKey im userStore). Ohne dieses
    // Aufräumen liefert initializeMap beim nächsten Mount die alte Instanz zurück, die
    // noch am inzwischen entfernten <div id="map"> hängt - die Karte bliebe dann leer,
    // bis die App komplett neu startet.
    const destroyMap = () => {
        if (!mapInstance.value) return;
        mapInstance.value.remove(); // baut Leaflets DOM und Event-Listener ab
        mapInstance.value = null;
        currentTileLayer.value = null;
        attributionContainer = null;
        isAttributionVisible.value = false;
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

    // Fliegt sanft zur Heimatposition zurück (z.B. per Logo-Klick in AppHeader.vue).
    // No-op, solange die Karte noch nie initialisiert wurde.
    const resetToHome = (center) => {
        if (!mapInstance.value) return;
        mapInstance.value.flyTo(center ?? DEFAULT_CENTER, 11, { duration: 1 });
    };

    const setAttributionVisible = (visible) => {
        isAttributionVisible.value = visible;
        if (!attributionContainer) return;
        attributionContainer.classList.toggle('is-visible', visible);

        // Leaflets Ecken-Container (.leaflet-bottom.leaflet-left) trägt per Standard-CSS
        // z-index:1000 und bildet damit einen Stacking-Context. Die Leiste darin kann aus
        // eigener Kraft nie über das Lasche-Sheet (z-index 9999) steigen - egal welchen
        // z-index sie selbst bekommt. Deshalb wird der Container mit angehoben, solange
        // der Nachweis offen ist (Styling siehe .attribution-open in Karte.vue).
        attributionContainer.parentElement?.classList.toggle('attribution-open', visible);
    };

    const toggleAttribution = () => setAttributionVisible(!isAttributionVisible.value);

    // Schließt den Kartennachweis nur, falls er offen ist (z.B. bei einem Klick irgendwo
    // auf die Karte) - im Gegensatz zu toggleAttribution kein Umschalten, damit ein
    // Karten-Klick ihn nicht versehentlich wieder öffnet
    const closeAttribution = () => {
        if (!isAttributionVisible.value) return;
        setAttributionVisible(false);
    };

    // Für Klick-außerhalb-Erkennung (document-weiter Listener in Karte.vue): die Leiste
    // ist ein von Leaflet erzeugtes DOM-Element und daher nicht per Template-Ref erreichbar
    const isAttributionTarget = (target) => {
        return !!(attributionContainer && attributionContainer.contains(target));
    };

    return {
        initializeMap,
        destroyMap,
        setLayer,
        resetToHome,
        availableLayers,
        activeLayerId,
        isAttributionVisible,
        toggleAttribution,
        closeAttribution,
        isAttributionTarget
    };
}