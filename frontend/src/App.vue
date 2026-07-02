<script setup>
import { RouterView, useRoute, useRouter } from 'vue-router'
import { onMounted } from 'vue'
import MenuBar from '@/components/MenuBar.vue'
import { useUserStore } from '@/store/userStore'
import { Capacitor } from '@capacitor/core'
import { App as CapacitorApp } from '@capacitor/app'
import { StatusBar, Style } from '@capacitor/status-bar'
import apiClient from '@/api/client'


const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

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
    await StatusBar.setStyle({ style: Style.Dark });

    // Fängt den velotag://strava-callback Deep Link ab, mit dem das Backend
    // nach dem Strava-Login zurück in die App springt
    CapacitorApp.addListener('appUrlOpen', ({ url }) => {
      if (url.startsWith('velotag://strava-callback')) {
        router.push('/map');
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
  <MenuBar v-if="!route.meta.hideMenu" />
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
</template>

<style>
/* html und body funktionieren in <style scoped> nicht! 
   Daher bleibt das hier ohne 'scoped', damit der graue Hintergrund überall gilt. */
html, body, #app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  background-color: #f5f7f8;
  font-family: sans-serif;
  box-sizing: border-box;
}
#app {
  display: flex;
  flex-direction: column;
}
.back-button {
  position: fixed;
  top: calc(var(--safe-top) + 0.5rem);
  left: calc(1rem + 44px + 0.75rem);
  z-index: 1010;
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