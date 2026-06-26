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
                <div class="main-card">
                    <div class="card-title-area">
                        <h4>Offene Einladungen</h4>
                    </div>

                    <div v-if="invites.length === 0" class="empty-state">
                        <p>Du hast aktuell keine offenen Einladungen.</p>
                    </div>

                    <ul v-else class="invite-list">
                        <li v-for="invite in invites" :key="invite.id" class="invite-item">
                            
                            <div class="invite-icon-box">
                                <svg xmlns="http://www.w3.org/2000/svg" height="22px" viewBox="0 -960 960 960" width="22px">
                                    <path d="M40-160v-112q0-34 17.5-62.5T104-378q62-31 126-46.5T360-440q66 0 130 15.5T616-378q29 15 46.5 43.5T680-272v112H40Zm720 0v-120q0-44-24.5-84.5T666-434q51 6 96 20.5t84 35.5q36 20 55 44.5t19 53.5v120H760ZM247-527q-47-47-47-113t47-113q47-47 113-47t113 47q47 47 47 113t-47 113q-47 47-113 47t-113-47Zm466 0q-47 47-113 47-11 0-28-2.5t-28-5.5q27-32 41.5-71t14.5-81q0-42-14.5-81T544-792q14-5 28-6.5t28-1.5q66 0 113 47t47 113q0 66-47 113ZM120-240h480v-32q0-11-5.5-20T580-306q-54-27-109-40.5T360-360q-56 0-111 13.5T140-306q-9 5-14.5 14t-5.5 20v32Zm296.5-343.5Q440-607 440-640t-23.5-56.5Q393-720 360-720t-56.5 23.5Q280-673 280-640t23.5 56.5Q327-560 360-560t56.5-23.5ZM360-240Zm0-400Z"/>
                                </svg>
                            </div>
                            
                            <div class="invite-info-text">
                                <span class="invite-label">Einladung zur Gruppe</span>
                                <span class="group-name">{{ invite.name }}</span>
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
                </div>
            </main>
        </template>
    </div>
</template>

<style scoped>
    /* Grundlayout & Container */
    .page-container {
        min-height: 100vh;
        background-color: #f8f9fa;
        display: flex;
        flex-direction: column;
    }

    .page-content {
        flex: 1;
        display: flex;
        justify-content: center;
        padding: 3rem 2rem;
        box-sizing: border-box;
    }

    /* Strukturierte Hauptkarte (analog zu GroupDetail) */
    .main-card {
        display: flex;
        flex-direction: column;    
        justify-content: flex-start;
        gap: 1.8rem;                
        background-color: #ffffff; 
        padding: 2rem;     
        border-radius: 0.8rem;     
        box-shadow: 0 0.4rem 1.2rem rgba(0, 0, 0, 0.02);
        box-sizing: border-box;
        width: 100%;
        max-width: 45rem;  
        border: 2px solid transparent;
    }

    .card-title-area h4 {
        margin: 0;
        font-size: 1.05rem;
        font-weight: 600;
        color: #2c3e50;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 0.5rem;
    }

    /* Listen- und Element-Styling */
    .invite-list {
        list-style: none;
        padding: 0;
        margin: 0;
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
    }

    .invite-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.8rem 1rem;
        background-color: #f8fafc;
        border-radius: 0.6rem;
        border: 1px solid #e2e8f0;
    }

    /* Icon Styling */
    .invite-icon-box {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 2.8rem;          
        height: 2.8rem;
        background-color: #e8f7f3; 
        border-radius: 0.6rem;     
        flex-shrink: 0;            
    }
    .invite-icon-box svg {
        width: 1.4rem;
        height: 1.4rem;
        fill: #3db897;
    }

    /* Textblöcke */
    .invite-info-text {
        display: flex;
        flex-direction: column;
        gap: 0.1rem;
    }
    .invite-label {
        font-size: 0.85rem;
        color: #7f8c8d;
    }
    .group-name {
        font-size: 1.05rem;
        font-weight: 600;
        color: #2c3e50;
    }

    /* Buttons & Actions ganz rechts ausrichten */
    .invite-actions {
        margin-left: auto;
        display: flex;
        gap: 0.6rem;
    }

    .invite-actions button {
        border: none;
        cursor: pointer;
        border-radius: 0.5rem;
        padding: 0.5em 1.2em;
        font-size: 0.85rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }

    /* Annehmen-Button (Dein typisches Mintgrün) */
    .btn-accept {
        background-color: #3db897;
        color: white;
        box-shadow: 0 0.1rem 0.4rem rgba(61, 184, 151, 0.15);
    }
    .btn-accept:hover {
        background-color: #2da081;
    }

    /* Ablehnen-Button (Passt sich dezent an, wird rot bei Hover) */
    .btn-decline {
        background-color: #f1f5f9;
        color: #64748b;
    }
    .btn-decline:hover {
        background-color: #fee2e2;
        color: #ef4444;
    }

    .invite-actions button:active {
        transform: scale(0.97);
    }

    /* Zustands-Designs (Empty & Loading) */
    .empty-state {
        text-align: center;
        padding: 2rem 0;
        color: #7f8c8d;
        font-size: 0.95rem;
    }

    .loading-state {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        color: #64748b;
        font-weight: 500;
    }
</style>