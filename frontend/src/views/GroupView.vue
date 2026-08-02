<script setup>
    import { ref, onMounted, watch } from 'vue'
    import api from '@/api/api';
    import { useRouter } from 'vue-router'
    import { useFavorite } from '@/composables/useFavorite.js'
    import HeaderButton from '@/components/HeaderButton.vue';
    import PageHeader from '@/components/PageHeader.vue';
    import CreateGroupModal from '@/components/CreateGroupModal.vue';
    import { isMobile } from '@/composables/viewport';

    import CameraGalleryPicker from '@/components/CameraGalleryPicker.vue';


    const groups = ref([])
    const loading = ref(false)
    const showPopup = ref(false)
    const newGroupDescription = ref("")
    const selectedFile = ref(null)
    const previewImage = ref(null)
    const router = useRouter()
    const { favoriteGroupId } = useFavorite()
    const toggleFavorite = (id) => {
    favoriteGroupId.value = favoriteGroupId.value === id ? null : id;
}
    

    watch(favoriteGroupId, async (newId, oldId) => {
    if (newId === oldId) return;
    console.log("Neuer Favorit ausgewählt:", newId);
    // Hier API call, falls wir den Favoriten in der Datenbank speichern wollen
    try {
        if (newId) {
            // Wir nutzen POST auf unseren eigenen Endpoint, da hier komplexe 
            // Datenbank-Operationen (altes False, neues True) passieren.
            await api.post(`groups/${newId}/favorite/`);
        } else {
            // Fallback, wenn der User "Keine ausgewählt" klickt
            await api.post(`groups/remove_favorite/`);
        }
    } catch(err) {
        console.error('Fehler beim Speichern des Favoriten:', err);
        // Rollback: Wenn das Backend einen Fehler wirft,
        // springt das Dropdown automatisch wieder auf den alten Wert zurück
        favoriteGroupId.value = oldId;
    }
    });

    const fetchGroups = async () => {
        try {
            loading.value = true;
            const response = await api.get('groups/');
            groups.value = response.data;

            const favoriteGroup = groups.value.find(g => g.is_favorite === true);
            favoriteGroupId.value = favoriteGroup ? favoriteGroup.id : null;

        } catch(err) {
            console.error('Fehler: ', err)
        } finally {
            loading.value = false;
        }
    }

    const onGroupPhotoAdded = (photos) => {
        const photo = photos[0];
        if (!photo) return;
        selectedFile.value = photo.file;
        previewImage.value = photo.previewUrl;
    }

    const createNewGroup = async () => {
        if (!newGroupName.value.trim()) return;
        try {
            const formData = new FormData();
            formData.append('name', newGroupName.value);
            if (newGroupDescription.value) formData.append('description', newGroupDescription.value);
            if (selectedFile.value) formData.append('profilbild', selectedFile.value);

            const response = await api.post('groups/', formData);

            const newGroup = response.data;
            groups.value.push(newGroup);
            showPopup.value = false;
            newGroupName.value = ""
            newGroupDescription.value = ""
            selectedFile.value = null
            previewImage.value = null
        } catch(error) {
            console.error("Fehler beim Erstellen der Gruppe:", error.response?.data || error.message);
        }
    }
    const handleGroupCreated = (newGroup) => {
        groups.value.push(newGroup);
        showPopup.value = false;
    }

    onMounted(() => {
        fetchGroups()
    })
</script>

<template>
    <div class="page-container">
        <Teleport v-if="isMobile" to="#app-header-actions">
            <HeaderButton @click="showPopup = true ">+ Neue Gruppe</HeaderButton>
        </Teleport>
        <PageHeader v-else>
            <HeaderButton @click="showPopup = true ">+ Neue Gruppe</HeaderButton>
        </PageHeader>

        <button class="mobile-fab-btn" @click="showPopup = true">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                <path d="M440-440H200v-80h240v-240h80v240h240v80H520v240h-80v-240Z"/>
            </svg>
        </button>

        <main class="page-content">
            <!--
            
            <div class="favorite-selector">
                <span class="selector-label">Favorit:</span>
                <select v-model="favoriteGroupId" class="clean-select">
                    <option :value="null">Keine ausgewählt</option>
                    <option v-for="group in groups" :key="group.id" :value="group.id">
                        {{ group.name }}
                    </option>
                </select>
            </div>
            -->
            

            <div id="group-grid">
                <div v-for="group in groups" :key="group.id" class="group-card"
                @click="router.push({ name: 'group-detail', params: { id: group.id } })">
                <div 
                    class="star-btn" 
                    :class="{ 'is-favorite': favoriteGroupId === group.id }" 
                    @click.stop="toggleFavorite(group.id)"
                    title="Als Favorit markieren"
                >
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px">
                        <path d="m233-120 65-281L80-590l288-25 112-265 112 265 288 25-218 189 65 281-247-149-247 149Z"/>
                    </svg>
                </div>
                    
                    <div class="card-main-content">
                        <img v-if="group.profilbild" :src="group.profilbild" alt="Gruppenbild" class="group-icon-box group-icon-img">
                        <div v-else class="group-icon-box">
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
                <textarea v-model="newGroupDescription" placeholder="Beschreibung (optional)" rows="3"></textarea>

                <img v-if="previewImage" :src="previewImage" alt="Gruppenbild" class="group-photo-preview">
                <CameraGalleryPicker :multiple="false" :has-photos="!!previewImage" @photos-added="onGroupPhotoAdded" />

                <div id="popup-actions">
                    <button @click="showPopup = false" id="cancle-btn">Abbrechen</button>
                    <button @click="createNewGroup" id="create-btn">Erstellen</button>
                </div>
            </div>
        </div>
        <CreateGroupModal
            v-if="showPopup"
            @close="showPopup = false"
            @created="handleGroupCreated"
        />
    </div>
