<script setup>
import { ref } from 'vue';
import api from '@/api/api';
import BaseModal from '@/components/BaseModal.vue';

const emit = defineEmits(['close', 'created']);

const newGroupName = ref('');
const saving = ref(false);
const errors = ref('');

const createNewGroup = async () => {
    if (!newGroupName.value.trim()) return;
    try {
        saving.value = true;
        errors.value = '';
        const response = await api.post('groups/', {
            name: newGroupName.value
        });
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
    box-shadow: 0 0 0 3px rgba(61, 184, 151, 0.15);
}

.group-error {
    margin: 0.75rem 0 0;
    background-color: #fee2e2;
    color: #e53e3e;
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
    background-color: #f1f5f9;
    color: #64748b;
    transition: all 0.2s ease;
}

.group-action:hover:not(:disabled) {
    background-color: #e2e8f0;
}

.group-action:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.group-action-create {
    background-color: var(--color-primary);
    color: white;
}

.group-action-create:hover:not(:disabled) {
    background-color: var(--color-primary-dark);
}
</style>
