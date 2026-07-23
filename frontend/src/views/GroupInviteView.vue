<script setup>
import { ref, onMounted } from 'vue'
import api from '@/api/api';
import PageHeader from '@/components/PageHeader.vue';

const loading = ref(false);
const invites = ref([]);

const fetchInvites = async () => {
    try {
        loading.value = true;
        const response = await api.get('/user/invitations/');
        invites.value = response.data;
    } catch(err) {
        console.error('Fehler beim Laden der Einladungen: ', err)
    } finally {
        loading.value = false;
    }
}

const answerInvite = async (groupId, action) => {
    try {
        await api.post('/user/invitations/', {
            group_id: groupId,
            action: action
        })
        await fetchInvites();
    } catch(err) {
        console.error('Fehler beim Antworten auf die Einladung: ', err)
    }
}

onMounted(() => {
    fetchInvites();
})
</script>

<template>
    <div class="page-container">
        <div v-if="loading" class="loading-state">
            <p>Einladungen werden geladen...</p>
        </div>

        <template v-else>
            <PageHeader title="Gruppen Einladungen" />
            
            <main class="page-content">
                <div v-if="invites.length === 0" class="empty-state">
                    <p>Du hast aktuell keine offenen Einladungen.</p>
                </div>

                <ul v-else class="invite-grid">
                    <li v-for="invite in invites" :key="invite.id" class="invite-tile">
                        
                        <div class="invite-container">
                            <div class="invite-icon-box">
                                <svg xmlns="http://www.w3.org/2000/svg" height="22px" viewBox="0 -960 960 960" width="22px">
                                    <path d="M40-160v-112q0-34 17.5-62.5T104-378q62-31 126-46.5T360-440q66 0 130 15.5T616-378q29 15 46.5 43.5T680-272v112H40Zm720 0v-120q0-44-24.5-84.5T666-434q51 6 96 20.5t84 35.5q36 20 55 44.5t19 53.5v120H760ZM247-527q-47-47-47-113t47-113q47-47 113-47t113 47q47 47 47 113t-47 113q-47 47-113 47t-113-47Zm466 0q-47 47-113 47-11 0-28-2.5t-28-5.5q27-32 41.5-71t14.5-81q0-42-14.5-81T544-792q14-5 28-6.5t28-1.5q66 0 113 47t47 113q0 66-47 113ZM120-240h480v-32q0-11-5.5-20T580-306q-54-27-109-40.5T360-360q-56 0-111 13.5T140-306q-9 5-14.5 14t-5.5 20v32Zm296.5-343.5Q440-607 440-640t-23.5-56.5Q393-720 360-720t-56.5 23.5Q280-673 280-640t23.5 56.5Q327-560 360-560t56.5-23.5ZM360-240Zm0-400Z"/>
                                </svg>
                            </div>
                            
                            <div class="invite-info-text">
                                <span class="invite-label">Einladung zur Gruppe</span>
                                <span class="group-name">{{ invite.name }}</span>
                            </div>
                        </div>

                        <div class="invite-actions">
                            <button @click="answerInvite(invite.id, 'accept')" class="btn-accept">
                                Annehmen
                            </button>
                            <button @click="answerInvite(invite.id, 'decline')" class="btn-decline">
                                Ablehnen
                            </button>
                        </div>

                    </li>
                </ul>
            </main>
        </template>
    </div>
</template>

<style scoped>
    /* Grundlayout & Container */
    .page-container {
        min-height: 100vh;
        background-color: var(--color-bg-page);
        display: flex;
        flex-direction: column;
    }

    .page-content {
        flex: 1;
        width: 100%;
        max-width: 45rem; /* Gleiche maximale Breite wie zuvor für ein sauberes Center-Layout */
        margin: 0 auto;
        padding: 1.5rem 1rem;
        box-sizing: border-box;
    }

    /* Kachellisten-Layout */
    .invite-grid {
        list-style: none;
        padding: 0;
        margin: 0;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    /* KACHELN (Wie deine Gruppenübersicht) */
    .invite-tile {
        display: flex;
        flex-direction: column; /* Mobil untereinander brechen */
        gap: 1rem;
        padding: 1.25rem;
        
        /* Karten-Look: Heller Hintergrund direkt auf dunklerer Page */
        background-color: var(--color-bg-card);
        border-radius: var(--radius-md);
        border: 1px solid var(--color-border);
        
        /* Plastischer Schatteneffekt */
        box-shadow: 0 0.2rem 0.6rem rgba(0, 0, 0, 0.03);
        transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }
    
    /* Hover-Effekt für die Kacheln */
    .invite-tile:hover {
        border-color: var(--color-primary);
        box-shadow: 0 0.4rem 1rem rgba(0, 0, 0, 0.06);
        transform: translateY(-2px);
    }

    .invite-container {
        display: flex;
        align-items: center;
        gap: 0.85rem;
        min-width: 0;
    }

    /* Icon Styling */
    .invite-icon-box {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 2.8rem;          
        height: 2.8rem;
        background-color: var(--color-primary-soft); /* Dezenter Mint-Hintergrund fürs Icon */
        border-radius: var(--radius-md);     
        flex-shrink: 0;            
    }
    .invite-icon-box svg {
        width: 1.4rem;
        height: 1.4rem;
        fill: var(--color-primary);
    }

    /* Textblöcke */
    .invite-info-text {
        display: flex;
        flex-direction: column;
        gap: 0.1rem;
        min-width: 0;
    }
    .invite-label {
        font-size: 0.8rem;
        color: var(--color-text-muted);
    }
    .group-name {
        font-size: 1.05rem;
        font-weight: 600;
        color: var(--color-text);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    /* Buttons & Actions */
    .invite-actions {
        display: flex;
        gap: 0.5rem;
        width: 100%;
    }

    .invite-actions button {
        flex: 1;
        border: none;
        cursor: pointer;
        border-radius: var(--radius-md);
        padding: 0.7rem 1.2rem;
        font-size: 0.85rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    /* Annehmen-Button */
    .btn-accept {
        background-color: var(--color-primary);
        color: var(--color-on-primary);
        box-shadow: 0 2px 4px rgba(var(--color-primary-rgb), 0.15);
    }
    .btn-accept:hover {
        background-color: var(--color-primary-dark);
    }

    /* Ablehnen-Button */
    .btn-decline {
        background-color: var(--color-bg-page);
        color: var(--color-text-muted);
        border: 1px solid var(--color-border) !important;
    }
    .btn-decline:hover {
        background-color: var(--color-danger-bg);
        color: var(--color-danger);
        border-color: var(--color-danger-border) !important;
    }

    .invite-actions button:active {
        transform: scale(0.97);
    }

    /* Zustands-Designs (Empty & Loading) */
    .empty-state {
        text-align: center;
        padding: 3rem 0;
        color: var(--color-text-muted);
        font-size: 0.95rem;
    }

    .loading-state {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        color: var(--color-text-muted);
        font-weight: 500;
    }

    /* --- TABLET / DESKTOP OPTIMIERUNGEN --- */
    @media (min-width: 580px) {
        .page-content {
            padding: 2rem 0rem; /* Mehr Luft nach oben/unten im Desktop-Grid */
        }
        .invite-tile {
            flex-direction: row; /* Inhalte sauber nebeneinander legen */
            align-items: center;
            justify-content: space-between;
            padding: 1.1rem 1.5rem;
            border-radius: var(--radius-lg);
        }
        .invite-actions {
            margin-left: auto;
            display: flex;
            gap: 0.6rem;
            width: auto;
        }
        .invite-actions button {
            flex: none;
            padding: 0.55em 1.5em;
        }
    }
</style>