</template>

<style scoped>
    .page-container {
        min-height: 100vh;
        padding-top: calc(var(--safe-top, 0px) + var(--app-header-height));
        padding-bottom: calc(var(--safe-bottom, 0px) + var(--tab-bar-height));
        background-color: var(--color-bg-page);
        display: flex;
        flex-direction: column;
        box-sizing: border-box;
    }

    /* Ab Desktop-Breite übernimmt PageHeader (sticky, eigener margin-top) den
       Versatz unter der DesktopNavBar - sonst würde der Abstand doppelt zählen. */
    @media (min-width: 768px) {
        .page-container {
            padding-top: 0;
        }
    }

    /* --- MOBILE BUTTON (FLOATING ACTION BUTTON) ---
       Gleicher Look wie die schwebenden Buttons auf der Karte (weißes Quadrat
       mit abgerundeten Ecken, Icon in Primärfarbe, wie .btn_ebenen_preview) */
    .mobile-fab-btn {
        position: fixed;
        bottom: calc(var(--safe-bottom, 0px) + var(--tab-bar-height) + 1.5rem);
        right: 1.5rem;
        z-index: 90;
        background-color: var(--color-bg-card);
        color: var(--color-primary);
        border: none;
        cursor: pointer;

        width: 50px;
        height: 50px;
        border-radius: 20px;
        padding: 0;

        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3);
        transition: all 0.2s ease;
    }

    .mobile-fab-btn:active {
        transform: scale(0.95);
    }

    /* Das SVG-Icon innerhalb des mobilen Kreises formatieren */
    .mobile-fab-btn svg {
        width: 1.5rem;
        height: 1.5rem;
    }

    .page-content {
        flex: 1;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: flex-start; /* Bereinigt: Jetzt wirklich oben ausgerichtet */
        padding: 2rem;               /* Bereinigt: Nur noch ein Padding-Wert */
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
        box-shadow: 0 0.6rem 1.8rem rgba(var(--color-primary-rgb), 0.08);
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
        background-color: var(--color-primary-soft);
        border-radius: var(--radius-md);
        flex-shrink: 0;
    }
    .group-icon-img {
        object-fit: cover;
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
        fill: var(--color-text-muted);
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
    #popup-content input[type="text"],
    #popup-content textarea {
        width: 100%;
        padding: 0.85rem 1rem;
        font-size: 1rem;
        font-family: inherit;
        border: 1px solid var(--color-border);
        border-radius: var(--radius-md);
        outline: none;
        color: var(--color-text);
        transition: all 0.2s ease;
        box-sizing: border-box;
        background-color: var(--color-bg-page);
        resize: vertical;
    }
    .group-photo-preview {
        width: 5rem;
        height: 5rem;
        border-radius: var(--radius-md);
        object-fit: cover;
        align-self: center;
    }
    #popup-content input[type="text"]:focus,
    #popup-content textarea:focus {
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
        /* Schwebenden Mobile-Button auf Desktop unsichtbar machen */
        .mobile-fab-btn {
            display: none;
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
    }

    .favorite-selector {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        margin-bottom: 1.5rem; 
        /* width: 100% und max-width hier ENTSORGEN */
        align-self: flex-start; /* Linksbündig zum Grid ausrichten */
        max-width: 58rem;       /* Nur für die Begrenzung */
        width: 100%;
    }

.selector-label {
    font-size: 0.9rem;
    color: var(--color-text-muted);
    font-weight: 500;
}
.clean-select {
    appearance: none;
    background-color: var(--color-bg-input);
    border: 1px solid var(--color-border);
    border-radius: 0.4rem;
    padding: 0.5rem 2rem 0.5rem 0.8rem;
    font-size: 0.9rem;
    color: var(--color-text);
    font-weight: 500;
    cursor: pointer;
    outline: none;
    transition: all 0.2s ease;
    background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="%2364748b"><path d="M7 10l5 5 5-5z"/></svg>');
    background-repeat: no-repeat;
    background-position: right 0.4rem center;
    background-size: 1.2rem;
}
.clean-select:focus,
.clean-select:hover {
    border-color: var(--color-primary);
}
.group-card {
    /* ... deine bisherigen Styles ... */
    position: relative; /* WICHTIG für die absolute Positionierung des Sterns */
}

/* Der Stern wird rechts oben in die Ecke gepinnt */
.star-btn {
    position: absolute;
    top: 0.1rem;
    right: 0.9rem;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 2.2rem;
    height: 2.2rem;
    border-radius: 50%;
    transition: background-color 0.2s ease;
    z-index: 2; /* Stellt sicher, dass er über allem liegt */
}

.star-btn:hover {
    background-color: var(--color-bg-hover);
}

.star-btn svg {
    fill: var(--color-border);
    transition: fill 0.2s ease, transform 0.2s ease;
}

.star-btn.is-favorite svg {
    fill: var(--color-warning);
    transform: scale(1.15);
}
</style>