<script setup>
import { ref, computed } from 'vue';
import api from '@/api/api';
import BaseModal from '@/components/BaseModal.vue';
import GroupSelectionUploadModal from '@/components/GroupSelectionUploadModal.vue';
import CameraGalleryPicker from '@/components/CameraGalleryPicker.vue';


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

const canSubmit = computed(() => selectedPhotos.value.length > 0 && !uploading.value);

const onPhotosAdded = (photos) => {
    error.value = '';
    selectedPhotos.value.push(...photos);
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

        <CameraGalleryPicker
            :disabled="uploading"
            :has-photos="selectedPhotos.length > 0"
            @photos-added="onPhotosAdded"
        />

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
    background-color: var(--color-danger-bg);
    color: var(--color-danger);
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
    background-color: var(--color-danger);
    color: var(--color-on-primary);
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
    color: var(--color-on-primary);
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