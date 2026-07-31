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

        <img v-if="previewImage" :src="previewImage" alt="Gruppenbild" class="group-photo-preview">
        <CameraGalleryPicker :multiple="false" :has-photos="!!previewImage" @photos-added="onGroupPhotoAdded" />

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
    margin-top: 0.85rem;
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

.group-photo-preview {
    width: 5rem;
    height: 5rem;
    border-radius: var(--radius-md);
    object-fit: cover;
    margin-top: 0.85rem;
    align-self: center;
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
