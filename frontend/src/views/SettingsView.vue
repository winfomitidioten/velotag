<script setup>
import { computed } from 'vue';
import { useSettingsStore } from '@/store/settingsStore.js';
import PageHeader from '@/components/PageHeader.vue';

const settings = useSettingsStore();

const themes = [
    { value: 'system', label: 'System' },
    { value: 'light', label: 'Hell'},
    { value: 'dark', label: 'Dunkel'},
];

const activeIndex = computed(() => 
    themes.findIndex(t => t.value === settings.theme)
);

</script>

<template>
    <div class="page-container">
        <PageHeader title="Einstellungen" />
        <main class="settings-content">

            <!-- Darstellung -->
            <section class="input-grou">
                <div class="theme-switch">
                    <div
                        v-for="t in themes" :key="t.value"
                        class="theme-option"
                        :class="{ active: settings.theme === t.value }"
                        @click="settings.setTheme(t.value)"
                    >{{  t.label  }}</div>
                    <div
                        class="theme-slider"
                        :style="{ transform: `translateX(${activeIndex * 100}%)` }"
                    ></div>
                </div>
            </section>

            <!-- Konto -->
            <section class="input-group">
                <h3 class="icon-heading">Konto</h3>
                <RouterLink to="/profile" class="row-link">
                    <span>Profil bearbeiten</span>
                    <svg class="chevron" xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
                        <path d="M504-480 320-664l56-56 240 240-240 240-56-56 184-184Z"/>
                    </svg>
                </RouterLink>

                <!-- Allgemeine Benachrichigungen-->
                <label class="toggle-row">
                    <span class="toggle-label">Benachrichtigungen</span>
                    <span class="switch">
                        <input type="checkbox" v-model="settings.notificationsEnabled" />
                        <span class="track"></span>
                    </span>
                </label>

                <label class="toggle-row" :class="{ disabled: !settings.notificationsEnabled }">
                    <span class="toggle-label">Gruppeneinladungen</span>
                    <span class="switch">
                        <input
                            type="checkbox"
                            v-model="settings.groupInvitesEnabled"
                            :disabled="!settings.notificationsEnabled"
                        />
                        <span class="track"></span>
                    </span>
                </label>
            </section> 
            
            <!-- Über -->
            <section class="input-group">
                <h3 class="icon-heading">Über</h3>
                <div class="about-row"><span>Version</span><span>0.0.0.1</span></div>
                <a class="row-link" href="#">
                    <span>Datenschutz</span>
                    <svg class="chevron" xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
                        <path d="M504-480 320-664l56-56 240 240-240 240-56-56 184-184Z"/>
                    </svg>
                </a>
                <a class="row-link" href="#">
                    <span>Impressum</span>
                    <svg class="chevron" xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
                        <path d="M504-480 320-664l56-56 240 240-240 240-56-56 184-184Z"/>
                    </svg>
                </a>
                <a class="row-link" href="mailto:support@velotag.app">
                    <span>Support kontaktieren</span>
                    <svg class="chevron" xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
                        <path d="M504-480 320-664l56-56 240 240-240 240-56-56 184-184Z"/>
                    </svg>
                </a>
            </section>
        </main>
    </div>
</template>

<style scoped>
.page-container {
    min-height: 100vh;
    background-color: var(--color-bg-page);
    display: flex;
    flex-direction: column;
}

/* Inhalt zentriert, mit Abstand nach dem stickenden PageHeader */
.settings-content {
    width: 100%;
    max-width: 600px;
    margin: 0 auto;
    padding: 1.5rem 1rem 4rem;
    box-sizing: border-box;
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
}

/* Karten-Container – identisch zur ProfileView */
.input-group {
    background-color: var(--color-bg-card);
    padding: 1.25rem;
    border-radius: var(--radius-lg);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    display: flex;
    flex-direction: column;
    gap: 0;
}

.icon-heading {
    color: var(--color-primary);
    margin: 0;
    margin-bottom: 10px;
    font-size: 1.2rem;
}

/* --- Segmented Control für die Theme-Auswahl --- */
.theme-switch {
    position: relative;
    display: flex;
    align-items: center;
    background-color: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-radius: 30px;
    padding: 4px;
    height: 44px;
    user-select: none;
    cursor: pointer;
}

