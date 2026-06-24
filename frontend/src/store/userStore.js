import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import api from '@/api/api';

export const useUserStore = defineStore('user', () => {
    const firstname = ref('');
    const lastname = ref('');
    const mail = ref('');
    const profileImage = ref('');

    const initials = computed(() => `${firstname.value[0] ?? ''}${lastname.value[0] ?? ''}`.toUpperCase());

    async function fetchProfile() {
        const response = await api.get('profil/');
        firstname.value = response.data.firstname;
        lastname.value = response.data.lastname;
        mail.value = response.data.mail;
        const pic = response.data.profilbild;
        profileImage.value = pic ?? '';
    };

    function clearUser() {
        firstname.value = '';
        lastname.value = '';
        mail.value = '';
        profileImage.value = '';
    }

    return { firstname, lastname, mail, initials, profileImage, fetchProfile, clearUser };
});
