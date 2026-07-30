<script setup>
import { useRoute, useRouter } from 'vue-router'
import { ref, onMounted, watch, computed } from 'vue'
import api from '@/api/api';
import PageHeader from '@/components/PageHeader.vue';
import HeaderButton from '@/components/HeaderButton.vue';
import { useUserStore } from '@/store/userStore'


import ConfirmDialog from '@/components/ConfirmDialog.vue';

const route = useRoute()
const router = useRouter()

const groupId = computed(() => route.params.id)
const group = ref(null)
const loading = ref(false)
const showPopup = ref(false)
const newMemberMail = ref("")

const userStore = useUserStore()

const goToProfile = (member) => {
    router.push({ name: 'user-profile', params: { id: member.id } })
}

const fetchGroup = async () => {
    try {
        loading.value = true;
        const response = await api.get(`groups/${groupId.value}/`);
        group.value = response.data;
    } catch(err) {
        console.error('Fehler beim Laden der Gruppe: ', err)
    } finally {
        loading.value = false;
    }
}

const inviteMember = async () => {
    if (!newMemberMail.value.trim()) return;
    try {
        const response = await api.post(`groups/${groupId.value}/invite/`, {
            email: newMemberMail.value
        });
    
        group.value = response.data;
        showPopup.value = false;
        newMemberMail.value = ""
    } catch(error) {
        console.error("Fehler beim Einladen:", error.response?.data || error.message);
        alert(error.response?.data?.error || "Es gab ein Problem beim Hinzufügen.");
    }
}

// Bestätigungs-Dialoge
const confirmAction = ref(null);
const memberToDelete = ref(null);
const actionBusy = ref(false);

const askDeleteMember = (email) => {
    memberToDelete.value = email;
    confirmAction.value = 'deleteMember';
};

const askDeleteGroup = () => { confirmAction.value = 'deleteGroup' };
const askLeaveGroup = () => { confirmAction.value = 'leaveGroup' };

const cancleConfirm = () => {
    confirmAction.value = null;
    memberToDelete.value = null;
};

const confirmConfig = computed(() => {
    switch (confirmAction.value) {
        case 'deleteMember':
            return {
                title: 'Mitglied entfernen?',
                message: `Möchtest du ${memberToDelete.value} wirklich aus der Gruppe entfernen?`,
                confirmLabel: 'Entfernen'
            };
        case 'deleteGroup':
            return {
                title: 'Gruppe löschen?',
                message: 'Die Gruppe wird dauerhaft gelöscht. Diese Aktion kann nicht rückgängig gemacht werden.',
                confirmLabel: 'Löschen'
            };
        case 'leaveGroup':
            return {
                title: 'Gruppe verlassen?',
                message: 'Möchtest du diese Gruppe wirklich verlassen?',
                confirmLabel: 'Verlassen'
            };
        default:
            return {};
    }
});

const handleConfirm = () => {
    if (confirmAction.value === 'deleteMember') return deleteMember();
    if (confirmAction.value === 'deleteGroup') return deleteGroup();
    if (confirmAction.value === 'leaveGroup') return leaveGroup();
};


const deleteMember = async () => {
    try{
        actionBusy.value = true;
        const response = await api.delete(`groups/${groupId.value}/kick`, {
            data: { email: memberToDelete.value }
        });
    
        group.value = response.data;
        cancleConfirm();
    } catch (error) {
        console.error("Fehler beim Löschen des Mitglieds:", error);
        alert(error.response?.data?.error || "Es gab ein Problem beim Entfernen des Mitglieds.");
    } finally {
        actionBusy.value = false;
    }
};

const deleteGroup = async () =>{
    try{
        actionBusy.value = true;
        await api.delete(`groups/${groupId.value}/`);
        router.push("/group");
    } catch (error) {
        console.error("Fehler beim Löschen der Gruppe:", error);
        alert(error.response?.data?.error || "Es gab ein Problem beim Löschen der Gruppe.");
        actionBusy.value = false;
    }
};

const leaveGroup = async () =>{
    try{
        actionBusy.value = true;
        await api.post(`groups/${groupId.value}/leave`);
        router.push("/group");
    } catch (error) {
        console.error("Fehler beim Verlassen der Gruppe:", error);
        alert(error.response?.data?.error || "Es gab ein Problem beim Verlassen der Gruppe.");
        actionBusy.value = false;
    }
};

watch(() => route.params.id, (newId) => {
    if (newId) fetchGroup();
})

onMounted(() => {
    fetchGroup();
})
</script>

