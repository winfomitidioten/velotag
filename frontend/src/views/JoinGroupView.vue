<script setup>
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import api from '@/api/api';
import PageHeader from '@/components/PageHeader.vue';

// Ziel des Einladungslinks/QR-Codes aus GroupDetailView.vue: der Token steckt
// in der URL (siehe router/index.js, Route "group-join"), wir müssen ihn nur
// noch an den Beitritts-Endpoint schicken.
const route = useRoute();
const router = useRouter();

const loading = ref(true);
const errorMessage = ref('');
const joinedGroup = ref(null);

const joinGroup = async () => {
    try {
        loading.value = true;
        const response = await api.post('groups/join/', {
            token: route.params.token
        });
        joinedGroup.value = response.data;
    } catch (error) {
        console.error('Fehler beim Beitreten über den Einladungslink:', error);
        errorMessage.value = error.response?.data?.error || 'Der Einladungslink ist ungültig oder abgelaufen.';
    } finally {
        loading.value = false;
    }
}

const goToGroup = () => {
    router.push({ name: 'group-detail', params: { id: joinedGroup.value.id } });
}

onMounted(() => {
    joinGroup();
})
</script>

<template>
    <div class="page-container">
        <PageHeader title="Gruppe beitreten" />

        <main class="page-content">
            <div v-if="loading" class="join-state">
                <p>Du trittst der Gruppe bei...</p>
            </div>

            <div v-else-if="joinedGroup" class="join-state">
                <p>Du bist der Gruppe <strong>{{ joinedGroup.name }}</strong> erfolgreich beigetreten.</p>
                <button @click="goToGroup" class="join-action-btn">Zur Gruppe</button>
            </div>

            <div v-else class="join-state">
                <p class="join-error">{{ errorMessage }}</p>
                <button @click="router.push('/group')" class="join-action-btn">Zu meinen Gruppen</button>
            </div>
        </main>
    </div>
</template>

<style scoped>
    .page-container {
        min-height: 100vh;
        background-color: var(--color-bg-page);
        display: flex;
        flex-direction: column;
    }

    .page-content {
        flex: 1;
        display: flex;
        justify-content: center;
        align-items: flex-start;
        padding: 3rem 1.5rem;
        box-sizing: border-box;
    }

    .join-state {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1.25rem;
        text-align: center;
        color: var(--color-text);
        max-width: 28rem;
    }

    .join-error {
        color: var(--color-danger);
    }

    .join-action-btn {
        border: none;
        cursor: pointer;
        border-radius: var(--radius-md);
        padding: 0.85rem 1.75rem;
        font-size: 0.95rem;
        font-weight: 600;
        background-color: var(--color-primary);
        color: var(--color-on-primary);
        transition: background-color 0.2s ease;
    }
    .join-action-btn:hover {
        background-color: var(--color-primary-dark);
    }
</style>
