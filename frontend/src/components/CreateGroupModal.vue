<script setup>
import { ref } from 'vue';
import api from '@/api/api';
import BaseModal from '@/components/BaseModal.vue';
import CameraGalleryPicker from '@/components/CameraGalleryPicker.vue';

const emit = defineEmits(['close', 'created']);

const newGroupName = ref('');
const newGroupDescription = ref('');
const selectedFile = ref(null);
const previewImage = ref(null);
const saving = ref(false);
const errors = ref('');

const showPhotoMenu = ref(false);

const onGroupPhotoAdded = (photos) => {
    const photo = photos[0];
    if (!photo) return;
    selectedFile.value = photo.file;
    previewImage.value = photo.previewUrl;
}

const createNewGroup = async () => {
    if (!newGroupName.value.trim()) return;
    try {
        saving.value = true;
        errors.value = '';
        const formData = new FormData();
        formData.append('name', newGroupName.value);
        if (newGroupDescription.value) formData.append('description', newGroupDescription.value);
        if (selectedFile.value) formData.append('profilbild', selectedFile.value);

        const response = await api.post('groups/', formData);
        const formData = new FormData();
        formData.append('name', newGroupName.value);
        if (newGroupDescription.value) formData.append('description', newGroupDescription.value);
        if (selectedFile.value) formData.append('profilbild', selectedFile.value);

        const response = await api.post('groups/', formData);
        emit('created', response.data);
    } catch (error) {
        console.error('Fehler beim Erstellen der Gruppe:', error.response?.data || error.message);
        errors.value = 'Gruppe konnte nicht erstellt werden.';
    } finally {
        saving.value = false;
    }
};
</script>

