<script setup>
    import { ref, onMounted } from 'vue';
    import { useRouter } from 'vue-router';
    import { useUserStore } from '@/store/userStore';
    import api from '@/api/api';
    import CameraGalleryPicker from '@/components/CameraGalleryPicker.vue';
    import PageHeader from '@/components/PageHeader.vue';
    import { isMobile } from '@/composables/viewport';

    const userStore = useUserStore();
    const router = useRouter();

    const saving = ref(false);
    const saved = ref(false);

    const profile = ref({
        firstname: '',
        lastname: '',
        mail: '',
        profilbild: null
    })
    const newPassword = ref('')
    const confirmPassword = ref('')
    const loading = ref(false)
    const selectedFile = ref(null)
    const previewImage = ref(null)

    const onProfilePhotoAdded = (photos) => {
        const photo = photos[0];
        if (!photo) return;
        selectedFile.value = photo.file;
        previewImage.value = photo.previewUrl;
    }

    const fetchProfile = async () => {
        try {
            loading.value = true
            const response = await api.get('profil/')
            profile.value = response.data
        } catch(err) {
            console.error('Fehler: ', err)
        } finally {
            loading.value = false
        }
    }

    const updateProfile = async () => {
        if(newPassword.value || confirmPassword.value) {
            if(newPassword.value !== confirmPassword.value) {
                alert("Die Passwörter stimmen nicht überein")
                return
            }
        
            const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[a-z])[A-Za-z\d@$!%*?&]{8,20}$/
            if(!passwordRegex.test(newPassword.value)){
                alert("Das Passwort erfüllt die Anforderungen nicht!\n\n" +
                    "- Mindestens 8 Zeichen lang\n" +
                    "- Mindestens ein Großbuchstabe\n" +
                    "- Mindestens eine Zahl\n" +
                    "- Mindestens ein Kleinbuchstabe");
                return;
            }
        }
        try {
            saving.value = true;
            saved.value = false;
            const formData = new FormData()

            if (profile.value.firstname !== undefined) formData.append('user.first_name', profile.value.firstname)
            if (profile.value.lastname !== undefined) formData.append('user.last_name', profile.value.lastname)
            if (profile.value.mail !== undefined) formData.append('user.email', profile.value.mail)

            if(newPassword.value){
                formData.append('password', newPassword.value)
            }
            if(selectedFile.value){
                formData.append('profilbild', selectedFile.value)
            }
            
            const response = await api.patch('profil/', formData)

            profile.value = response.data
            await userStore.fetchProfile();

            newPassword.value = ""
            confirmPassword.value = ""
            selectedFile.value = null
            saved.value = true;
            setTimeout(() => saved.value = false, 2500);
        } catch(err){
            console.error('Fehler beim Speichern: ', err.response?.data || err)
            alert("Fehler beim Speichern. Bitte überprüfe deine Eingaben.");
        } finally {
            saving.value = false;
        }
    }

    onMounted(() => {
        fetchProfile();
    })
</script>

