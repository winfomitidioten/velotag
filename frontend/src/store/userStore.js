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
        onboardingCompleted.value = response.data.onboarding_completed ?? false;
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
    }

    return {
        id, firstname, lastname, mail, initials, profileImage,
        latitude, longitude, locationName, onboardingCompleted,
        fetchProfile, clearUser
    };
});
