import { ref } from 'vue';
import L from 'leaflet';
import api from '@/api/api';
import { feature } from '@turf/turf';

/*
Fotos, die aktuell in der Grid-/Slide-Ansicht angezeigt werden
*/
export const activeGalleryPhotos = ref(null);

let currentPhotoPinGroup = null;

// Wird beim Unmount von Karte.vue aufgerufen: der Verweis ist modulweit und zeigte nach
// einem Remount sonst auf eine Ebene der bereits zerstörten Karte.
export function resetPhotoPinState() {
    currentPhotoPinGroup = null;
    activeGalleryPhotos.value = null;
}

function groupPinsByLocation(pins) {
    const groups = new Map();
    for (const pin of pins) {
        const key = `${pin.latitude.toFixed(6)}, ${pin.longitude.toFixed(6)}`;
        if (!groups.has(key)) {
            groups.set(key, {latitude: pin.latitude, longitude: pin.longitude, photos: [] });
        }
        groups.get(key).photos.push(pin);
    }
    return Array.from(groups.values());
}

export async function drawPhotoPins(map, isGroupViewStatus = false, groupId = null) {
    if (currentPhotoPinGroup) {
        map.removeLayer(currentPhotoPinGroup);
        currentPhotoPinGroup = null;
    }

    // Gruppenansicht ohne ausgewählte Gruppe (z.B. noch kein Favorit gesetzt):
    // keine Pins zeichnen, statt auf die "alle Pins"-Liste zurückzufallen
    if (isGroupViewStatus && !groupId) {
        return;
    }

    const url = isGroupViewStatus ? `photo-pins/group/${groupId}/` : 'photo-pins/list/';
    const response = await api.get(url);
    const groups = groupPinsByLocation(response.data);

    const featureGroup = L.featureGroup().addTo(map);
    currentPhotoPinGroup = featureGroup;

    groups.forEach(group => {
        const icon = L.divIcon({
            className: 'photo-pin-marker',
            html: `
                <div class="photo-pin-dot">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor" width="16" height="16">
                        <path d="M480-260q75 0 127.5-52.5T660-440q0-75-52.5-127.5T480-620q-75 0-127.5 52.5T300-440q0 75 52.5 127.5T480-260Zm0-80q-42 0-71-29t-29-71q0-42 29-71t71-29q42 0 71 29t29 71q0 42-29 71t-71 29ZM160-120q-33 0-56.5-23.5T80-200v-480q0-33 23.5-56.5T160-760h126l74-80h240l74 80h126q33 0 56.5 23.5T880-680v480q0 33-23.5 56.5T800-120H160Zm0-80h640v-480H638l-73-80H395l-73 80H160v480Zm320-240Z"/>
                    </svg>
                    ${group.photos.length > 1 ? `<span class="photo-pin-count">${group.photos.length}</span>` : ''}
                </div>
            `,
            iconSize: [32, 32],
            iconAnchor: [16, 16]
        })

        const marker = L.marker([group.latitude, group.longitude], { icon });
        marker.on('click', () => {
            activeGalleryPhotos.value = group.photos;
        })
        featureGroup.addLayer(marker);
    })
}