<template>
    <div class="page-container">
        <div v-if="loading" class="loading-state">
            <p>Gruppe wird geladen...</p>
        </div>

        <template v-else-if="group">
            <PageHeader>
                <HeaderButton v-if="group.is_admin" class="desktop-create-btn" @click="askDeleteGroup">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                        <path d="m376-300 104-104 104 104 56-56-104-104 104-104-56-56-104 104-104-104-56 56 104 104-104 104 56 56Zm-96 180q-33 0-56.5-23.5T200-200v-520h-40v-80h200v-40h240v40h200v80h-40v520q0 33-23.5 56.5T680-120H280Zm400-600H280v520h400v-520Zm-400 0v520-520Z"/>
                    </svg>
                    <span>Gruppe Löschen</span>
                </HeaderButton>
            </PageHeader>
            
            <button v-if="group.is_admin" @click="showPopup = true" class="mobile-fab-btn">
                <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                    <path d="M720-400v-120H600v-80h120v-120h80v120h120v80H800v120h-80ZM247-527q-47-47-47-113t47-113q47-47 113-47t113 47q47 47 47 113t-47 113q-47 47-113 47t-113-47ZM40-160v-112q0-34 17.5-62.5T104-378q62-31 126-46.5T360-440q66 0 130 15.5T616-378q29 15 46.5 43.5T680-272v112H40Zm80-80h480v-32q0-11-5.5-20T580-306q-54-27-109-40.5T360-360q-56 0-111 13.5T140-306q-9 5-14.5 14t-5.5 20v32Zm296.5-343.5Q440-607 440-640t-23.5-56.5Q393-720 360-720t-56.5 23.5Q280-673 280-640t23.5 56.5Q327-560 360-560t56.5-23.5ZM360-640Zm0 400Z"/>
                </svg>
            </button>

            <main class="page-content">
                <div class="group-card">
                    <div class="card-main-content">
                        <div class="group-icon-box">
                            <svg xmlns="http://www.w3.org/2000/svg" height="22px" viewBox="0 -960 960 960" width="22px">
                                <path d="M40-160v-112q0-34 17.5-62.5T104-378q62-31 126-46.5T360-440q66 0 130 15.5T616-378q29 15 46.5 43.5T680-272v112H40Zm720 0v-120q0-44-24.5-84.5T666-434q51 6 96 20.5t84 35.5q36 20 55 44.5t19 53.5v120H760ZM247-527q-47-47-47-113t47-113q47-47 113-47t113 47q47 47 47 113t-47 113q-47 47-113 47t-113-47Zm466 0q-47 47-113 47-11 0-28-2.5t-28-5.5q27-32 41.5-71t14.5-81q0-42-14.5-81T544-792q14-5 28-6.5t28-1.5q66 0 113 47t47 113q0 66-47 113ZM120-240h480v-32q0-11-5.5-20T580-306q-54-27-109-40.5T360-360q-56 0-111 13.5T140-306q-9 5-14.5 14t-5.5 20v32Zm296.5-343.5Q440-607 440-640t-23.5-56.5Q393-720 360-720t-56.5 23.5Q280-673 280-640t23.5 56.5Q327-560 360-560t56.5-23.5ZM360-240Zm0-400Z"/>
                            </svg>
                        </div>
                        <div class="group-info">
                            <h3>{{ group.name }}</h3>
                            <span>{{ group.member_count }} Mitglieder</span>
                        </div>
                        
                        <div class="button-group">
                            <button v-if="group.is_admin" @click="showPopup = true" class="action-btn desktop-invite-btn">
                                <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="currentColor">
                                    <path d="M720-400v-120H600v-80h120v-120h80v120h120v80H800v120h-80ZM247-527q-47-47-47-113t47-113q47-47 113-47t113 47q47 47 47 113t-47 113q-47 47-113 47t-113-47ZM40-160v-112q0-34 17.5-62.5T104-378q62-31 126-46.5T360-440q66 0 130 15.5T616-378q29 15 46.5 43.5T680-272v112H40Zm80-80h480v-32q0-11-5.5-20T580-306q-54-27-109-40.5T360-360q-56 0-111 13.5T140-306q-9 5-14.5 14t-5.5 20v32Zm296.5-343.5Q440-607 440-640t-23.5-56.5Q393-720 360-720t-56.5 23.5Q280-673 280-640t23.5 56.5Q327-560 360-560t56.5-23.5ZM360-640Zm0 400Z"/>
                                </svg>
                                <span>Einladen</span>
                            </button>

                            <button @click="askLeaveGroup" class="leave-btn">
                                <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="currentColor">
                                    <path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h280v80H200v560h280v80H200Zm440-160-55-58 102-102H360v-80h327L585-622l55-58 200 200-200 200Z"/>
                                </svg>
                                <span>Verlassen</span>
                            </button>
                        </div>
                    </div>

                    <div class="card-stats-area">
                        <h4>Mitglieder</h4>
                        <ul class="member-list">
                            <li v-for="member in group.members" :key="member.id" class="member-item">
                                <img v-if="member.profilbild" :src="member.profilbild" alt="Profilbild" 
                                    class="member-avatar-img" @click="goToProfile(member)"/>
                                <div v-else class="member-avatar" @click="goToProfile(member)">
                                    {{ (member.first_name || member.email).charAt(0).toUpperCase() }}
                                </div>
                                
                                <div class="member-info-text">
                                    <span class="member-name">
                                        <template v-if="member.first_name || member.last_name">
                                            {{ member.first_name }} {{ member.last_name }}
                                        </template>
                                        <template v-else>
                                            {{ member.username }}
                                        </template>
                                        <span v-if="member.email === group.admin_email" class="admin-badge">Admin</span>
                                    </span>
                                    <span class="member-email">{{ member.email }}</span>
                                </div>

                                <div v-if="group.is_admin && member.email !== group.admin_email" class="delete-member" @click="askDeleteMember(member.email)">
                                    <svg xmlns="http://www.w3.org/2000/svg" height="22px" viewBox="0 -960 960 960" width="22px">
                                        <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/>
                                    </svg>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>
            </main>

            <div v-if="showPopup" @click.self="showPopup = false" id="popup-overlay">
                <div id="popup-content">
                    <h3>Mitglieder einladen</h3>
                    <input v-model="newMemberMail" type="email" placeholder="max@mail.de" @keyup.enter="inviteMember">
                    <div id="popup-actions">
                        <button @click="showPopup = false" id="cancel-btn">Abbrechen</button>
                        <button @click="inviteMember" id="create-btn">Einladen</button>
                    </div>
                </div>
            </div>
            <ConfirmDialog
                v-if="confirmAction"
                :title="confirmConfig.title"
                :message="confirmConfig.message"
                :confirm-label="confirmConfig.confirmLabel"
                danger
                :busy="actionBusy"
                @confirm="handleConfirm"
                @cancel="cancleConfirm"
            />
        </template>
    </div>
