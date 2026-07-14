<script setup>
import { ref, computed } from 'vue';
import { Camera } from '@capacitor/camera';
import { Capacitor } from '@capacitor/core';
import api from '@/api/api';
import BaseModal from '@/components/BaseModal.vue';
import GroupSelectionUploadModal from '@/components/GroupSelectionUploadModal.vue';


const props = defineProps({
    latitude: { type: Number, required: true },
    longitude: { type: Number, required: true }
});
const emit = defineEmits(['close', 'created']);

const selectedPhotos = ref([]);
const description = ref('');
const selectedGroups = ref([]);
const uploading = ref(false);
const error = ref('');

// Auf dem Handy übernimmt das Camera-Plugin die Auswahl (nativer Dialog, Kamera inklusive).
// Im Browser bleibt es beim <input type="file">, dort gäbe es sonst @ionic/pwa-elements als Abhängigkeit
const isNative = Capacitor.isNativePlatform();

const canSubmit = computed(() => selectedPhotos.value.length > 0 && !uploading.value);

const onFilesSelected = (event) => {
    const files = Array.from(event.target.files || []);
    for (const file of files) {
        selectedPhotos.value.push({
            file,
            previewUrl: URL.createObjectURL(file)
        });
    }
    event.target.value = '';
};

// Das Plugin liefert nur einen webPath - daraus eine echte File machen, damit der
// Upload unten unverändert mit FormData weiterarbeiten kann
const addPhotoFromWebPath = async (webPath) => {
    if (!webPath) return;   // webPath ist laut Plugin-Typ optional
    const blob = await (await fetch(webPath)).blob();
    selectedPhotos.value.push({
        file: new File([blob], `foto-${Date.now()}.jpg`, { type: blob.type || 'image/jpeg' }),
        previewUrl: URL.createObjectURL(blob)
    });
};

const takePhoto = async () => {
    try {
        error.value = '';
        const photo = await Camera.takePhoto({ quality: 80, correctOrientation: true });
        await addPhotoFromWebPath(photo.webPath);
    } catch (e) {
        // Bricht der User die Kamera ab, wirft das Plugin ebenfalls - das ist kein Fehler
        console.debug('Kamera abgebrochen oder nicht verfügbar:', e);
    }
};

const pickFromGallery = async () => {
    try {
        error.value = '';
        const { results } = await Camera.chooseFromGallery({
            allowMultipleSelection: true,
            quality: 80,
            correctOrientation: true
        });
        for (const photo of results) {
            await addPhotoFromWebPath(photo.webPath);
        }
    } catch (e) {
        console.debug('Galerie-Auswahl abgebrochen:', e);
    }
};

const removePhoto = (index) => {
    URL.revokeObjectURL(selectedPhotos.value[index].previewUrl);
    selectedPhotos.value.splice(index, 1);
};

const submitPin = async () => {
    if (selectedPhotos.value.length === 0) {
        error.value = 'Bitte wähle zuerst ein Foto aus.';
        return;
    }
    try {
        uploading.value = true;
        error.value = '';
        const formData = new FormData();
        formData.append('latitude', props.latitude);
        formData.append('longitude', props.longitude);
        formData.append('description', description.value);
        selectedGroups.value.forEach(id => formData.append('groups', id));
        selectedPhotos.value.forEach(photo => formData.append('image', photo.file));

        await api.post('photo-pins/create/', formData);
        emit('created');
    } catch (e) {
        console.error('Fehler beim Hochladen:', e);
        error.value = 'Foto konnte nicht gespeichert werden.';
    } finally {
        uploading.value = false;
    };
};

