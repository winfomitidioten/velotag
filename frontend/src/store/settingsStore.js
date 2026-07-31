import { defineStore } from 'pinia';
import { ref, watch } from 'vue';
import api from '@/api/api';

const THEME_STORAGE_KEY = 'velotag_theme';
const VALID_THEMES = ['system', 'light', 'dark'];

/**
 * applyTheme wendet das gewählte Theme auf <html> an
 * bei 'system' wird kein Theme gesetzt, sodass die @media {prefers-color-scheme}-Regel in main.css greift
 */

function applyTheme(theme) {
    const root = document.documentElement;
    if (theme === 'system') { 
        root.removeAttribute('data-theme');
    } else {
        root.setAttribute('data-theme', theme);
    }
}

export const useSettingsStore = defineStore('settings', () => {
    const stored = localStorage.getItem(THEME_STORAGE_KEY);
    const theme = ref(VALID_THEMES.includes(stored) ? stored : 'system');
    const NOTIFY_KEY = 'velotag_notifications';
    const INVITE_KEY = 'velotag_group_invites';

    const notificationsEnabled = ref(JSON.parse(localStorage.getItem(NOTIFY_KEY) ?? 'true'));
    const groupInvitesEnabled = ref(JSON.parse(localStorage.getItem(INVITE_KEY) ?? 'true'));

    watch(notificationsEnabled, (v) => localStorage.setItem(NOTIFY_KEY, JSON.stringify(v)));

    // Ob niemand mehr diesen Nutzer in eine Gruppe einladen darf, wird serverseitig
    // durchgesetzt (GroupInviteAdmin) - localStorage ist hier nur ein schneller
    // Anzeige-Cache, die eigentliche Quelle ist immer der Server. Bewusst kein watch()
    // fuer den Server-Sync (Klick -> setGroupInvitesEnabled() ruft die API direkt und
    // unmittelbar auf, statt indirekt ueber einen Watcher zu laufen).
    async function setGroupInvitesEnabled(value) {
        groupInvitesEnabled.value = value;
        localStorage.setItem(INVITE_KEY, JSON.stringify(value));
        try {
            await api.patch('profil/', { group_invites_enabled: value });
        } catch (err) {
            console.error('Fehler beim Speichern der Gruppeneinladungen-Einstellung:', err);
        }
    }

    async function loadGroupInvitesSetting() {
        try {
            const response = await api.get('profil/');
            groupInvitesEnabled.value = response.data.group_invites_enabled;
            localStorage.setItem(INVITE_KEY, JSON.stringify(groupInvitesEnabled.value));
        } catch (err) {
            console.error('Fehler beim Laden der Gruppeneinladungen-Einstellung:', err);
        }
    }

    applyTheme(theme.value);

    watch(theme, (value) => {
        localStorage.setItem(THEME_STORAGE_KEY, value);
        applyTheme(value);
    });

    function setTheme(value) {
        if (VALID_THEMES.includes(value)) theme.value = value;
    }

    return { theme, setTheme, notificationsEnabled, groupInvitesEnabled, loadGroupInvitesSetting, setGroupInvitesEnabled };
});


