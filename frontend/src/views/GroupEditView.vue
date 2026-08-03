<script setup>
import { useRoute, useRouter } from 'vue-router'
import { ref, onMounted, computed } from 'vue'
import api from '@/api/api';
import PageHeader from '@/components/PageHeader.vue';
import CameraGalleryPicker from '@/components/CameraGalleryPicker.vue';
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import BaseModal from '@/components/BaseModal.vue';
import { usePageTitle } from '@/composables/usePageTitle';
import { isMobile } from '@/composables/viewport';

const route = useRoute()
const router = useRouter()
const { setPageTitle } = usePageTitle()

const groupId = computed(() => route.params.id)
const group = ref(null)
const loading = ref(false)

const name = ref("")
const description = ref("")
const selectedFile = ref(null)
const previewImage = ref(null)
const removeProfilbild = ref(false)

const saving = ref(false)
const saved = ref(false)

const showPhotoMenu = ref(false)
const hasPhoto = computed(() => !!previewImage.value || (!!group.value?.profilbild && !removeProfilbild.value))

const showDeleteConfirm = ref(false)
const deleting = ref(false)

const fetchGroup = async () => {
    try {
        loading.value = true;
        const response = await api.get(`groups/${groupId.value}/`);
        group.value = response.data;
        setPageTitle('Gruppe bearbeiten');

        // Direkter Aufruf der URL durch Nicht-Admins zurück zur Gruppenansicht schicken -
        // der Bearbeiten-Button ist ohnehin nur für Admins sichtbar.
        if (!group.value.is_admin) {
            router.replace(`/group/${groupId.value}`);
            return;
        }

        name.value = group.value.name;
        description.value = group.value.description || "";
    } catch(err) {
        console.error('Fehler beim Laden der Gruppe: ', err)
    } finally {
        loading.value = false;
    }
}

const onPhotoAdded = (photos) => {
    const photo = photos[0];
    if (!photo) return;
    selectedFile.value = photo.file;
    previewImage.value = photo.previewUrl;
    removeProfilbild.value = false;
}

// Entfernt das Bild ohne ein neues auszuwählen (Akzeptanzkriterium: löschen ohne Ersatz).
const removePicture = () => {
    selectedFile.value = null;
    previewImage.value = null;
    removeProfilbild.value = true;
}

const saveGroup = async () => {
    if (!name.value.trim()) return;
    try {
        saving.value = true;
        saved.value = false;
        const formData = new FormData();
        formData.append('name', name.value);
        formData.append('description', description.value); // leerer String entfernt die Beschreibung

        if (selectedFile.value) {
            formData.append('profilbild', selectedFile.value);
        } else if (removeProfilbild.value) {
            formData.append('remove_profilbild', 'true');
        }

        const response = await api.patch(`groups/${groupId.value}/`, formData);
        group.value = response.data;
        selectedFile.value = null;
        removeProfilbild.value = false;
        saved.value = true;
        setTimeout(() => saved.value = false, 2500);
    } catch (error) {
        console.error("Fehler beim Bearbeiten der Gruppe:", error);
        alert(error.response?.data?.error || "Es gab ein Problem beim Speichern der Änderungen.");
    } finally {
        saving.value = false;
    }
}

const deleteGroup = async () => {
    try {
        deleting.value = true;
        await api.delete(`groups/${groupId.value}/`);
        router.push("/group");
    } catch (error) {
        console.error("Fehler beim Löschen der Gruppe:", error);
        alert(error.response?.data?.error || "Es gab ein Problem beim Löschen der Gruppe.");
        deleting.value = false;
    }
}

onMounted(() => {
    fetchGroup();
})
</script>

