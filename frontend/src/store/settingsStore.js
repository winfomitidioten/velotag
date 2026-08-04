import { defineStore } from 'pinia';
import { ref, watch } from 'vue';

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
    watch(groupInvitesEnabled, (v) => localStorage.setItem(INVITE_KEY, JSON.stringify(v)));

    applyTheme(theme.value);

    watch(theme, (value) => {
        localStorage.setItem(THEME_STORAGE_KEY, value);
        applyTheme(value);
    });

    function setTheme(value) {
        if (VALID_THEMES.includes(value)) theme.value = value;
    }

    return { theme, setTheme, notificationsEnabled, groupInvitesEnabled };
});