<template>
    <Teleport v-if="isMobile" to="#app-header-actions">
        <button type="button" class="settings-btn" @click="router.push('/settings')" aria-label="Einstellungen öffnen">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
        </button>
    </Teleport>
    <PageHeader v-else>
        <button type="button" class="settings-btn" @click="router.push('/settings')" aria-label="Einstellungen öffnen">
            <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
            </svg>
        </button>
    </PageHeader>

    <div id="outer-box">
        <form id="formular" @submit.prevent="updateProfile">
            <div id="profile-selector" class="input-group">
                <div class="profile-row">
                    <div id="profile-picture">
                        <img :src="previewImage || profile.profilbild || '/profile_pic.jpg'" id="picture" alt="Profilbild">
                    </div>
                    <div id="profile-text">
                        <h3>Profilbild</h3>
                        <p>Wähle ein neues Profilbild aus</p>
                    </div>
                </div>

                <CameraGalleryPicker
                    :multiple="false"
                    :has-photos="!!previewImage"
                    @photos-added="onProfilePhotoAdded"
                />
            </div>
            
            <div id="personal-info" class="input-group">
                <h3 class="icon-heading">
                    <svg xmlns="http://www.w3.org/2000/svg" 
                        height="24px" 
                        viewBox="0 -960 960 960" 
                        width="24px" 
                        fill="currentColor">
                        <path d="M367-527q-47-47-47-113t47-113q47-47 113-47t113 47q47 47 47 113t-47 113q-47 47-113 47t-113-47ZM160-160v-112q0-34 17.5-62.5T224-378q62-31 126-46.5T480-440q66 0 130 15.5T736-378q29 15 46.5 43.5T800-272v112H160Zm80-80h480v-32q0-11-5.5-20T700-306q-54-27-109-40.5T480-360q-56 0-111 13.5T260-306q-9 5-14.5 14t-5.5 20v32Zm296.5-343.5Q560-607 560-640t-23.5-56.5Q513-720 480-720t-56.5 23.5Q400-673 400-640t23.5 56.5Q447-560 480-560t56.5-23.5ZM480-640Zm0 400Z"/>
                    </svg>
                    Persönliche Informationen
                </h3>
                <div id="names">
                    <div class="name-field">
                        <label for="vorname">Vorname</label>
                        <input type="text" placeholder="Vorname" id="vorname" v-model="profile.firstname">
                    </div>
                    <div class="name-field">
                        <label for="nachname">Nachname</label>
                        <input type="text" placeholder="Nachname" id="nachname" v-model="profile.lastname">
                    </div>
                </div>
                <div class="email-field">
                    <label for="mail">
                        <svg xmlns="http://www.w3.org/2000/svg" 
                            height="24px" 
                            viewBox="0 -960 960 960" 
                            width="24px" 
                            fill="currentColor">
                            <path d="M160-160q-33 0-56.5-23.5T80-240v-480q0-33 23.5-56.5T160-800h640q33 0 56.5 23.5T880-720v480q0 33-23.5 56.5T800-160H160Zm320-280L160-640v400h640v-400L480-440Zm0-80 320-200H160l320 200ZM160-640v-80 480-400Z"/>
                        </svg>
                        Email
                    </label>
                    <input type="email" placeholder="julius@mail.de" id="mail" v-model="profile.mail">
                </div>
            </div>
            
            <div id="password" class="input-group">
                <h3 class="icon-heading">
                    <svg xmlns="http://www.w3.org/2000/svg" 
                        height="24px" 
                        viewBox="0 -960 960 960" 
                        width="24px" 
                        fill="currentColor">
                        <path d="M240-80q-33 0-56.5-23.5T160-160v-400q0-33 23.5-56.5T240-640h40v-80q0-83 58.5-141.5T480-920q83 0 141.5 58.5T680-720v80h40q33 0 56.5 23.5T800-560v400q0 33-23.5 56.5T720-80H240Zm0-80h480v-400H240v400Zm296.5-143.5Q560-327 560-360t-23.5-56.5Q513-440 480-440t-56.5 23.5Q400-393 400-360t23.5 56.5Q447-280 480-280t56.5-23.5ZM360-640h240v-80q0-50-35-85t-85-35q-50 0-85 35t-35 85v80ZM240-160v-400 400Z"/>
                    </svg>
                    Passwort ändern
                </h3>
                <div id="password-change">
                    <div class="name-field">
                        <label>Neues Passwort</label>
                        <input type="password" v-model="newPassword">
                    </div>
                    <div class="name-field">
                        <label>Passwort bestätigen</label>
                        <input type="password" v-model="confirmPassword">
                    </div>
                </div>
            </div>
            <button type="submit" id="save" :disabled="saving">
                <template v-if="saving">
                    <svg class="spinner" xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="12" r="10" stroke="white" stroke-width="2" stroke-dasharray="40" stroke-dashoffset="10"/>
                    </svg>
                    Wird gespeichert...
                </template>
                <template v-else-if="saved">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                        <path d="M382-240 154-468l57-57 171 171 367-367 57 57-424 424Z"/>
                    </svg>
                    Gespeichert!
                </template>
                <template v-else>
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                        <path d="M840-680v480q0 33-23.5 56.5T760-120H200q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h480l160 160Zm-80 34L646-760H200v560h560v-446ZM565-275q35-35 35-85t-35-85q-35-35-85-35t-85 35q-35 35-35 85t35 85q35 35 85 35t85-35ZM240-560h360v-160H240v160Zm-40-86v446-560 114Z"/>
                    </svg>
                    Änderungen speichern
                </template>
            </button>
        </form>
    </div>
</template>