.theme-option {
    flex: 1;
    text-align: center;
    font-size: 0.95rem;
    font-weight: 600;
    color: var(--color-text-muted);
    z-index: 2;
    cursor: pointer;
    transition: color 0.3s ease;
}

.theme-option.active {
    color: var(--color-on-primary);
}

.theme-slider {
    position: absolute;
    top: 4px;
    left: 4px;
    width: calc((100% - 8px) / 3);
    height: calc(100% - 8px);
    background-color: var(--color-primary);
    border-radius: 25px;
    transition: transform 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 1;
}

.row-link,
.toggle-row,
.about-row {
    display: flex;
    align-items: center;          /* vertikal zentriert */
    justify-content: space-between;/* Label links, Chevron/Switch rechts */
    padding: 0.9rem 0;
    border-top: 1px solid var(--color-border);
    text-align: left;             /* Text linksbündig */
}

/* --- Zeilen-Links (Profil, Datenschutz, Impressum, Support) --- */
.row-link {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 0;
    color: var(--color-text);
    text-decoration: none;
    font-size: 1rem;
    font-weight: 500;
    border: none;
    background: none;
    width: 100%;
    text-align: left;
    cursor: pointer;
    border-top: 1px solid var(--color-border);
}

/* erste Zeile direkt nach einer Überschrift braucht keine obere Linie */
.icon-heading + .row-link,
.icon-heading + .toggle-row,
.icon-heading + .about-row {
    border-top: none;
}

/* erster Link in einer Karte braucht keine Trennlinie oben */
.row-link:first-of-type {
    border-top: none;
}

.row-link:hover {
    color: var(--color-primary);
}

/* optional, falls du später eine rote Aktion (z. B. Konto löschen) einbaust */
.row-link--danger {
    color: var(--color-danger);
}
.row-link--danger:hover {
    color: var(--color-danger-dark);
}

/* Chevron bei navigierenden Zeilen – rechtsbündig durch space-between der .row-link */
.row-link--nav, .chevron {
    width: 20px;
    height: 20px;
    flex-shrink: 0;               /* Chevron wird nie gestaucht */
    color: var(--color-text-muted);
    transition: transform 0.15s ease, color 0.15s ease;
}

/* kleine Bewegung nach rechts beim Hover – optionaler Feinschliff */
.row-link--nav:hover .chevron {
    color: var(--color-primary);
    transform: translateX(2px);
}

/* --- Info-Zeile "Version" (kein Link) --- */
.about-row {
    display: flex;
    justify-content: space-between;
    padding: 0.85rem 0;
    font-size: 1rem;
    color: var(--color-text);
    border-bottom: 1px solid var(--color-border);
}
.about-row span:last-child {
    color: var(--color-text-muted);
}
.toggle-row {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 0.85rem 0;
    border-top: 1px solid var(--color-border);
    cursor: pointer;
}
.toggle-row.disabled {
    opacity: 0.45;
    cursor: not-allowed;
}
.toggle-label {
    font-size: 1rem;
    font-weight: 500;
    color: var(--color-text);
}

/* Schalter */
.switch {
    position: relative;
    flex-shrink: 0;
    width: 46px;
    height: 26px;
}
.switch input {
    position: absolute;
    opacity: 0;        /* echte Checkbox unsichtbar, aber bedienbar/fokussierbar */
    width: 100%;
    height: 100%;
    margin: 0;
    cursor: inherit;
}
.track {
    position: absolute;
    inset: 0;
    background-color: var(--color-border);
    border-radius: 999px;
    transition: background-color 0.25s ease;
}
/* der weiße Knauf */
.track::before {
    content: '';
    position: absolute;
    top: 3px;
    left: 3px;
    width: 20px;
    height: 20px;
    background-color: var(--color-bg-card);
    border-radius: 50%;
    box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
    transition: transform 0.25s ease;
}
/* an: Track grün, Knauf nach rechts */
.switch input:checked + .track {
    background-color: var(--color-primary);
}
.switch input:checked + .track::before {
    transform: translateX(20px);
}

/* --- Größere Bildschirme --- */
@media (min-width: 480px) {
    .input-group {
        padding: 2rem;
    }
    .settings-content {
        padding: 2rem 1.5rem 4rem;
    }
}
</style>