</template>

<style scoped>
    @media (max-width: 480px) {
    .field-row {
            flex-direction: column;
            gap: 0;
        }
    }
    .page-container {
        min-height: 100vh;
        background-color: var(--color-bg-page);
        display: flex;
        flex-direction: column;
    }

    header h3 {
        font-size: 1.2rem;
        font-weight: 600;
        margin: 0;
        padding-left: 130px;
        color: var(--color-text);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .desktop-create-btn {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        background-color: var(--color-danger);
        color: var(--color-on-primary);
        border: none;
        padding: 0.5rem 1rem;
        border-radius: var(--radius-md);
        cursor: pointer;
        font-weight: 600;
    }

    .mobile-fab-btn {
        position: fixed;
        bottom: 2rem;
        right: 1.5rem;
        z-index: 90;
        background-color: var(--color-primary);
        color: var(--color-on-primary);
        border: none;
        cursor: pointer;
        width: 3.5rem;
        height: 3.5rem;
        border-radius: 50%;
        padding: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 14px rgba(var(--color-primary-rgb), 0.4);
        transition: all 0.2s ease;
    }
    .mobile-fab-btn:active {
        transform: scale(0.95);
    }

    .button-group {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .desktop-invite-btn {
        display: none; 
    }

    .leave-btn {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background-color: transparent;
        border: 1px solid var(--color-danger);
        color: var(--color-danger);
        cursor: pointer;
        border-radius: var(--radius-md);
        padding: 0.6em 1.2em;
        font-size: 0.9rem;
        font-weight: 600;
        transition: all 0.2s ease;
        white-space: nowrap;
    }
    .leave-btn:hover {
        background-color: var(--color-danger-bg);
    }

    .page-content {
        flex: 1;
        display: flex;
        justify-content: center;
        padding: 1rem;
        box-sizing: border-box;
    }

    .group-card {
        display: flex;
        flex-direction: column;    
        justify-content: flex-start;
        gap: 1.5rem;                
        background-color: var(--color-bg-card); 
        padding: 1.25rem;     
        border-radius: var(--radius-md);     
        box-shadow: 0 0.2rem 0.8rem rgba(0, 0, 0, 0.03);
        box-sizing: border-box;
        width: 100%;
        max-width: 45rem;  
        border: 2px solid transparent;
        align-self: start;
    }

    .card-main-content {
        display: flex;
        align-items: center;
        width: 100%;
        gap: 1rem;
    }

    .group-icon-box {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 3rem;          
        height: 3rem;
        background-color: var(--color-primary-soft);
        border-radius: var(--radius-md);     
        flex-shrink: 0;            
    }
    .group-icon-box svg {
        width: 1.5rem;
        height: 1.5rem;
        fill: var(--color-primary);
    }
    
    .group-info {
        display: flex;
        flex-direction: column;
        gap: 0.1rem;   
        flex-grow: 1;      
        min-width: 0;
    }
    .group-info h3 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--color-text);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .group-info span {
        font-size: 0.85rem;
        color: var(--color-text-muted);           
    }

    .card-stats-area {
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
    }
    .card-stats-area h4 {
        margin: 0;
        font-size: 1rem;
        font-weight: 600;
        color: var(--color-text);
        border-bottom: 2px solid var(--color-bg-page);
        padding-bottom: 0.5rem;
    }

    .member-list {
        list-style: none;
        padding: 0;
        margin: 0;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .member-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.6rem;
        background-color: var(--color-bg-page);
        border-radius: var(--radius-md);
        border: 1px solid var(--color-border);
    }

    .member-avatar-img {
        width: 2.2rem;
        height: 2.2rem;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid var(--color-primary); 
    }

    .member-avatar {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 2.2rem;
        height: 2.2rem;
        background-color: var(--color-primary-soft);
        color: var(--color-primary);
        font-weight: 600;
        font-size: 0.95rem;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .member-info-text {
        display: flex;
        flex-direction: column;
        gap: 0.1rem;
        min-width: 0; 
    }

    .member-name {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--color-text);
    }

    .member-email {
        font-size: 0.8rem;
        color: var(--color-text-muted);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .admin-badge {
        font-size: 0.7rem;
        background-color: var(--color-primary-soft);
        color: var(--color-primary);
        padding: 0.1rem 0.4rem;
        border-radius: var(--radius-sm);
        font-weight: 500;
    }

    .delete-member {
        margin-left: auto;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        transition: background-color 0.2s ease, transform 0.1s ease;
        flex-shrink: 0;
    }
    .delete-member svg {
        fill: var(--color-text-muted);
    }
    .delete-member:hover {
        background-color: var(--color-danger-bg);
    }
    .delete-member:hover svg {
        fill: var(--color-danger);
    }

    #popup-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-color: rgba(44, 62, 80, 0.4); 
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 999;
        backdrop-filter: blur(4px); 
        padding: 1rem;
        box-sizing: border-box;
    }

    #popup-content {
        background: var(--color-bg-card);
        padding: 1.5rem;
        border-radius: var(--radius-lg);
        width: 100%;
        max-width: 28rem;
        box-shadow: 0 1rem 3rem rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        gap: 1.25rem;
        box-sizing: border-box;
    }
    #popup-content h3 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--color-text);
    }
    #popup-content input[type="email"] {
        width: 100%;
        padding: 0.85rem 1rem;
        font-size: 1rem;
        border: 1px solid var(--color-border);
        border-radius: var(--radius-md);
        outline: none;
        color: var(--color-text);
        box-sizing: border-box;
        background-color: var(--color-bg-page);
    }
    #popup-content input[type="email"]:focus {
        border-color: var(--color-primary);
    }
    #popup-actions {
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
    }
    #popup-actions button {
        border: none;
        cursor: pointer;
        border-radius: var(--radius-md);
        padding: 0.85rem 1.5rem;
        font-size: 0.95rem;
        font-weight: 600;
        flex: 1;
    }
    #cancel-btn {
        background-color: var(--color-bg-hover);
        color: var(--color-text-muted);
    }
    #create-btn {
        background-color: var(--color-primary);
        color: var(--color-on-primary);
    }

    .loading-state {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        color: var(--color-text-muted);
    }

    .member-avatar-img,
    .member-avatar {
        cursor: pointer;
    }


    @media (min-width: 480px) {
        header h3 {
            padding-left: 95px; 
        }
        .page-content {
            padding: 3rem 2rem;
        }
        .group-card {
            padding: 2rem;
        }
        .mobile-fab-btn {
            display: none;
        }
        .desktop-invite-btn {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background-color: var(--color-primary);
            color: var(--color-on-primary);
            border: none;
            cursor: pointer;
            border-radius: var(--radius-md);
            padding: 0.6em 1.4em;
            font-size: 0.9rem;
            font-weight: 600;
            white-space: nowrap;
        }
        .desktop-invite-btn:hover {
            background-color: var(--color-primary-dark);
        }
    }
</style>