<style scoped>
    .settings-btn {
        width: 40px;
        height: 40px;
        padding: 0;
        border: none;
        background: none;
        color: var(--color-text-muted);
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        border-radius: var(--radius-md);
    }
    .settings-btn:hover {
        background-color: var(--color-bg-page, #f0f2f5);
        color: var(--color-primary);
    }
    .settings-btn svg {
        width: 22px;
        height: 22px;
    }

    #outer-box {
        /* Platz nach oben für den fixierten AppHeader, nach unten für die TabBar */
        padding: calc(var(--safe-top) + var(--app-header-height) + 1.5rem) 1rem
                 calc(var(--safe-bottom) + var(--tab-bar-height) + 1rem) 1rem;
        min-height: 100vh;
        width: 100%;
        background-color: var(--color-bg-page);
        box-sizing: border-box;
    }

    #formular {
        width: 100%;
        max-width: 600px;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
        margin: 0 auto;
        padding-bottom: 8rem;
    }

    img {
        border-radius: 50%;
        border: 0.25rem solid var(--color-primary);
        /* Etwas kompakter auf dem Handy, damit es neben dem Text gut Platz hat */
        width: 5.5rem;
        height: 5.5rem;
        object-fit: cover;
    }

    .input-group {
        background-color: var(--color-bg-card);
        padding: 1.25rem;
        border-radius: var(--radius-lg);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }

    #profile-selector {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    /* JETZT NEBENEEINANDER AUF DEM HANDY */
    .profile-row {
        display: flex;
        flex-direction: row;
        align-items: center;
        text-align: left;
        gap: 1.2rem;
    }

    #profile-text {
        flex: 1; /* Nimmt den restlichen verfügbaren Platz ein */
    }

    #profile-text h3 {
        color: var(--color-text);
        margin: 0 0 0.25rem 0;
        font-size: 1.1rem;
    }

    #profile-text p {
        color: var(--color-text-muted);
        font-size: 0.85rem;
        margin: 0;
        line-height: 1.3;
    }

    #profile-picture {
        position: relative;
        flex-shrink: 0; /* Verhindert, dass das Bild auf kleinen Bildschirmen gestaucht wird */
    }

    #personal-info {
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }

    .icon-heading {
        color: var(--color-primary);
        margin: 0 0 0.5rem 0;
        font-size: 1.2rem;
    }

    #names, #password-change {
        display: flex;
        flex-direction: column;
        gap: 1rem;
        width: 100%;
    }

    .name-field, .email-field {
        display: flex;
        gap: 0.4rem;
        flex-direction: column;
        width: 100%;
    }

    label {
        font-weight: 500;
        font-size: 0.9rem;
        color: var(--color-text);
    }

    input {
        padding: 0.85rem;
        border-radius: var(--radius-md);
        border: 1px solid var(--color-border);
        box-sizing: border-box;
        width: 100%;
        font-size: 1rem;
        background-color: var(--color-bg-page);
        color: var(--color-text);
    }

    input:focus {
        outline: none;
        border-color: var(--color-primary);
        box-shadow: 0 0 0 2px rgba(var(--color-primary-rgb), 0.2);
    }

    h3, label, #save {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    #save {
        background-color: var(--color-primary);
        border: none;
        color: var(--color-on-primary);
        border-radius: var(--radius-md);
        display: flex;
        justify-content: center;
        align-items: center;
        gap: 0.5rem;
        padding: 1rem;
        font-size: 1rem;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.2s ease;
        width: 100%;
    }

    #save:hover:not(:disabled) {
        background-color: var(--color-primary-dark);
    }

    #save:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .spinner {
        animation: spin 0.8s linear infinite;
        transform-origin: center;
    }

    @keyframes spin {
        to { transform: rotate(360deg); }
    }

    /* --- Media Queries für größere Bildschirme (Tablets/Desktop) --- */
    @media (min-width: 480px) {
        #outer-box {
            /* Desktop braucht meist weniger Abstand nach oben, außer der Header zieht mit um */
            padding: calc(var(--safe-top) + var(--app-header-height) + 3rem) 1.5rem
                     calc(var(--safe-bottom) + var(--tab-bar-height) + 1.5rem) 1.5rem;
        }

        .input-group {
            padding: 2rem;
        }

        img {
            /* Auf dem Desktop darf das Bild wieder etwas größer sein */
            width: 7rem;
            height: 7rem;
        }

        #names, #password-change {
            flex-direction: row; /* Stehen auf dem Desktop nebeneinander */
        }
    }

    /* Ab Desktop-Breite übernimmt PageHeader (sticky, eigener margin-top) den
       Versatz unter der DesktopNavBar - sonst würde der Abstand doppelt zählen. */
    @media (min-width: 768px) {
        #outer-box {
            padding-top: 1.5rem;
        }
    }
</style>