const autoGrow = (event) => {
    const textarea = event.target;
    textarea.style.height = 'auto';
    textarea.style.height = `${textarea.scrollHeight}px`;
}
</script>
<template>
    <!-- busy: während des Uploads lässt sich das Fenster nicht schließen,
         damit der laufende Request nicht versehentlich abgebrochen wird -->
    <BaseModal :busy="uploading" @close="$emit('close')">
        <div class="header">
            <h2>Foto hinzufügen</h2>
        </div>

        <div v-if="error" class="error-message">
            {{ error }}
        </div>

        <div v-if="selectedPhotos.length" class="photo-preview-grid">
            <div v-for="(photo, index) in selectedPhotos" :key="photo.previewUrl" class="photo-preview-item">
                <img :src="photo.previewUrl" class="photo-preview" alt="Ausgewähltes Foto" />
                <button type="button" class="photo-remove-button" :disabled="uploading" @click="removePhoto(index)" aria-label="Foto entfernen">
                    &times;
                </button>
            </div>
        </div>

        <!-- Auf dem Handy: eigene Buttons für Kamera und Galerie. Der Android-WebView
             blendet die Kamera im Datei-Dialog aus, sobald multiple gesetzt ist -->
        <div v-if="isNative" class="photo-picker-row">
            <button type="button" class="photo-picker-button" :disabled="uploading" @click="takePhoto">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
                    <path d="M480-260q75 0 127.5-52.5T660-440q0-75-52.5-127.5T480-620q-75 0-127.5 52.5T300-440q0 75 52.5 127.5T480-260Zm0-80q-42 0-71-29t-29-71q0-42 29-71t71-29q42 0 71 29t29 71q0 42-29 71t-71 29ZM160-120q-33 0-56.5-23.5T80-200v-480q0-33 23.5-56.5T160-760h126l74-80h240l74 80h126q33 0 56.5 23.5T880-680v480q0 33-23.5 56.5T800-120H160Zm0-80h640v-480H638l-73-80H395l-73 80H160v480Zm320-240Z"/>
                </svg>
                <span>Foto aufnehmen</span>
            </button>

            <button type="button" class="photo-picker-button" :disabled="uploading" @click="pickFromGallery">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
                    <path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h560q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H200Zm0-80h560v-560H200v560Zm40-80h480L570-480 450-320l-90-120-120 160Zm-40 80v-560 560Z"/>
                </svg>
                <span>Aus Galerie wählen</span>
            </button>
        </div>

        <!-- Im Browser bleibt es beim klassischen Datei-Dialog -->
        <template v-else>
            <input type="file" accept="image/*" multiple id="photo-upload" :disabled="uploading" @change="onFilesSelected" />
            <label for="photo-upload" class="photo-picker-button">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
                    <path d="M480-260q75 0 127.5-52.5T660-440q0-75-52.5-127.5T480-620q-75 0-127.5 52.5T300-440q0 75 52.5 127.5T480-260Zm0-80q-42 0-71-29t-29-71q0-42 29-71t71-29q42 0 71 29t29 71q0 42-29 71t-71 29ZM160-120q-33 0-56.5-23.5T80-200v-480q0-33 23.5-56.5T160-760h126l74-80h240l74 80h126q33 0 56.5 23.5T880-680v480q0 33-23.5 56.5T800-120H160Zm0-80h640v-480H638l-73-80H395l-73 80H160v480Zm320-240Z"/>
                </svg>
                <span>{{ selectedPhotos.length ? 'Weitere Fotos hinzufügen' : 'Fotos auswählen' }}</span>
            </label>
        </template>
        <textarea v-model="description" class="description-input" placeholder="Beschreibung (optional)" rows="2" :disabled="uploading" @input="autoGrow"></textarea>

        <GroupSelectionUploadModal @update:selected-group="selectedGroups = $event" />

        <button type="button" class="submit-button" :disabled="!canSubmit" @click="submitPin">
            {{ uploading ? 'Wird hochgeladen ...' : 'Foto(s) hinzufügen' }}
        </button>
    </BaseModal>
</template>

<style scoped>
/* Overlay, Box und Schließen-Button kommen aus BaseModal */
.header h2 {
    margin: 20px 0px 20px 0;
}

.error-message {
    background-color: #fee2e2;
    color: #e53e3e;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 15px;
    font-size: 14px;
}

.photo-preview-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin: 15px 0;
}

.photo-preview-item {
    position: relative;
    aspect-ratio: 1 / 1;
}

.photo-preview {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 8px;
}

.photo-remove-button {
    position: absolute;
    top: -6px;
    right: -6px;
    width: 22px;
    height: 22px;
    border-radius: 50%;
    border: none;
    background-color: #e53e3e;
    color: white;
    line-height: 1;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
}

.photo-remove-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

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

.description-input {
    width: 100%;
    box-sizing: border-box;
    padding: 10px;
    border: 1px solid var(--color-border, #e5e7eb);
    border-radius: 8px;
    font-family: inherit;
    font-size: 14px;
    resize: none;
    overflow: hidden;
    max-height: 160px;
    margin: 15px 0 10px;
}

.submit-button {
    width: 100%;
    margin-top: 15px;
    padding: 12px;
    border: none;
    border-radius: 8px;
    background-color: var(--color-primary, #3db897);
    color: white;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.15s;
}

.submit-button:hover:not(:disabled) {
    background-color: var(--color-primary-dark, #35a684);
}

.submit-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}
</style>