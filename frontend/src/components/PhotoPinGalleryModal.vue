<script setup>
import { ref, computed } from 'vue';
import api from '@/api/api';
import BaseModal from '@/components/BaseModal.vue';
import ConfirmDialog from './ConfirmDialog.vue';
import GroupSelectionUploadModal from '@/components/GroupSelectionUploadModal.vue';

const props = defineProps({
    photos: { type: Array, required: true },
    isGroupView: { type: Boolean, default: false }
});
const emit = defineEmits(['close', 'deleted', 'updated']);

const activeIndex = ref(props.photos.length === 1 ? 0 : null); // Setzt den Startwert von activeIndex abhängig von der Foto-Anzahl
const isEditing = ref(false);
const editDescription = ref('');
const editGroupIds = ref([]);
const saving = ref(false);
const deleting = ref(false);
const errors = ref('');
const showDeleteConfirm = ref(false);

const activePhoto = computed(() =>
    activeIndex.value !== null ? props.photos[activeIndex.value] : null
);

const resetEdit = () => {
    isEditing.value = false;
    errors.value = '';
};

const startEdit = () => {
    editDescription.value = activePhoto.value.description || '';
    editGroupIds.value = [...(activePhoto.value.groups_ids || [])];
    isEditing.value = true;
};

// Jede Schließen-Geste (X, Hintergrund-Klick, Escape) landet hier.
// Laufende Requests blockt BaseModal über :busy bereits ab
const requestClose = () => {
    if (isEditing.value) return resetEdit();    // erst raus aus dem Bearbeiten-Modus, nicht gleich schließen
    emit('close');
};

const openSlide = (index) => {
    resetEdit();
    activeIndex.value = index;
};

const backToGrid = () => {
    resetEdit();
    activeIndex.value = null;
};

const showPrev = () => {
    resetEdit();
    activeIndex.value = (activeIndex.value - 1 + props.photos.length) % props.photos.length;
};

const showNext = () => {
    resetEdit();
    activeIndex.value = (activeIndex.value + 1) % props.photos.length;
};

const saveEdit = async () => {
    try {
        saving.value = true;
        errors.value = '';
        const response = await api.patch(`photo-pins/${activePhoto.value.id}/`, {
            description : editDescription.value,
            groups : editGroupIds.value
        });
        emit('updated', response.data);
        isEditing.value = false;
    } catch (e) {
        console.error('Fehler beim Speichern:', e);
        errors.value = 'Änderung konnte nicht gespeichert werden';
    } finally {
        saving.value = false;
    }
}

const deletePhoto = async () => {
    try {
        deleting.value = true;
        errors.value = '';
        const deletedId = activePhoto.value.id;
        await api.delete(`photo-pins/${deletedId}/`);
        showDeleteConfirm.value = false;
        activeIndex.value = null; 
        emit('deleted', deletedId);
    } catch (e) {
        console.error('Fehler beim Löschen:', e);
        showDeleteConfirm.value = false;
        errors.value = 'Foto konnte nicht gelöscht werden.';
    } finally {
        deleting.value = false;
    }
}

const autoGrow = (event) => {
    const textarea = event.target;
    textarea.style.height = 'auto';
    textarea.style.height = `${textarea.scrollHeight}px`;
}
</script>

