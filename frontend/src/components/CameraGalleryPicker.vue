<script setup>
import { computed } from 'vue';
import { Camera } from '@capacitor/camera';
import { Capacitor } from '@capacitor/core';

const props = defineProps({
    disabled: { type: Boolean, default: false },
    hasPhotos: { type: Boolean, default: false },
    multiple: { type: Boolean, default: true },
    singular: { type: Boolean, default: false } // Einzahl-Beschriftung, z.B. fürs Onboarding-Profilbild
});
const emit = defineEmits(['photos-added']);

const photoLabel = computed(() => {
    if (props.singular) return props.hasPhotos ? 'Foto ändern' : 'Foto auswählen';
    return props.hasPhotos ? 'Weitere Fotos hinzufügen' : 'Fotos auswählen';
});

// Auf dem Handy übernimmt das Camera-Plugin die Auswahl (nativer Dialog, Kamera inklusive).
// Im Browser bleibt es beim <input type="file">, dort gäbe es sonst @ionic/pwa-elements als Abhängigkeit
const isNative = Capacitor.isNativePlatform();

// Das Plugin liefert nur einen webPath - daraus eine echte File machen, damit der
// Upload im Modal unverändert mit FormData weiterarbeiten kann
const photoFromWebPath = async (webPath) => {
    if (!webPath) return null;   // webPath ist laut Plugin-Typ optional
    const blob = await (await fetch(webPath)).blob();
    return {
        file: new File([blob], `foto-${Date.now()}.jpg`, { type: blob.type || 'image/jpeg' }),
        previewUrl: URL.createObjectURL(blob)
    };
};

const takePhoto = async () => {
    try {
        const photo = await Camera.takePhoto({ quality: 80, correctOrientation: true });
        const added = await photoFromWebPath(photo.webPath);
        if (added) emit('photos-added', [added]);
    } catch (e) {
        // Bricht der User die Kamera ab, wirft das Plugin ebenfalls - das ist kein Fehler
        console.debug('Kamera abgebrochen oder nicht verfügbar:', e);
    }
};

const pickFromGallery = async () => {
    try {
        const { results } = await Camera.chooseFromGallery({
            allowMultipleSelection: props.multiple,
            quality: 80,
            correctOrientation: true
        });
        const added = [];
        for (const photo of results) {
            const converted = await photoFromWebPath(photo.webPath);
            if (converted) added.push(converted);
        }
        if (added.length) emit('photos-added', added);
    } catch (e) {
        console.debug('Galerie-Auswahl abgebrochen:', e);
    }
};

const onFilesSelected = (event) => {
    const files = Array.from(event.target.files || []);
    const added = files.map(file => ({
        file,
        previewUrl: URL.createObjectURL(file)
    }));
    event.target.value = '';
    if (added.length) emit('photos-added', added);
};
</script>

<template>
    <slot
        :is-native="isNative"
        :take-photo="takePhoto"
        :pick-from-gallery="pickFromGallery"
        :on-files-selected="onFilesSelected"
    >
        <!-- Fallback: Standard-Aussehen, wenn kein eigener Slot-Inhalt übergeben wird -->
        <div v-if="isNative" class="photo-picker-row">
            <button type="button" class="photo-picker-button" :disabled="disabled" @click="takePhoto">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
                    <path d="M480-260q75 0 127.5-52.5T660-440q0-75-52.5-127.5T480-620q-75 0-127.5 52.5T300-440q0 75 52.5 127.5T480-260Zm0-80q-42 0-71-29t-29-71q0-42 29-71t71-29q42 0 71 29t29 71q0 42-29 71t-71 29ZM160-120q-33 0-56.5-23.5T80-200v-480q0-33 23.5-56.5T160-760h126l74-80h240l74 80h126q33 0 56.5 23.5T880-680v480q0 33-23.5 56.5T800-120H160Zm0-80h640v-480H638l-73-80H395l-73 80H160v480Zm320-240Z"/>
                </svg>
                <span>Foto aufnehmen</span>
            </button>

            <button type="button" class="photo-picker-button" :disabled="disabled" @click="pickFromGallery">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
                    <path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h560q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H200Zm0-80h560v-560H200v560Zm40-80h480L570-480 450-320l-90-120-120 160Zm-40 80v-560 560Z"/>
                </svg>
                <span>Aus Galerie wählen</span>
            </button>
        </div>

        <template v-else>
            <input type="file" accept="image/*" :multiple="multiple" id="photo-upload" :disabled="disabled" @change="onFilesSelected" />
            <label for="photo-upload" class="photo-picker-button">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
                    <path d="M480-260q75 0 127.5-52.5T660-440q0-75-52.5-127.5T480-620q-75 0-127.5 52.5T300-440q0 75 52.5 127.5T480-260Zm0-80q-42 0-71-29t-29-71q0-42 29-71t71-29q42 0 71 29t29 71q0 42-29 71t-71 29ZM160-120q-33 0-56.5-23.5T80-200v-480q0-33 23.5-56.5T160-760h126l74-80h240l74 80h126q33 0 56.5 23.5T880-680v480q0 33-23.5 56.5T800-120H160Zm0-80h640v-480H638l-73-80H395l-73 80H160v480Zm320-240Z"/>
                </svg>
                <span>{{ photoLabel }}</span>
            </label>
        </template>
    </slot>
</template>

<style scoped>
#photo-upload {
    display: none;
}

/* Kamera und Galerie nebeneinander (nur auf dem Handy) */
.photo-picker-row {
    display: flex;
    gap: 8px;
}

.photo-picker-row .photo-picker-button {
    flex: 1;
    flex-direction: column;
    gap: 4px;
    font-size: 13px;
}

.photo-picker-button {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    padding: 12px;
    border: 1px dashed var(--color-border, #b3b3b3);
    border-radius: 8px;
    background-color: var(--color-bg-page, #f9f9f9);
    color: var(--color-text, #1a1a1a);
    cursor: pointer;
    font-size: 14px;
    transition: border-color 0.15s, color 0.15s;
}

.photo-picker-button:hover {
    border-color: var(--color-primary, #3db897);
    color: var(--color-primary, #3db897);
}

.photo-picker-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.photo-picker-button svg {
    width: 22px;
    height: 22px;
}
</style>