<template>
    <PageHeader v-if="!isMobile" />

    <div class="page-container">
        <div v-if="loading" class="loading-state">
            <p>Gruppe wird geladen...</p>
        </div>

        <form v-else-if="group" class="edit-form" @submit.prevent="saveGroup">
            <div class="input-group photo-fields-group">
                <CameraGalleryPicker
                    :multiple="false"
                    :has-photos="!!previewImage"
                    @photos-added="onPhotoAdded"
                    v-slot="{ isNative, takePhoto, pickFromGallery, onFilesSelected }"
                >
                    <div class="photo-col">
                        <div class="photo-wrapper">
                            <img v-if="previewImage" :src="previewImage" alt="Gruppenbild" class="group-photo">
                            <img v-else-if="group.profilbild && !removeProfilbild" :src="group.profilbild" alt="Gruppenbild" class="group-photo">
                            <div v-else class="group-photo group-photo-placeholder">
                                <svg xmlns="http://www.w3.org/2000/svg" height="28px" viewBox="0 -960 960 960" width="28px">
                                    <path d="M40-160v-112q0-34 17.5-62.5T104-378q62-31 126-46.5T360-440q66 0 130 15.5T616-378q29 15 46.5 43.5T680-272v112H40Zm720 0v-120q0-44-24.5-84.5T666-434q51 6 96 20.5t84 35.5q36 20 55 44.5t19 53.5v120H760ZM247-527q-47-47-47-113t47-113q47-47 113-47t113 47q47 47 47 113t-47 113q-47 47-113 47t-113-47Zm466 0q-47 47-113 47-11 0-28-2.5t-28-5.5q27-32 41.5-71t14.5-81q0-42-14.5-81T544-792q14-5 28-6.5t28-1.5q66 0 113 47t47 113q0 66-47 113ZM120-240h480v-32q0-11-5.5-20T580-306q-54-27-109-40.5T360-360q-56 0-111 13.5T140-306q-9 5-14.5 14t-5.5 20v32Zm296.5-343.5Q440-607 440-640t-23.5-56.5Q393-720 360-720t-56.5 23.5Q280-673 280-640t23.5 56.5Q327-560 360-560t56.5-23.5ZM360-240Zm0-400Z"/>
                                </svg>
                            </div>

                            <!-- Web: Klick öffnet den Datei-Dialog des Browsers direkt (mobile Browser
                                 bieten dort selbst schon Kamera + Galerie als Auswahl an). -->
                            <label
                                v-if="!isNative"
                                for="group-photo-upload"
                                class="photo-edit-overlay"
                                :class="{ 'photo-edit-overlay-persistent': !hasPhoto }"
                                aria-label="Profilbild ändern"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="currentColor">
                                    <path d="M200-200h57l391-391-57-57-391 391v57Zm-80 80v-170l528-527q12-11 26.5-17t30.5-6q16 0 31 6t26 18l55 56q12 11 17.5 26t5.5 30q0 16-5.5 30.5T817-647L290-120H120Zm640-584-56-56 56 56Zm-141 85-28-29 57 57-29-28Z"/>
                                </svg>
                            </label>
                            <!-- Native App: Kamera und Galerie sind getrennte Plugin-Aufrufe, daher
                                 hier explizit zur Auswahl stellen statt direkt eine Aktion auszuführen. -->
                            <button
                                v-else
                                type="button"
                                class="photo-edit-overlay"
                                :class="{ 'photo-edit-overlay-persistent': !hasPhoto }"
                                @click="showPhotoMenu = true"
                                aria-haspopup="true"
                                :aria-expanded="showPhotoMenu"
                                aria-label="Profilbild ändern"
                            >
                                <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="currentColor">
                                    <path d="M200-200h57l391-391-57-57-391 391v57Zm-80 80v-170l528-527q12-11 26.5-17t30.5-6q16 0 31 6t26 18l55 56q12 11 17.5 26t5.5 30q0 16-5.5 30.5T817-647L290-120H120Zm640-584-56-56 56 56Zm-141 85-28-29 57 57-29-28Z"/>
                                </svg>
                            </button>

                            <BaseModal v-if="isNative && showPhotoMenu" variant="sheet" width="24rem" @close="showPhotoMenu = false">
                                <h2>Gruppenbild ändern</h2>
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
                        <input v-if="!isNative" type="file" accept="image/*" id="group-photo-upload" class="visually-hidden-input" @change="onFilesSelected">

                        <button
                            v-if="(group.profilbild && !removeProfilbild) || previewImage"
                            type="button"
                            class="remove-picture-btn"
                            @click="removePicture"
                        >
                            Bild entfernen
                        </button>
                    </div>
                </CameraGalleryPicker>

                <div class="fields-col">
                    <div class="field">
                        <label for="group-name">Gruppenname</label>
                        <input id="group-name" v-model="name" type="text" placeholder="Gruppenname">
                    </div>
                    <div class="field">
                        <label for="group-description">Beschreibung</label>
                        <textarea id="group-description" v-model="description" placeholder="Beschreibung (optional)" rows="4"></textarea>
                    </div>
                </div>
            </div>

            <button type="submit" id="save" :disabled="saving">
                <template v-if="saving">
                    <svg class="spinner" xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="12" r="10" stroke="white" stroke-width="2" stroke-dasharray="40" stroke-dashoffset="10"/>
                    </svg>
                    Wird gespeichert...
                </template>
                <template v-else-if="saved">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                        <path d="M382-240 154-468l57-57 171 171 367-367 57 57-424 424Z"/>
                    </svg>
                    Gespeichert!
                </template>
                <template v-else>
                    Änderungen speichern
                </template>
            </button>

            <button type="button" id="cancel" :disabled="saving" @click="router.push(`/group/${groupId}`)">
                Abbrechen
            </button>

            <div class="danger-zone">
                <h4>Gefahrenzone</h4>
                <p>Das Löschen der Gruppe kann nicht rückgängig gemacht werden. Alle Mitglieder verlieren den Zugriff auf die Gruppe.</p>
                <button type="button" class="delete-group-btn" @click="showDeleteConfirm = true">
                    Gruppe löschen
                </button>
            </div>
        </form>
    </div>

    <ConfirmDialog
        v-if="showDeleteConfirm"
        title="Gruppe löschen?"
        message="Die Gruppe wird dauerhaft gelöscht. Diese Aktion kann nicht rückgängig gemacht werden."
        confirm-label="Löschen"
        danger
        :busy="deleting"
        @confirm="deleteGroup"
        @cancel="showDeleteConfirm = false"
    />
