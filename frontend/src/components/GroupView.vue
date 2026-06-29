<script setup>
    import { ref, onMounted } from 'vue'
    import api from '@/api/api';
    import { useRouter } from 'vue-router'
    import PageHeader from '@/components/PageHeader.vue';

    const groups = ref([])
    const loading = ref(false)
    const showPopup = ref(false)
    const newGroupName = ref("")
    const router = useRouter()

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
        <PageHeader title="Meine Gruppen">
            <button class="header-btn" @click="showPopup = true">+ Neue Gruppe</button>
        </PageHeader>
        <header>
            <h3>Meine Gruppen</h3>
            <button class="desktop-create-btn" @click="showPopup = true">
                <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                    <path d="M440-440H200v-80h240v-240h80v240h240v80H520v240h-80v-240Z"/>
                </svg>
                <span>Neue Gruppe</span>
            </button>
        </header>

        <button class="mobile-fab-btn" @click="showPopup = true">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                <path d="M440-440H200v-80h240v-240h80v240h240v80H520v240h-80v-240Z"/>
            </svg>
        </button>

        <main class="page-content">
            <div id="group-grid">
                <div v-for="group in groups" :key="group.id" class="group-card"
                @click="router.push({ name: 'group-detail', params: { id: group.id } })">
                    
                    <div class="card-main-content">
                        <div class="group-icon-box">
                            <svg xmlns="http://www.w3.org/2000/svg" 
                                 height="22px" 
                                 viewBox="0 -960 960 960" 
                                 width="22px" >
                                 <path d="M40-160v-112q0-34 17.5-62.5T104-378q62-31 126-46.5T360-440q66 0 130 15.5T616-378q29 15 46.5 43.5T680-272v112H40Zm720 0v-120q0-44-24.5-84.5T666-434q51 6 96 20.5t84 35.5q36 20 55 44.5t19 53.5v120H760ZM247-527q-47-47-47-113t47-113q47-47 113-47t113 47q47 47 47 113t-47 113q-47 47-113 47t-113-47Zm466 0q-47 47-113 47-11 0-28-2.5t-28-5.5q27-32 41.5-71t14.5-81q0-42-14.5-81T544-792q14-5 28-6.5t28-1.5q66 0 113 47t47 113q0 66-47 113ZM120-240h480v-32q0-11-5.5-20T580-306q-54-27-109-40.5T360-360q-56 0-111 13.5T140-306q-9 5-14.5 14t-5.5 20v32Zm296.5-343.5Q440-607 440-640t-23.5-56.5Q393-720 360-720t-56.5 23.5Q280-673 280-640t23.5 56.5Q327-560 360-560t56.5-23.5ZM360-240Zm0-400Z"/>
                            </svg>
                        </div>
                        <div class="group-info">
                            <h3>{{ group.name }}</h3>
                            <span>{{ group.member_count }} Mitglieder</span>
                        </div>
                        
                        <div class="forward-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" 
                            height="22px" 
                            viewBox="0 -960 960 960" 
                            width="22px">
                            <path d="m321-80-71-71 329-329-329-329 71-71 400 400L321-80Z"/></svg>
                        </div>
                    </div>

                    <div class="card-stats-area">
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
        background-color: var(--color-bg-page);
        display: flex;
        flex-direction: column;
    }

    .header-btn {
        background-color: #3db897;
    }
    header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        background-color: var(--color-bg-card);
        box-shadow: 0 0.2rem 0.6rem rgba(0, 0, 0, 0.05);
        box-sizing: border-box;
        padding: 1rem 1.5rem;
        min-height: 4.8rem;
    }
    
    header h3 {
        font-size: 1.2rem;
        font-weight: 600;
        margin: 0;
        /* Schiebt den Text mobil weiter nach rechts wegen der Menübar */
        padding-left: 130px; 
        color: var(--color-text);
    }
    
    /* --- MOBILE BUTTON (FLOATING ACTION BUTTON) --- */
    .mobile-fab-btn {
        position: fixed;
        bottom: 2rem;
        right: 1.5rem;
        z-index: 90;
        background-color: var(--color-primary);
        color: white;
        border: none;
        cursor: pointer;
        
        /* Macht den Button mobil kreisrund */
        width: 3.5rem;
        height: 3.5rem;
        border-radius: 50%;
        padding: 0;
        
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 14px rgba(61, 184, 151, 0.4);
        transition: all 0.2s ease;
    }
    .header-btn:hover {
        background-color: #2da081;

    }
    .mobile-fab-btn:active {
        transform: scale(0.95);
    }

    /* Das SVG-Icon innerhalb des mobilen Kreises formatieren */
    .mobile-fab-btn svg {
        width: 1.75rem;
        height: 1.75rem;
    }

    /* --- DESKTOP BUTTON --- */
    .desktop-create-btn {
        /* Standardmäßig auf mobilen Geräten komplett ausblenden */
        display: none; 
    }

    .page-content {
        flex: 1;
        display: flex;
        justify-content: center;
        padding: 1rem;
        box-sizing: border-box;
    }
    
    #group-grid {
        display: grid;
        grid-template-columns: 1fr; 
        gap: 1rem;             
        width: 100%;
        max-width: 58rem;  
        align-content: start;
    }

    .group-card {
        display: flex;
        flex-direction: column;     
        justify-content: flex-start;
        gap: 1.2rem;                
        background-color: var(--color-bg-card); 
        padding: 1.25rem;     
        border-radius: var(--radius-md);     
        box-shadow: 0 0.2rem 0.8rem rgba(0, 0, 0, 0.03);
        box-sizing: border-box;
        cursor: pointer;                                 
        border: 2px solid transparent;       
        transition: all 0.2s ease;
    }
    
    .group-card:hover {
        border-color: var(--color-primary);              
        box-shadow: 0 0.6rem 1.8rem rgba(61, 184, 151, 0.08); 
    }
    
    .group-card:hover .forward-icon svg {
        fill: var(--color-primary);
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
        background-color: #e8f7f3; 
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
    }
    .group-info h3 {
        margin: 0;
        font-size: 1.1rem;
        font-weight: 600;
        color: var(--color-text);
    }
    .group-info span {
        font-size: 0.85rem;
        color: var(--color-text-muted);           
    }

    .card-stats-area {
        display: flex;
        gap: 1rem;
        font-size: 0.85rem;
        color: var(--color-text-muted);
    }

    .forward-icon {
        margin-left: auto;
        display: flex;
        align-items: center;
    }
    
    .forward-icon svg {
        fill: #94a3b8;
        transition: fill 0.2s ease;
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
    #popup-content input[type="text"] {
        width: 100%;
        padding: 0.85rem 1rem;
        font-size: 1rem;
        border: 1px solid var(--color-border);
        border-radius: var(--radius-md);
        outline: none;
        color: var(--color-text);
        transition: all 0.2s ease;
        box-sizing: border-box;
        background-color: var(--color-bg-page);
    }
    #popup-content input[type="text"]:focus {
        border-color: var(--color-primary);
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
        border-radius: var(--radius-md);
        padding: 0.85rem 1.5rem;
        font-size: 0.95rem;
        font-weight: 600;
        transition: all 0.2s ease;
        flex: 1;
    }
    #cancle-btn {
        background-color: #f1f5f9;
        color: #64748b;
    }
    #cancle-btn:hover {
        background-color: #e2e8f0;
    }
    #create-btn {
        background-color: var(--color-primary);
        color: white;
    }
    #create-btn:hover {
        background-color: var(--color-primary-dark);
    }

    /* --- TABLET / DESKTOP OPTIMIERUNGEN --- */
    @media (min-width: 480px) {
        header {
            padding: 1.2rem 2rem;
        }

        header h3 {
            font-size: 1.25rem;
            /* Auf Desktop reicht das ursprüngliche Standard-Padding */
            padding-left: 95px; 
        }

        /* Schwebenden Mobile-Button auf Desktop unsichtbar machen */
        .mobile-fab-btn {
            display: none;
        }

        /* Desktop-Button im Header oben rechts einblenden und stylen */
        .desktop-create-btn {
            display: flex;
            align-items: center;
            gap: 0.4rem;
            background-color: var(--color-primary);
            color: white;
            border: none;
            cursor: pointer;
            border-radius: var(--radius-md);
            padding: 0.6em 1.4em;
            font-size: 0.9rem;
            font-weight: 600;
            transition: all 0.2s ease;
            box-shadow: none;
        }

        .desktop-create-btn:hover {
            background-color: var(--color-primary-dark);
        }

        .desktop-create-btn svg {
            width: 1.2rem;
            height: 1.2rem;
        }

        #group-grid {
            grid-template-columns: repeat(auto-fill, minmax(26rem, 1fr)); 
            gap: 1.5rem;             
        }

        .group-card {
            padding: 1.5rem;
            border-radius: var(--radius-lg);
        }

        .page-content {
            padding: 3rem 2rem;
        }

        #popup-content {
            padding: 2.5rem;
            gap: 1.5rem;
        }

        #popup-actions button {
            flex: none;
        }
    }
</style>