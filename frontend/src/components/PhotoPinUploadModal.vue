<script setup>
import { ref, computed } from 'vue';
import api from '@/api/api';
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
    <div class="popup">
        <div class="popup-content">
            <div class="header">
                <h2>Foto hinzufügen</h2>
            </div>
            <button @click="$emit('close')" class="popup-close-button" aria-label="Schließen">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
                    <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/>
                </svg>
            </button>

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

            <input type="file" accept="image/*" multiple id="photo-upload" :disabled="uploading" @change="onFilesSelected" />
            <label for="photo-upload" class="photo-picker-button">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
                    <path d="M480-260q75 0 127.5-52.5T660-440q0-75-52.5-127.5T480-620q-75 0-127.5 52.5T300-440q0 75 52.5 127.5T480-260Zm0-80q-42 0-71-29t-29-71q0-42 29-71t71-29q42 0 71 29t29 71q0 42-29 71t-71 29ZM160-120q-33 0-56.5-23.5T80-200v-480q0-33 23.5-56.5T160-760h126l74-80h240l74 80h126q33 0 56.5 23.5T880-680v480q0 33-23.5 56.5T800-120H160Zm0-80h640v-480H638l-73-80H395l-73 80H160v480Zm320-240Z"/>
                </svg>
                <span>{{ selectedPhotos.length ? 'Weitere Fotos hinzufügen' : 'Fotos auswählen' }}</span>
            </label>
            <textarea v-model="description" class="description-input" placeholder="Beschreibung (optional)" rows="2" :disabled="uploading" @input="autoGrow"></textarea>

            <GroupSelectionUploadModal @update:selected-group="selectedGroups = $event" />

            <button type="button" class="submit-button" :disabled="!canSubmit" @click="submitPin">
                {{ uploading ? 'Wird hochgeladen ...' : 'Foto(s) hinzufügen' }}
            </button>
        </div>
    </div>
</template>

<style scoped>
.popup {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1001;
}

.popup-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
    position: relative;
    width: min(420px, 90vw);
    max-height: 85vh;
    overflow-y: auto;
}

.header h2 {
    margin: 20px 0px 20px 0;
}

.popup-close-button {
    position: absolute;
    top: 16px;
    right: 16px;
    background-color: var(--color-primary, #3db897);
    border: none;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: white;
    border-radius: 50%;
    transition: background-color 0.15s;
    z-index: 3000;
}

.popup-close-button:hover {
    background-color: var(--color-primary-dark, #35a684);
}

.popup-close-button svg {
    width: 24px;
    height: 24px;
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