<template>
    <BaseModal :width="isEditing ? 'min(760px, 92vw)' : 'min(480px, 88vw)'" :busy="saving || deleting" @close="requestClose">
            <!-- Grid-Ansicht für die Fotos an einem Punkt -->
            <template v-if="activePhoto === null">
                <h2>{{ photos.length > 1 ? `${photos.length} Fotos` : '1 Foto' }}</h2>
                <div class="gallery-grid">
                    <button
                        v-for="(photo, index) in photos"
                        :key="photo.id"
                        type="button"
                        class="gallery-grid-item"
                        @click="openSlide(index)"
                    >
                        <img :src="photo.image" :alt="photo.description || 'Foto'" />
                    </button>
                </div>
            </template>

            <!-- Slide-Ansicht für einzelne Fotos (mit Vor und Zurück) -->
            <template v-else>
                <!-- Übersicht-Button: im Bearbeiten-Modus ausgeblendet -->
                <button v-if="photos.length > 1 && !isEditing" type="button" class="gallery-back-button" @click="backToGrid" aria-label="Zurück zur Übersicht">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                        <path d="M560-240 320-480l240-240 56 56-184 184 184 184-56 56Z"/>
                    </svg>
                    <span>Übersicht</span>
                </button>

                <!-- Im Bearbeiten-Modus zweispaltig: Foto links, Formular rechts -->
                <div class="gallery-body" :class="{ 'is-editing': isEditing }">
                    <div class="gallery-slide">
                        <!-- Vor/Zurück: im Bearbeiten-Modus ausgeblendet -->
                        <button v-if="photos.length > 1 && !isEditing" type="button" class="gallery-nav gallery-nav-prev" @click="showPrev" aria-label="Vorheriges Foto">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="15 6 9 12 15 18" />
                            </svg>
                        </button>

                        <div class="gallery-image-box">
                            <img :src="activePhoto.image" :alt="activePhoto.description || 'Foto'" class="gallery-slide-image" />
                        </div>

                        <button v-if="photos.length > 1 && !isEditing" type="button" class="gallery-nav gallery-nav-next" @click="showNext" aria-label="Nächstes Foto">
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <polyline points="9 6 15 12 9 18" />
                            </svg>
                        </button>
                    </div>

                    <div class="gallery-detail">
                        <p v-if="errors" class="gallery-error">{{ errors }}</p>

                        <!-- Bearbeiten -->
                        <template v-if="isEditing">
                            <span class="gallery-title">Beschreibung:</span>
                            <textarea v-model="editDescription" class="gallery-edit-input" rows="3" :disabled="saving" @input="autoGrow"></textarea>

                            <!-- Gruppen-Auswahl (gleiches Dropdown wie beim Foto-Upload, ohne Optional-Label) -->
                            <span class="gallery-title">weise dein Bild einer Gruppe zu:</span>
                            <GroupSelectionUploadModal :model-value="editGroupIds" :show-header="false" @update:selected-group="editGroupIds = $event" />

                            <div class="gallery-actions">
                                <button type="button" class="gallery-action" :disabled="saving" @click="resetEdit">Abbrechen</button>
                                <button type="button" class="gallery-action gallery-action-save" :disabled="saving" @click="saveEdit">
                                    {{ saving ? 'Wird gespeichert ...' : 'Speichern' }}
                                </button>
                            </div>
                        </template>

                        <!-- Anzeige -->
                        <template v-else>
                            <p v-if="isGroupView && activePhoto.uploader" class="gallery-meta">Von {{ activePhoto.uploader }}</p>
                            <p v-else-if="!isGroupView && activePhoto.groups && activePhoto.groups.length" class="gallery-meta">
                                {{ activePhoto.groups.length > 1 ? 'Gruppen' : 'Gruppe' }}: {{ activePhoto.groups.map(g => g.name).join(', ') }}
                            </p>

                            <p v-if="activePhoto.description" class="gallery-description">{{ activePhoto.description }}</p>

                            <div v-if="activePhoto.is_owner" class="gallery-actions">
                                <button type="button" class="gallery-action gallery-action-update" @click="startEdit">Bearbeiten</button>
                                <button type="button" class="gallery-action gallery-action-delete" :disabled="deleting" @click="showDeleteConfirm = true">
                                    {{ deleting ? 'Wird gelöscht ...' : 'Löschen' }}
                                </button>
                            </div>
                        </template>
                    </div>
                </div>

                <p v-if="photos.length > 1 && !isEditing" class="gallery-counter">{{ activeIndex + 1 }} / {{ photos.length }}</p>
            </template>

            <ConfirmDialog v-if="showDeleteConfirm" title="Foto löschen?" message="Das Foto wird dauerhaft entfernt. Diese Aktion kann nicht rückgängig gemacht werden." confirm-label="Löschen" danger :busy="deleting" @confirm="deletePhoto" @cancel="showDeleteConfirm = false" />
    </BaseModal>
</template>

<style scoped>
/* Overlay, Box und Schließen-Button kommen aus BaseModal */

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-top: 15px;
    /* Feste Maximalhöhe: bei vielen Fotos wird innerhalb des Grids gescrollt,
       statt dass das ganze Fenster mitwächst */
    max-height: 60vh;
    overflow-y: auto;
    padding-right: 4px;
}

/* Abgerundete Scrollbar (passend zu den runden Fenster-Ecken) */
.gallery-grid::-webkit-scrollbar {
    width: 8px;
}
.gallery-grid::-webkit-scrollbar-track {
    background: transparent;
}
.gallery-grid::-webkit-scrollbar-thumb {
    background-color: #cbd5e1;
    border-radius: 8px;
}
.gallery-grid::-webkit-scrollbar-thumb:hover {
    background-color: #94a3b8;
}

.gallery-grid-item {
    padding: 0;
    border: none;
    background: none;
    cursor: pointer;
    aspect-ratio: 1 / 1;
}

.gallery-grid-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 8px;
}