</template>

<style scoped>
    .page-container {
        min-height: 100vh;
        padding: calc(var(--safe-top, 0px) + var(--app-header-height) + 1.5rem) 1rem
                 calc(var(--safe-bottom, 0px) + var(--tab-bar-height) + 1.5rem) 1rem;
        background-color: var(--color-bg-page);
        box-sizing: border-box;
    }

    /* Ab Desktop-Breite übernimmt PageHeader (sticky, eigener margin-top) den
       Versatz unter der DesktopNavBar - sonst würde der Abstand doppelt zählen. */
    @media (min-width: 768px) {
        .page-container {
            padding-top: 1.5rem;
        }
    }

    .loading-state {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        color: var(--color-text-muted);
    }

    .edit-form {
        width: 100%;
        max-width: 40rem;
        margin: 0 auto;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        padding-bottom: 4rem;
    }

    .input-group {
        background-color: var(--color-bg-card);
        padding: 1.25rem;
        border-radius: var(--radius-lg);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .photo-fields-group {
        flex-direction: column;
        align-items: stretch;
        gap: 1.25rem;
    }

    .photo-col {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
    }

    .photo-wrapper {
        position: relative;
        border-radius: var(--radius-md);
    }

    .group-photo {
        width: 6rem;
        height: 6rem;
        border-radius: var(--radius-md);
        object-fit: cover;
        border: 3px solid var(--color-primary);
        box-sizing: border-box;
        flex-shrink: 0;
        display: block;
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
       Bild, statt als dauerhaft sichtbarer Button (auf Touch-Geräten löst
       der erste Tap :hover aus und zeigt den Stift, der zweite Tap wählt ihn an). */
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

    .remove-picture-btn {
        background: none;
        border: none;
        color: var(--color-text-muted);
        text-decoration: underline;
        cursor: pointer;
        font-size: 0.85rem;
        padding: 0;
    }
    .remove-picture-btn:hover {
        color: var(--color-danger);
    }

    .fields-col {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        min-width: 0;
        flex: 1;
    }

    .field {
        display: flex;
        flex-direction: column;
        gap: 0.4rem;
    }

    .field label {
        font-weight: 500;
        font-size: 0.9rem;
        color: var(--color-text);
    }

    .field input,
    .field textarea {
        padding: 0.85rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--color-border);
        box-sizing: border-box;
        width: 100%;
        font-size: 1rem;
        font-family: inherit;
        background-color: var(--color-bg-page);
        color: var(--color-text);
        resize: vertical;
    }
    .field input:focus,
    .field textarea:focus {
        outline: none;
        border-color: var(--color-primary);
    }

    #save {
        background-color: var(--color-primary);
        border: none;
        color: var(--color-on-primary);
        border-radius: var(--radius-md);
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        width: 100%;
    }
    #save:hover:not(:disabled) {
        background-color: var(--color-primary-dark);
    }
    #save:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    #cancel {
        background-color: var(--color-bg-hover);
        border: 1px solid var(--color-border);
        color: var(--color-text-muted);
        border-radius: var(--radius-md);
        padding: 1rem;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        width: 100%;
        margin-top: -0.75rem;
    }
    #cancel:hover:not(:disabled) {
        color: var(--color-text);
    }
    #cancel:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .spinner {
        animation: spin 0.8s linear infinite;
        transform-origin: center;
    }
    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    .danger-zone {
        border: 1px solid var(--color-danger);
        background-color: var(--color-danger-bg);
        border-radius: var(--radius-lg);
        padding: 1.25rem;
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
    }
    .danger-zone h4 {
        margin: 0;
        font-size: 1rem;
        font-weight: 600;
        color: var(--color-danger);
    }
    .danger-zone p {
        margin: 0;
        font-size: 0.85rem;
        line-height: 1.4;
        color: var(--color-text-muted);
    }
    .delete-group-btn {
        align-self: flex-start;
        background-color: transparent;
        border: 1px solid var(--color-danger);
        color: var(--color-danger);
        cursor: pointer;
        border-radius: var(--radius-md);
        padding: 0.6em 1.2em;
        font-size: 0.9rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    .delete-group-btn:hover {
        background-color: var(--color-danger);
        color: var(--color-on-primary);
    }

    @media (min-width: 480px) {
        .input-group {
            padding: 2rem;
        }
    }

    /* Ab Desktop-Breite steht das Bild links neben Name/Beschreibung statt darüber */
    @media (min-width: 768px) {
        .photo-fields-group {
            flex-direction: row;
            align-items: flex-start;
        }
        .photo-col {
            flex-shrink: 0;
        }
        .group-photo {
            width: 7rem;
            height: 7rem;
        }
        .fields-col {
            padding-top: 0.25rem;
        }
    }
</style>