<template>
    <BaseModal width="min(28rem, 88vw)" :busy="saving" @close="emit('close')">
        <h2>Neue Gruppe erstellen</h2>

        <CameraGalleryPicker
            :multiple="false"
            :has-photos="!!previewImage"
            :disabled="saving"
            @photos-added="onGroupPhotoAdded"
            v-slot="{ isNative, takePhoto, pickFromGallery, onFilesSelected }"
        >
            <div class="photo-wrapper">
                <img v-if="previewImage" :src="previewImage" alt="Gruppenbild" class="group-photo">
                <div v-else class="group-photo group-photo-placeholder">
                    <svg xmlns="http://www.w3.org/2000/svg" height="28px" viewBox="0 -960 960 960" width="28px">
                        <path d="M40-160v-112q0-34 17.5-62.5T104-378q62-31 126-46.5T360-440q66 0 130 15.5T616-378q29 15 46.5 43.5T680-272v112H40Zm720 0v-120q0-44-24.5-84.5T666-434q51 6 96 20.5t84 35.5q36 20 55 44.5t19 53.5v120H760ZM247-527q-47-47-47-113t47-113q47-47 113-47t113 47q47 47 47 113t-47 113q-47 47-113 47t-113-47Zm466 0q-47 47-113 47-11 0-28-2.5t-28-5.5q27-32 41.5-71t14.5-81q0-42-14.5-81T544-792q14-5 28-6.5t28-1.5q66 0 113 47t47 113q0 66-47 113ZM120-240h480v-32q0-11-5.5-20T580-306q-54-27-109-40.5T360-360q-56 0-111 13.5T140-306q-9 5-14.5 14t-5.5 20v32Zm296.5-343.5Q440-607 440-640t-23.5-56.5Q393-720 360-720t-56.5 23.5Q280-673 280-640t23.5 56.5Q327-560 360-560t56.5-23.5ZM360-240Zm0-400Z"/>
                    </svg>
                </div>

                <!-- Web: öffnet den Datei-Dialog des Browsers direkt (mobile Browser bieten dort selbst schon Kamera + Galerie als Auswahl an) -->
                <label
                    v-if="!isNative"
                    for="new-group-photo-upload"
                    class="photo-edit-overlay"
                    :class="{ 'photo-edit-overlay-persistent': !previewImage }"
                    aria-label="Profilbild auswählen"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="currentColor">
                        <path d="M200-200h57l391-391-57-57-391 391v57Zm-80 80v-170l528-527q12-11 26.5-17t30.5-6q16 0 31 6t26 18l55 56q12 11 17.5 26t5.5 30q0 16-5.5 30.5T817-647L290-120H120Zm640-584-56-56 56 56Zm-141 85-28-29 57 57-29-28Z"/>
                    </svg>
                </label>
                <!-- Native App: Kamera und Galerie sind getrennte Plugin-Aufrufe, hier explizit zur Auswahl stellen -->
                <button
                    v-else
                    type="button"
                    class="photo-edit-overlay"
                    :class="{ 'photo-edit-overlay-persistent': !previewImage }"
                    @click="showPhotoMenu = true"
                    aria-haspopup="true"
                    :aria-expanded="showPhotoMenu"
                    aria-label="Profilbild auswählen"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="currentColor">
                        <path d="M200-200h57l391-391-57-57-391 391v57Zm-80 80v-170l528-527q12-11 26.5-17t30.5-6q16 0 31 6t26 18l55 56q12 11 17.5 26t5.5 30q0 16-5.5 30.5T817-647L290-120H120Zm640-584-56-56 56 56Zm-141 85-28-29 57 57-29-28Z"/>
                    </svg>
                </button>

                <BaseModal v-if="isNative && showPhotoMenu" variant="sheet" width="24rem" @close="showPhotoMenu = false">
                    <h2>Profilbild auswählen</h2>
                    <div class="photo-menu">
                        <button type="button" class="photo-menu-item" @click="takePhoto(); showPhotoMenu = false">
                            <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="currentColor">
                                <path d="M480-260q75 0 127.5-52.5T660-440q0-75-52.5-127.5T480-620q-75 0-127.5 52.5T300-440q0 75 52.5 127.5T480-260Zm0-80q-42 0-71-29t-29-71q0-42 29-71t71-29q42 0 71 29t29 71q0 42-29 71t-71 29ZM160-120q-33 0-56.5-23.5T80-200v-480q0-33 23.5-56.5T160-760h126l74-80h240l74 80h126q33 0 56.5 23.5T880-680v480q0 33-23.5 56.5T800-120H160Z"/>
                            </svg>
                            Foto aufnehmen
                        </button>
                        <button type="button" class="photo-menu-item" @click="pickFromGallery(); showPhotoMenu = false">
                            <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="currentColor">
                                <path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h560q33 0 56.5 23.5T840-760v560q0 33-23.5 56.5T760-120H200Zm40-80h480L570-480 450-320l-90-120-120 160Z"/>
                            </svg>
                            Aus Galerie wählen
                        </button>
                    </div>
                </BaseModal>
            </div>
            <input v-if="!isNative" type="file" accept="image/*" id="new-group-photo-upload" class="visually-hidden-input" :disabled="saving" @change="onFilesSelected">
        </CameraGalleryPicker>

        <input
            v-model="newGroupName"
            type="text"
            class="group-name-input"
            placeholder="Name deiner Gruppe..."
            :disabled="saving"
            @keyup.enter="createNewGroup"
        />

        <textarea
            v-model="newGroupDescription"
            class="group-description-input"
            placeholder="Beschreibung (optional)"
            rows="3"
            :disabled="saving"
        ></textarea>

        <p v-if="errors" class="group-error">{{ errors }}</p>

        <div class="group-actions">
            <button type="button" class="group-action" :disabled="saving" @click="emit('close')">Abbrechen</button>
            <button type="button" class="group-action group-action-create" :disabled="saving" @click="createNewGroup">
                {{ saving ? 'Wird erstellt ...' : 'Erstellen' }}
            </button>
        </div>
    </BaseModal>
</template>

<style scoped>
/* Overlay, Box und Schließen-Button kommen aus BaseModal */

.group-name-input {
    width: 100%;
    box-sizing: border-box;
    margin-top: 1.5rem;
    padding: 0.85rem 1rem;
    font-size: 1rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    outline: none;
    color: var(--color-text);
    background-color: var(--color-bg-page);
    transition: all 0.2s ease;
}

.group-name-input:focus {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.15);
}