.gallery-back-button {
    display: flex;
    align-items: center;
    gap: 4px;
    /* negatives margin-top hebt den Button aus dem 40px-Padding auf top:20px –
       auf dieselbe Höhe wie den absolut positionierten X-Button von BaseModal */
    height: 36px;
    box-sizing: border-box;
    margin: -20px auto 12px 0;
    padding: 6px 10px 6px 6px;
    border: none;
    border-radius: 20px;
    background-color: var(--color-bg-page, #f0f2f5);
    color: var(--color-text, #1a1a1a);
    cursor: pointer;
    font-size: 13px;
}

.gallery-back-button svg {
    width: 20px;
    height: 20px;
}

.gallery-slide {
    display: flex;
    align-items: center;
    gap: 8px;
}

/* Bearbeiten-Modus: Foto links, Formular rechts (vertikal mittig zum Foto) */
.gallery-body.is-editing {
    display: flex;
    align-items: center;
    gap: 16px;
    text-align: center;
}

.gallery-body.is-editing .gallery-slide {
    flex: 0 0 45%;
    min-width: 0;
}

.gallery-body.is-editing .gallery-image-box {
    height: 46vh;
    max-height: 400px;
}

.gallery-detail {
    min-width: 0;
}

.gallery-body.is-editing .gallery-detail {
    flex: 1;
    align-self: stretch;
    display: flex;
    flex-direction: column;
    justify-content: center; /* vertikal mittig */
    align-items: center;     /* horizontal mittig */
    gap: 12px;
}

/* Beschreibungsfeld im Bearbeiten-Modus etwas größer */
.gallery-body.is-editing .gallery-edit-input {
    min-height: 90px;
    margin-top: 0;
}

.gallery-title {
    font-size: 13px;
    font-weight: 600;
    align-self: flex-start;  /* linksbündig statt zentriert */
    margin-bottom: -6px;     /* weniger Abstand nach unten (kompensiert den gap) */
    color: var(--color-text-muted, #888888);
}

/* Auf schmalen Screens (Handy) zweispaltig zu eng -> wieder untereinander */
@media (max-width: 600px) {
    .gallery-body.is-editing {
        flex-direction: column;
        align-items: stretch;
    }
    .gallery-body.is-editing .gallery-slide {
        flex: none;
    }
    .gallery-body.is-editing .gallery-image-box {
        height: 38vh;
    }
}

/* Feste, konstant große Box (Höhe an der Viewport-Höhe statt an der Breite ausgerichtet,
   damit sie immer mit Luft nach oben/unten ins Fenster passt – keine Scrollbar) */
.gallery-image-box {
    flex: 1;
    min-width: 0;
    height: 50vh;
    max-height: 440px;
    display: flex;
    align-items: center;
    justify-content: center;
}

/* Bild schrumpft auf seine tatsächliche Größe innerhalb der Box, dadurch greift der
   border-radius am Foto selbst und nicht an der (unsichtbaren) Box-Fläche */
.gallery-slide-image {
    max-width: 100%;
    max-height: 100%;
    width: auto;
    height: auto;
    border-radius: 16px;
}

.gallery-nav {
    flex-shrink: 0;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: none;
    background-color: var(--color-bg-page, #f0f2f5);
    color: var(--color-text, #1a1a1a);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
}

.gallery-nav svg {
    width: 20px;
    height: 20px;
}

.gallery-meta {
    margin: 12px 0 0;
    font-size: 12px;
    font-weight: 600;
    color: var(--color-text-muted, #888888);
}

.gallery-description {
    margin: 12px 0 0;
    font-size: 14px;
    color: var(--color-text, #1a1a1a);
}

.gallery-counter {
    margin: 4px 0 0;
    font-size: 12px;
    color: var(--color-text-muted, #888888);
}

.gallery-error {
    margin: 12px 0 0;
    background-color: #fee2e2;
    color: #e53e3e;
    padding: 8px;
    border-radius: 8px;
    font-size: 13px;
}

.gallery-edit-input {
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
    margin-top: 12px;
}

.gallery-actions {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-top: 12px;
}

.gallery-action {
    padding: 8px 14px;
    border: 1px solid var(--color-border, #e5e7eb);
    border-radius: 20px;
    background-color: white;
    color: var(--color-text, #1a1a1a);
    font-size: 13px;
    cursor: pointer;
}

.gallery-action:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.gallery-action-save {
    background-color: var(--color-primary, #3db897);
    border-color: var(--color-primary, #3db897);
    color: white;
}

.gallery-action-update {
    border-color: var(--color-primary);
    color: var(--color-primary);
}

.gallery-action-delete {
    border-color: #e53e3e;
    color: #e53e3e;
}

</style>