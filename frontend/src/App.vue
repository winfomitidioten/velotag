<script setup>
import { RouterView, useRoute, useRouter } from 'vue-router'
import { onMounted } from 'vue'
import apiClient from '@/api/client'

import AppHeader from '@/components/AppHeader.vue'
import AppToast from '@/components/AppToast.vue'
import StravaActivityPicker from '@/components/StravaActivityPicker.vue'

import { useUserStore } from '@/store/userStore'
import { useSettingsStore } from './store/settingsStore'

import { useStravaImport } from '@/composables/useStravaImport'

import { Capacitor } from '@capacitor/core'
import { App as CapacitorApp } from '@capacitor/app'
import { StatusBar, Style } from '@capacitor/status-bar'

useSettingsStore(); // legt den Store an, der Konstruktor wendet gespeichertes Theme sofort an

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const { showStravaImport } = useStravaImport();

const goBack = () => {
  router.push(route.meta.backTo ?? '/map');
};

const setAppHeight = () => {
  document.documentElement.style.setProperty('--app-height', `${window.innerHeight}px`);
};

onMounted(async () => {
  if (Capacitor.isNativePlatform()) {
    apiClient.defaults.baseURL = 'http://167.233.33.166/api';
    await StatusBar.setOverlaysWebView({ overlay: true });
    // Style.Light => dunkle Uhr/Batterie-Icons, richtig für unseren hellen Hintergrund
    // (Style.Dark ist entgegen des Namens für dunkle Hintergründe mit hellen Icons gedacht)
    await StatusBar.setStyle({ style: Style.Light });

    // Fängt den velotag://strava-callback Deep Link ab, mit dem das Backend
    // nach dem Strava-Login zurück in die App springt
    CapacitorApp.addListener('appUrlOpen', ({ url }) => {
      if (url.startsWith('velotag://strava-callback')) {
        router.push('/map');
        showStravaImport.value = true;
      }
    });
  }

  setAppHeight();
  window.addEventListener('resize', setAppHeight);
  // forceViewportRecalc();
  const token = localStorage.getItem('auth_token');
  if (token && token !== 'undefined') {
    try {
      await userStore.fetchProfile();
    } catch {
      localStorage.removeItem('auth_token');
      router.push('/login');
    }
  } else {
    localStorage.removeItem('auth_token');
  }
});

</script>

<template>
  <AppHeader v-if="!route.meta.hideMenu && !showStravaImport" />
  <RouterView v-slot="{ Component }">
    <keep-alive include="Karte">
      <component :is="Component" />
    </keep-alive>
  </RouterView>
  <button v-if="route.meta.showBack" class="back-button" @click="goBack" aria-label="Zurück zur Vorherigen Seite">
    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
      <path d="M560-240 320-480l240-240 56 56-184 184 184 184-56 56Z"/>
    </svg>
  </button>

  <StravaActivityPicker v-if="showStravaImport" @close="showStravaImport = false" />
  <AppToast />
</template>

<style>
/* html und body funktionieren in <style scoped> nicht! 
   Daher bleibt das hier ohne 'scoped', damit der graue Hintergrund überall gilt. */
html, body, #app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  background-color: var(--color-bg-page);
  /* Basis-Textfarbe: greift für alle Texte ohne eigene color-Regel (sonst
     bleiben sie beim UA-Standard schwarz und sind im Dunkel-Modus unlesbar) */
  color: var(--color-text);
  transition: var(--theme-transition);
  font-family: sans-serif;
  box-sizing: border-box;
}
#app {
  display: flex;
  flex-direction: column;
}
.back-button {
  position: fixed;
  /* Sitzt unter dem fixierten AppHeader statt daneben, seit der Hamburger-Button
     weggefallen ist */
  top: calc(var(--safe-top) + var(--app-header-height) + 0.5rem);
  left: 1rem;
  z-index: 1005;
  width: 44px;
  height: 44px;
  padding: 0;
  border: none;
  border-radius: var(--radius-lg);
  background: var(--color-bg-card);
  color: var(--color-primary);
  cursor: pointer;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}
.back-button:hover {
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}
</style>