.group-description-input {
    width: 100%;
    box-sizing: border-box;
    margin-top: 0.75rem;
    padding: 0.85rem 1rem;
    font-size: 1rem;
    font-family: inherit;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    outline: none;
    color: var(--color-text);
    background-color: var(--color-bg-page);
    resize: vertical;
    transition: all 0.2s ease;
}

.group-description-input:focus {
    border-color: var(--color-primary);
    box-shadow: 0 0 0 3px rgba(var(--color-primary-rgb), 0.15);
}

.photo-wrapper {
    position: relative;
    width: 5rem;
    height: 5rem;
    margin: 1.25rem auto 0;
    border-radius: var(--radius-md);
}

.group-photo {
    width: 5rem;
    height: 5rem;
    border-radius: var(--radius-md);
    object-fit: cover;
    display: block;
    border: 3px solid var(--color-primary);
    box-sizing: border-box;
}

.group-photo-placeholder {
    display: flex;
    justify-content: center;
    align-items: center;
    background-color: var(--color-primary-soft);
}
.group-photo-placeholder svg {
    fill: var(--color-primary);
}

/* Bearbeiten-Stift über dem Bild - erscheint erst bei Hover/Tap auf das
   Bild, statt als dauerhaft sichtbarer Button. */
.photo-edit-overlay {
    position: absolute;
    inset: 0;
    display: flex;
    align-items: center;
    justify-content: center;
    background-color: rgba(0, 0, 0, 0.45);
    border-radius: var(--radius-md);
    border: none;
    padding: 0;
    color: #fff;
    cursor: pointer;
    opacity: 0;
    transition: opacity 0.15s ease;
}
.photo-wrapper:hover .photo-edit-overlay,
.photo-wrapper:focus-within .photo-edit-overlay {
    opacity: 1;
}

/* Ohne Bild ist der Stift dauerhaft sichtbar - er signalisiert hier ein
   leeres, ausfüllbares Feld statt eine Aktion auf einem vorhandenen Bild. */
.photo-edit-overlay-persistent {
    opacity: 1;
    background-color: rgba(0, 0, 0, 0.25);
}

.visually-hidden-input {
    position: absolute;
    width: 1px;
    height: 1px;
    overflow: hidden;
    clip: rect(0, 0, 0, 0);
}

/* Auswahlmenü für die native App (Kamera vs. Galerie) - Overlay, Rahmen
   und Schließen-Verhalten kommen aus BaseModal, hier nur die Buttons. */
.photo-menu {
    margin-top: 1.5rem;
    border: 1px solid var(--color-border);
    border-radius: var(--radius-md);
    overflow: hidden;
    display: flex;
    flex-direction: column;
}
.photo-menu-item {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    background: none;
    border: none;
    border-bottom: 1px solid var(--color-border);
    color: var(--color-text);
    padding: 1rem 1.25rem;
    font-size: 0.95rem;
    font-weight: 500;
    cursor: pointer;
    text-align: left;
}
.photo-menu-item:last-child {
    border-bottom: none;
}
.photo-menu-item:hover {
    background-color: var(--color-bg-hover);
}
.photo-menu-item svg {
    fill: var(--color-primary);
    flex-shrink: 0;
}

.group-error {
    margin: 0.75rem 0 0;
    background-color: var(--color-bg-card);
    color: var(--color-danger);
    padding: 0.5rem;
    border-radius: var(--radius-md);
    font-size: 0.85rem;
}

.group-actions {
    display: flex;
    justify-content: center;
    gap: 0.75rem;
    margin-top: 1.5rem;
}

.group-action {
    flex: 1;
    padding: 0.85rem 1.5rem;
    border: none;
    border-radius: var(--radius-md);
    font-size: 0.95rem;
    font-weight: 600;
    cursor: pointer;
    background-color: var(--color-bg-page);
    color: var(--color-text-muted);
    transition: all 0.2s ease;
}

.group-action:hover:not(:disabled) {
    background-color: var(--color-bg-hover);
}

.group-action:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.group-action-create {
    background-color: var(--color-primary);
    color: var(--color-on-primary);
}

.group-action-create:hover:not(:disabled) {
    background-color: var(--color-primary-dark);
}
</style>
