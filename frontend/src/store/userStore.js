import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/api/api';

export const useUserStore = defineStore('user', () => {
    const firstname = ref('');
    const lastname = ref('');
    const mail = ref('');
    const profileImage = ref('');
    const id = ref(null);
    const latitude = ref(null);
    const longitude = ref(null);
    const locationName = ref('');
    const onboardingCompleted = ref(null); // null = noch nicht geladen (siehe Router-Guard)

    // Wird bei jedem Logout hochgezählt und in App.vue als :key der Routen-Komponente
    // benutzt. Ohne das überlebt die <keep-alive>-Instanz der Karte den Account-Wechsel
    // und zeigt Routen, Fahrtenzahl und Kilometer des vorherigen Nutzers weiter.
    // Ein Zähler statt der User-ID: die ID ist nach dem Login erst nach fetchProfile()
    // gesetzt, die Karte würde sonst zweimal mounten und Leaflet sichtbar neu aufbauen.
    const sessionKey = ref(0);

    const initials = computed(() => `${firstname.value[0] ?? ''}${lastname.value[0] ?? ''}`.toUpperCase());

    async function fetchProfile() {
        const response = await api.get('profil/');
        id.value = response.data.id;
        firstname.value = response.data.firstname;
        lastname.value = response.data.lastname;
        mail.value = response.data.mail;
        const pic = response.data.profilbild;
        profileImage.value = pic ?? '';
        latitude.value = response.data.latitude ?? null;
        longitude.value = response.data.longitude ?? null;
        locationName.value = response.data.location_name ?? '';
        // Nach dem Laden nie mehr null: null ist exklusiv der "noch nicht geladen"-Zustand
        // für den Router-Guard (siehe oben) - ein fehlender Serverwert zählt hier als false.
        onboardingCompleted.value = response.data.onboarding_completed ?? false;
    };

    // Beim harten Neuladen (F5) sind mehrere Komponenten (App.vue, Karte.vue, ...) gleichzeitig
    // auf ein geladenes Profil angewiesen - ensureProfile teilt sich einen einzigen laufenden
    // Request statt jede Komponente einzeln fetchProfile() aufrufen zu lassen
    let pendingFetch = null;
    function ensureProfile() {
        if (onboardingCompleted.value !== null) return Promise.resolve();
        if (!pendingFetch) {
            pendingFetch = fetchProfile().finally(() => { pendingFetch = null; });
        }
        return pendingFetch;
    };

    function clearUser() {
        id.value = null;
        firstname.value = '';
        lastname.value = '';
        mail.value = '';
        profileImage.value = '';
        latitude.value = null;
        longitude.value = null;
        locationName.value = '';
        onboardingCompleted.value = null;
        sessionKey.value++;
    }

    return {
        id, firstname, lastname, mail, initials, profileImage,
        latitude, longitude, locationName, onboardingCompleted, sessionKey,
        fetchProfile, ensureProfile, clearUser
    };
});
