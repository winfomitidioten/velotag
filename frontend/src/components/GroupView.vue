<script setup>
    import { ref, onMounted } from 'vue'
    import api from '@/api/api';

    const groups = ref([])
    const loading = ref(false)
    const showPopup = ref(false)
    const newGroupName = ref("")

    const fetchGroups = async () => {
        try {
            loading.value = true;
            const response = await api.get('groups/');
            groups.value = response.data;
        } catch(err) {
            console.error('Fehler: ', err)
        } finally {
            loading.value = false;
        }
    }

    const createNewGroup = async () => {
        if (!newGroupName.value.trim()) return;
        try {
            const response = await api.post('groups/', {
                name: newGroupName.value
            });
            
            const newGroup = response.data;
            groups.value.push(newGroup);
            showPopup.value = false;
            newGroupName.value = ""
        } catch(error) {
            console.error("Fehler beim Erstellen der Gruppe:", error.response?.data || error.message);
        }
    }

    onMounted(() => {
        fetchGroups()
    })
</script>

<template>
    <div class="page-container">
        <header>
            <h3>Meine Gruppen</h3>
            <button @click="showPopup = true"> + Neue Gruppe</button>
        </header>

        <main class="page-content">
            <div id="group-grid">
                <div v-for="group in groups" :key="group.id" class="group-card">
                    <div class="group-icon-box">
                        <svg xmlns="http://www.w3.org/2000/svg" 
                             height="24px" 
                             viewBox="0 -960 960 960" 
                             width="24px">
                            <path d="M200-80q-83 0-141.5-58.5T0-280q0-83 58.5-141.5T200-480q83 0 141.5 58.5T400-280q0 83-58.5 141.5T200-80Zm85-115q35-35 35-85t-35-85q-35-35-85-35t-85 35q-35 35-35 85t35 85q35 35 85 35t85-35Zm155-5v-200L312-512q-12-11-18-25.5t-6-30.5q0-16 6.5-30.5T312-624l112-112q12-12 27.5-18t32.5-6q17 0 32.5 6t27.5 18l76 76q28 28 64 44t76 16v80q-57 0-108.5-22T560-604l-32-32-96 96 88 92v248h-80Zm123.5-563.5Q540-787 540-820t23.5-56.5Q587-900 620-900t56.5 23.5Q700-853 700-820t-23.5 56.5Q653-740 620-740t-56.5-23.5ZM760-80q-83 0-141.5-58.5T560-280q0-83 58.5-141.5T760-480q83 0 141.5 58.5T960-280q0 83-58.5 141.5T760-80Zm85-115q35-35 35-85t-35-85q-35-35-85-35t-85 35q-35 35-35 85t35 85q35 35 85 35t85-35Z"/>
                        </svg>
                    </div>
                    <div class="group-info">
                        <h3>{{ group.name }}</h3>
                        <span>{{ group.member_count }} Mitglieder</span>
                    </div>
                </div>
            </div>
        </main>

        <div v-if="showPopup" @click.self="showPopup = false" id="popup-overlay">
            <div id="popup-content">
                <h3>Neue Gruppe erstellen</h3>
                <input v-model="newGroupName" type="text" placeholder="Name deiner Gruppe..." @keyup.enter="createNewGroup">
                <div id="popup-actions">
                    <button @click="showPopup = false" id="cancle-btn">Abbrechen</button>
                    <button @click="createNewGroup" id="create-btn">Erstellen</button>
                </div>
            </div>
        </div>
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
    header button {
        background-color: #3db897;
        color: white;
        border: none;
        cursor: pointer;
        border-radius: 0.6rem;
        padding: 0.6em 1.4em;
        font-size: 0.9rem;
        font-weight: 600;
        transition: all 0.2s ease;
    }
    header button:hover {
        background-color: #2da081;
    }

    .page-content {
        flex: 1;
        display: flex;
        justify-content: center;
        padding: 3rem 2rem;
        box-sizing: border-box;
    }
    #group-grid {
        display: grid;
        grid-template-columns: repeat(2, 1fr); 
        gap: 1.5rem;             
        width: 100%;
        max-width: 55rem;  
    }

    .group-card {
        display: flex;
        align-items: center;       
        gap: 1rem;               
        background-color: #ffffff; 
        padding: 1rem 1.2rem;
        border-radius: 0.8rem;     
        box-shadow: 0 0.4rem 1.2rem rgba(0, 0, 0, 0.02);
        box-sizing: border-box;
    }
    .group-icon-box {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 3.5rem;           
        height: 3.5rem;
        background-color: #e8f7f3; 
        border-radius: 0.8rem;     
        flex-shrink: 0;            
    }
    .group-icon-box svg {
        width: 1.8rem;
        height: 1.8rem;
        fill: #3db897;
    }
    .group-info {
        display: flex;
        flex-direction: column;
        gap: 0.3rem;          
    }
    .group-info h3 {
        margin: 0;
        font-size: 1.15rem;
        font-weight: 600;
        color: #2c3e50;
    }
    .group-info span {
        font-size: 0.9rem;
        color: #7f8c8d;           
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
    #popup-content input[type="text"] {
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
    #popup-content input[type="text"]:focus {
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
</style>