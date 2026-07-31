<script setup>
import { RouterView, useRoute, useRouter } from 'vue-router'
import { onMounted, onUnmounted, watch } from 'vue'
import apiClient from '@/api/client'

import AppHeader from '@/components/AppHeader.vue'
import AppTabBar from '@/components/AppTabBar.vue'
import StravaActivityPicker from '@/components/StravaActivityPicker.vue'

import { useUserStore } from '@/store/userStore'
import { useSettingsStore } from './store/settingsStore'

import { useStravaImport } from '@/composables/useStravaImport'
import { useSwipeBack } from '@/composables/useSwipeBack'

import { Capacitor } from '@capacitor/core'
import { App as CapacitorApp } from '@capacitor/app'
import { StatusBar, Style } from '@capacitor/status-bar'

const settingsStore = useSettingsStore(); // Konstruktor wendet gespeichertes Theme sofort an

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();
const { showStravaImport } = useStravaImport();
const swipeBack = useSwipeBack();

const setAppHeight = () => {
  document.documentElement.style.setProperty('--app-height', `${window.innerHeight}px`);
};

// Bei theme='system' folgt die Statusleiste der OS-Einstellung, sonst der
// manuell gewählten
const prefersDark = window.matchMedia('(prefers-color-scheme: dark)');

const updateStatusBarStyle = () => {
  if (!Capacitor.isNativePlatform()) return;
  const isDark = settingsStore.theme === 'dark'
    || (settingsStore.theme === 'system' && prefersDark.matches);
  // Style.Dark => helle Uhr/Batterie-Icons (für unseren dunklen Hintergrund im Dark Mode)
  // Style.Light => dunkle Icons (für den hellen Hintergrund im Light Mode)
  // (Die Namen sind entgegen der Intuition nach dem Hintergrund benannt, nicht nach der Icon-Farbe)
  StatusBar.setStyle({ style: isDark ? Style.Dark : Style.Light });
};

onMounted(async () => {
  if (Capacitor.isNativePlatform()) {
    apiClient.defaults.baseURL = 'http://167.233.33.166/api';
    await StatusBar.setOverlaysWebView({ overlay: true });
    updateStatusBarStyle();
    watch(() => settingsStore.theme, updateStatusBarStyle);
    prefersDark.addEventListener('change', updateStatusBarStyle);

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
  swipeBack.start();
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

onUnmounted(() => {
  swipeBack.stop();
  prefersDark.removeEventListener('change', updateStatusBarStyle);
});
</script>

<template>
  <AppHeader v-if="!route.meta.hideMenu && !showStravaImport" />
  <RouterView v-slot="{ Component }">
    <keep-alive include="Karte">
      <component :is="Component" />
    </keep-alive>
  </RouterView>
  <AppTabBar v-if="!route.meta.hideMenu && !showStravaImport" />

  <StravaActivityPicker v-if="showStravaImport" @close="showStravaImport = false" />
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
</style>