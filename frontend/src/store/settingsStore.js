import { defineStore } from 'pinia';
import { ref, watch, nextTick } from 'vue';
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
    // Anzeige-Cache, die eigentliche Quelle ist immer der Server.
    let applyingServerValue = false;
    watch(groupInvitesEnabled, async (v) => {
        localStorage.setItem(INVITE_KEY, JSON.stringify(v));
        if (applyingServerValue) return;
        try {
            await api.patch('profil/', { group_invites_enabled: v });
        } catch (err) {
            console.error('Fehler beim Speichern der Gruppeneinladungen-Einstellung:', err);
        }
    });

    async function loadGroupInvitesSetting() {
        try {
            const response = await api.get('profil/');
            applyingServerValue = true;
            groupInvitesEnabled.value = response.data.group_invites_enabled;
            await nextTick(); // Watcher (oben) muss zuerst laufen, bevor das Flag zurückgesetzt wird -
                               // sonst würde der frisch geladene Wert gleich wieder ans Backend zurückgepatcht.
        } catch (err) {
            console.error('Fehler beim Laden der Gruppeneinladungen-Einstellung:', err);
        } finally {
            applyingServerValue = false;
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

    return { theme, setTheme, notificationsEnabled, groupInvitesEnabled, loadGroupInvitesSetting };
});


