<script setup>
import { useRoute } from 'vue-router'
import { ref, onMounted } from 'vue'
import api from '@/api/api';

const route = useRoute()
const groupId = route.params.id
const group = ref(null)
const loading = ref(false)
const showPopup = ref(false)
const newMemberMail = ref("")

const fetchGroup = async () => {
    try {
        loading.value = true;
        const response = await api.get(`groups/${groupId}/`);
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
        const response = await api.post(`groups/${groupId}/invite/`, {
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

const deleteMember = async (email) => {
    if (!confirm(`Möchtest du das Mitglied (${email}) wirklich aus der Gruppe entfernen?`)) return;

    try{
        const response = await api.delete(`groups/${groupId}/`, {
            data: { email: email }
        });
        
        group.value = response.data;
    } catch (error) {
        console.error("Fehler beim Löschen des Mitglieds:", error);
        alert(error.response?.data?.error || "Es gab ein Problem beim Entfernen des Mitglieds.");
    }
}

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
            <header>
                <h3>{{ group.name }}</h3>
            </header>
            
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
                        
                        <button v-if="group.is_admin" @click="showPopup = true" class="action-btn">
                            <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="#ffffff">
                                <path d="M720-400v-120H600v-80h120v-120h80v120h120v80H800v120h-80ZM247-527q-47-47-47-113t47-113q47-47 113-47t113 47q47 47 47 113t-47 113q-47 47-113 47t-113-47ZM40-160v-112q0-34 17.5-62.5T104-378q62-31 126-46.5T360-440q66 0 130 15.5T616-378q29 15 46.5 43.5T680-272v112H40Zm80-80h480v-32q0-11-5.5-20T580-306q-54-27-109-40.5T360-360q-56 0-111 13.5T140-306q-9 5-14.5 14t-5.5 20v32Zm296.5-343.5Q440-607 440-640t-23.5-56.5Q393-720 360-720t-56.5 23.5Q280-673 280-640t23.5 56.5Q327-560 360-560t56.5-23.5ZM360-640Zm0 400Z"/>
                            </svg>
                            Einladen
                        </button>
                    </div>

                    <div class="card-stats-area">
                        <h4>Mitglieder</h4>
                        <ul class="member-list">
                            <li v-for="member in group.members" :key="member.id" class="member-item">
                                
                                <img 
                                    v-if="member.profilbild" 
                                    :src="member.profilbild" 
                                    alt="Profilbild" 
                                    class="member-avatar-img"
                                />
                                <div v-else class="member-avatar">
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

                                <div v-if="group.is_admin && member.email !== group.admin_email" class="delete-member" @click="deleteMember(member.email)">
                                    <svg xmlns="http://www.w3.org/2000/svg" 
                                    height="22px" 
                                    viewBox="0 -960 960 960" 
                                    width="22px">
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
                        <button @click="showPopup = false" id="cancle-btn">Abbrechen</button>
                        <button @click="inviteMember" id="create-btn">Einladen</button>
                    </div>
                </div>
            </div>
        </template>
    </div>
</template>

<style scoped>
    .page-container {
        min-height: 100vh;
        background-color: #f8f9fa;
        display: flex;
        flex-direction: column;
    }

    header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        background-color: #ffffff;
        box-shadow: 0 0.2rem 0.6rem rgba(0, 0, 0, 0.05);
        box-sizing: border-box;
        padding: 1.2rem 2rem;
    }
    header h3 {
        font-size: 1.25rem;
        font-weight: 500;
        margin: 0;
        color: #2c3e50;
    }

    .page-content {
        flex: 1;
        display: flex;
        justify-content: center;
        padding: 3rem 2rem;
        box-sizing: border-box;
    }

    .group-card {
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
        width: 3.2rem;          
        height: 3.2rem;
        background-color: #e8f7f3; 
        border-radius: 0.6rem;     
        flex-shrink: 0;            
    }
    .group-icon-box svg {
        width: 1.6rem;
        height: 1.6rem;
        fill: #3db897;
    }
    
    .group-info {
        display: flex;
        flex-direction: column;
        gap: 0.2rem;   
        flex-grow: 1;      
    }
    .group-info h3 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 600;
        color: #2c3e50;
    }
    .group-info span {
        font-size: 0.9rem;
        color: #7f8c8d;           
    }

    .action-btn {
        background-color: #3db897;
        color: white;
        border: none;
        cursor: pointer;
        border-radius: 0.6rem;
        padding: 0.6em 1.4em;
        font-size: 0.9rem;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        transition: all 0.2s ease;
    }
    .action-btn:hover {
        background-color: #2da081;
    }

    .card-stats-area {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    .card-stats-area h4 {
        margin: 0;
        font-size: 1.05rem;
        font-weight: 600;
        color: #2c3e50;
        border-bottom: 2px solid #f1f5f9;
        padding-bottom: 0.5rem;
    }

    .member-list {
        list-style: none;
        padding: 0;
        margin: 0;
        display: flex;
        flex-direction: column;
        gap: 0.6rem;
    }

    .member-item {
        display: flex;
        align-items: center;
        gap: 1rem;
        padding: 0.6rem 0.8rem;
        background-color: #f8fafc;
        border-radius: 0.6rem;
        border: 1px solid #e2e8f0;
    }

    .member-avatar-img {
        width: 2.2rem;
        height: 2.2rem;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid #3db897; 
    }

    .member-avatar {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 2.2rem;
        height: 2.2rem;
        background-color: #e8f7f3;
        color: #3db897;
        font-weight: 600;
        font-size: 0.95rem;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .member-info-text {
        display: flex;
        flex-direction: column;
        gap: 0.1rem;
    }

    .member-name {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.95rem;
        font-weight: 600;
        color: #2c3e50;
    }

    .member-email {
        font-size: 0.85rem;
        color: #7f8c8d;
    }

    .admin-badge {
        font-size: 0.75rem;
        background-color: #e8f7f3;
        color: #3db897;
        padding: 0.1rem 0.4rem;
        border-radius: 0.4rem;
        font-weight: 500;
    }

    .delete-member {
        margin-left: auto;
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 2.2rem;
        height: 2.2rem;
        border-radius: 50%;
        transition: background-color 0.2s ease, transform 0.1s ease;
    }
    
   
    .delete-member svg {
        fill: #94a3b8; 
        transition: fill 0.2s ease;
    }

   
    .delete-member:hover {
        background-color: #fee2e2; 
    }
    
    .delete-member:hover svg {
        fill: #ef4444; 
    }

    .delete-member:active {
        transform: scale(0.9); 
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
    }

    #popup-content {
        background: #ffffff;
        padding: 2.5rem;
        border-radius: 1.2rem;
        width: 100%;
        max-width: 28rem;
        box-shadow: 0 1rem 3rem rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        box-sizing: border-box;
    }
    #popup-content h3 {
        margin: 0;
        font-size: 1.4rem;
        font-weight: 600;
        color: #2c3e50;
    }
    #popup-content input[type="email"] {
        width: 100%;
        padding: 0.8rem 1rem;
        font-size: 1rem;
        border: 2px solid #e2e8f0;
        border-radius: 0.6rem;
        outline: none;
        color: #2c3e50;
        transition: all 0.2s ease;
        box-sizing: border-box;
    }
    #popup-content input[type="email"]:focus {
        border-color: #3db897;
        box-shadow: 0 0 0 3px rgba(61, 184, 151, 0.15);
    }
    #popup-actions {
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
    }
    #popup-actions button {
        border: none;
        cursor: pointer;
        border-radius: 0.6rem;
        padding: 0.7em 1.5em;
        font-size: 0.95rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    #cancle-btn {
        background-color: #f1f5f9;
        color: #64748b;
    }
    #cancle-btn:hover {
        background-color: #e2e8f0;
        color: #475569;
    }
    #create-btn {
        background-color: #3db897;
        color: white;
        box-shadow: 0 0.2rem 0.8rem rgba(61, 184, 151, 0.2);
    }
    #create-btn:hover {
        background-color: #2da081;
        box-shadow: 0 0.4rem 1.2rem rgba(61, 184, 151, 0.3);
    }
    #create-btn:active {
        transform: scale(0.98);
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