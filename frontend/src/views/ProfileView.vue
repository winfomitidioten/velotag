<script setup>
    import { ref, computed, onMounted } from 'vue';
    import { useUserStore } from '@/store/userStore';
    import { Geolocation } from '@capacitor/geolocation';
    import api from '@/api/api';
    import CameraGalleryPicker from '@/components/CameraGalleryPicker.vue';

    const userStore = useUserStore();

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

    // --- Standort ---
    const latitude = ref(null);
    const longitude = ref(null);
    const locationName = ref('');
    const manualQuery = ref('');
    const locationLoading = ref(false);
    const locationError = ref('');
    const sensorHint = ref('');

    const detectLocation = async () => {
        locationError.value = '';
        sensorHint.value = '';
        locationLoading.value = true;
        try {
            const position = await Geolocation.getCurrentPosition();
            latitude.value = position.coords.latitude;
            longitude.value = position.coords.longitude;
            try {
                const response = await api.get('geocode/reverse/', {
                    params: { lat: latitude.value, lon: longitude.value }
                });
                locationName.value = response.data.display_name || '';
                // Freitextfeld mitbefüllen, damit der User nicht denkt, er müsse
                // den Ort zusätzlich manuell eingeben
                manualQuery.value = locationName.value;
            } catch {
                // Reverse-Geocoding ist rein kosmetisch, Fehler hier blockieren nicht
            }
        } catch {
            sensorHint.value = 'Standort konnte nicht ermittelt werden. Bitte gib deinen Ort manuell ein.';
        } finally {
            locationLoading.value = false;
        }
    };

    const searchLocation = async () => {
        if (!manualQuery.value.trim()) return;
        locationError.value = '';
        locationLoading.value = true;
        try {
            const response = await api.get('geocode/', { params: { query: manualQuery.value } });
            latitude.value = response.data.latitude;
            longitude.value = response.data.longitude;
            locationName.value = response.data.display_name;
        } catch {
            locationError.value = 'Ort nicht gefunden, bitte anders formulieren.';
        } finally {
            locationLoading.value = false;
        }
    };

    const fetchProfile = async () => {
        try {
            loading.value = true
            const response = await api.get('profil/')
            profile.value = response.data
            latitude.value = response.data.latitude ?? null;
            longitude.value = response.data.longitude ?? null;
            locationName.value = response.data.location_name ?? '';
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
            if (latitude.value !== null && longitude.value !== null) {
                formData.append('latitude', latitude.value);
                formData.append('longitude', longitude.value);
            }
            if (locationName.value) formData.append('location_name', locationName.value);

            const response = await api.patch('profil/', formData)

            profile.value = response.data
            latitude.value = response.data.latitude ?? null;
            longitude.value = response.data.longitude ?? null;
            locationName.value = response.data.location_name ?? '';
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

            <div id="location" class="input-group">
                <h3 class="icon-heading">
                    <svg xmlns="http://www.w3.org/2000/svg"
                        height="24px"
                        viewBox="0 -960 960 960"
                        width="24px"
                        fill="currentColor">
                        <path d="M480-480q33 0 56.5-23.5T560-560q0-33-23.5-56.5T480-640q-33 0-56.5 23.5T400-560q0 33 23.5 56.5T480-480Zm0 400Q319-217 239.5-334.5T160-552q0-150 96.5-239T480-880q127 0 223.5 89T800-552q0 100-79.5 217.5T480-80Z"/>
                    </svg>
                    Standort
                </h3>

                <button type="button" class="btn-location" :disabled="locationLoading" @click="detectLocation">
                    <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 -960 960 960" width="18px" fill="currentColor">
                        <path d="M480-480q33 0 56.5-23.5T560-560q0-33-23.5-56.5T480-640q-33 0-56.5 23.5T400-560q0 33 23.5 56.5T480-480Zm0 400Q319-217 239.5-334.5T160-552q0-150 96.5-239T480-880q127 0 223.5 89T800-552q0 100-79.5 217.5T480-80Z"/>
                    </svg>
                    <span>{{ locationLoading ? 'Ermittle Standort...' : 'Standort automatisch ermitteln' }}</span>
                </button>
                <p v-if="sensorHint" class="location-hint">{{ sensorHint }}</p>

                <div class="name-field location-search">
                    <label>Ort manuell eingeben</label>
                    <div class="location-search-row">
                        <input
                            type="text"
                            v-model="manualQuery"
                            placeholder="z.B. Wiesbaden"
                            @keyup.enter="searchLocation"
                        >
                        <button type="button" class="btn-location-search" :disabled="locationLoading" @click="searchLocation">Suchen</button>
                    </div>
                    <p v-if="locationError" class="location-error">{{ locationError }}</p>
                </div>

                <p v-if="locationName" class="location-confirmed">Aktueller Standort: {{ locationName }}</p>
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
    #outer-box {
        /* Genug Platz nach oben, damit der fixierte AppHeader und der darunter
           liegende Zurück-Pfeil (bei calc(var(--safe-top) + var(--app-header-height) + 0.5rem),
           Höhe 44px) nicht über dem Profilbild liegen */
        padding: calc(var(--safe-top) + var(--app-header-height) + 5rem) 1rem 1rem 1rem;
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
        padding-bottom: 4rem;
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

    #location {
        display: flex;
        flex-direction: column;
        gap: 0.75rem;
    }

    .btn-location {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 8px;
        width: 100%;
        padding: 0.85rem;
        background: var(--color-bg-page);
        color: var(--color-primary);
        border: 1.5px solid var(--color-primary);
        border-radius: var(--radius-md);
        font-size: 0.95rem;
        font-weight: 600;
        cursor: pointer;
        transition: background 0.2s;
    }
    .btn-location:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }

    .location-search-row {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .location-search-row input {
        flex: 1;
    }

    .btn-location-search {
        flex-shrink: 0;
        padding: 0.85rem 1rem;
        background: none;
        border: 1px solid var(--color-border);
        border-radius: var(--radius-md);
        color: var(--color-primary);
        font-weight: 600;
        font-size: 0.9rem;
        cursor: pointer;
    }
    .btn-location-search:disabled {
        opacity: 0.5;
        cursor: not-allowed;
    }

    .location-hint {
        font-size: 0.85rem;
        color: var(--color-text-muted);
        text-align: center;
        margin: 0;
    }
    .location-error {
        font-size: 0.85rem;
        color: var(--color-danger);
        margin: 0.4rem 0 0;
    }
    .location-confirmed {
        font-size: 0.9rem;
        color: var(--color-primary);
        margin: 0;
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
            padding: calc(var(--safe-top) + var(--app-header-height) + 3rem) 1.5rem;
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
</style>