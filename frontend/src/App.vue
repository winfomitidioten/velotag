<script setup>
import { RouterView, useRoute, useRouter } from 'vue-router'
import { onMounted, onUnmounted, watch } from 'vue'
import apiClient from '@/api/client'

import AppHeader from '@/components/AppHeader.vue'
import AppToast from '@/components/AppToast.vue'
import AppTabBar from '@/components/AppTabBar.vue'
import DesktopNavBar from '@/components/DesktopNavBar.vue'
import StravaActivityPicker from '@/components/StravaActivityPicker.vue'

import { useUserStore } from '@/store/userStore'
import { useSettingsStore } from './store/settingsStore'

import { useStravaImport } from '@/composables/useStravaImport'
import { useToast } from '@/composables/useToast'
import { useSwipeBack } from '@/composables/useSwipeBack'
import { isMobile, updateIsMobile } from '@/composables/viewport'
import { consumePendingRedirect } from '@/utils/pendingRedirect'

import { Capacitor } from '@capacitor/core'
import { App as CapacitorApp } from '@capacitor/app'
import { StatusBar, Style } from '@capacitor/status-bar'
import { LocalNotifications } from '@capacitor/local-notifications'
import { PushNotifications } from '@capacitor/push-notifications'

const settingsStore = useSettingsStore(); // Konstruktor wendet gespeichertes Theme sofort an

const route = useRoute();
const router = useRouter();
const userStore = useUserStore();

const { showStravaImport } = useStravaImport();
const { showToast } = useToast();

// Registriert das Geraet fuer Push-Benachrichtigungen bei Gruppeneinladungen (nur Android).
const setupAndroidPush = async () => {
  if (Capacitor.getPlatform() !== 'android') {
    return;
  }
  try {
    let permStatus = await PushNotifications.checkPermissions();

    if (permStatus.receive === 'prompt') {
      permStatus = await PushNotifications.requestPermissions();
    }

    if (permStatus.receive !== 'granted') {
      console.log("Nutzer hat Benachrichtigungen blockiert");
      return;
    }

    // Ohne eigenen Channel landet die Benachrichtigung nur im Verlauf (Shade),
    // zeigt aber kein Heads-up-Banner auf dem Sperr-/Homebildschirm. importance: 5
    // (IMPORTANCE_HIGH) ist dafür nötig. Die channel_id muss im Backend beim
    // Versand exakt so referenziert werden (siehe notifications.py).
    await PushNotifications.createChannel({
      id: 'group_invitations',
      name: 'Gruppeneinladungen',
      description: 'Benachrichtigungen über neue Gruppeneinladungen',
      importance: 5,
    });

    // Listener MÜSSEN vor register() angehängt werden: Capacitor kann das
    // 'registration'-Event nativ nahezu sofort feuern, sobald register() aufgerufen
    // wird - wenn der Listener erst danach registriert wird, geht der Token verloren
    // ("No listeners found for event registration" im Logcat).
    // Wichtig: der Event-Name ist 'registration', NICHT 'register' (das ist nur der
    // Methodenname von PushNotifications.register() weiter unten).
    await PushNotifications.addListener('registration', async (token) => {
      try {
        await apiClient.post('/user/save-push-token/', {
          token: token.value,
          platform: 'android'
        });
      } catch (err) {
        console.error("Fehler beim Senden des Tokens an Backend: ", err);
      }
    });

    await PushNotifications.addListener('pushNotificationActionPerformed', (action) => {
      console.log("Nutzer hat Benachrichtigung geklickt", action.notification);
      const data = action.notification.data;

      if (data && data.type == 'group_invitation') {
        router.push('group/invitations');
      }
    });

    // Bei geöffneter App zeigt Android selbst kein System-Banner für die
    // empfangene Nachricht (das Notification-Objekt wird nur an die App
    // weitergereicht) - hier übernehmen wir das mit unserem eigenen Toast,
    // statt dass die Benachrichtigung sonst unbemerkt bliebe.
    await PushNotifications.addListener('pushNotificationReceived', (notification) => {
      showToast(`${notification.title}: ${notification.body}`);
    });

    await PushNotifications.register();
  } catch (error) {
    console.log("Fehler beim Push:", error)
  }
}

// Feste ID fuer die taegliche Erinnerung: schedule() mit derselben ID ersetzt
// eine bereits geplante Benachrichtigung, statt Duplikate anzuhaeufen - daher
// reicht ein einfacher Check ueber getPending(), ob sie schon existiert.
const DAILY_REMINDER_ID = 1001;

// Rein lokale, taegliche Erinnerung ans Radfahren (kein Backend/Server noetig,
// laeuft komplett auf dem Geraet).
const setupDailyReminder = async () => {
  if (!Capacitor.isNativePlatform()) {
    return;
  }
  try {
    let permStatus = await LocalNotifications.checkPermissions();

    if (permStatus.display === 'prompt') {
      permStatus = await LocalNotifications.requestPermissions();
    }

    if (permStatus.display !== 'granted') {
      console.log("Nutzer hat lokale Benachrichtigungen blockiert");
      return;
    }

    const { notifications: pending } = await LocalNotifications.getPending();
    if (pending.some((n) => n.id === DAILY_REMINDER_ID)) {
      return; // schon geplant, z.B. von einem frueheren App-Start
    }

    await LocalNotifications.schedule({
      notifications: [{
        id: DAILY_REMINDER_ID,
        title: 'Schon gefahren heute? 🚴',
        body: 'Vergiss nicht, deine heutige Fahrt in velotag festzuhalten.',
        schedule: {
          on: { hour: 11, minute: 0 },
          repeats: true,
        },
      }],
    });
  } catch (error) {
    console.log("Fehler bei der taeglichen Erinnerung:", error)
  }
}
const swipeBack = useSwipeBack();

const setAppHeight = () => {
  document.documentElement.style.setProperty('--app-height', `${window.innerHeight}px`);
  updateIsMobile();
};

// Kompaktere Header-Höhe nur auf der Karte UND nur mobil - die Desktop-Navbar
// nutzt dieselbe Variable (main.css, @media min-width:768px), daher hier ohne
// Inline-Override die CSS-eigenen Werte (mobil 52px / desktop 56px) greifen lassen.
watch([() => route.name, isMobile], ([name, mobile]) => {
  if (mobile && name === 'map') {
    document.documentElement.style.setProperty('--app-header-height', '28px');
  } else {
    document.documentElement.style.removeProperty('--app-header-height');
  }
}, { immediate: true });

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
  await setupDailyReminder();
  await setupAndroidPush();
  if (Capacitor.isNativePlatform()) {
    // baseURL wird bereits in api/client.js korrekt gesetzt (VITE_API_BASE_URL ??
    // Produktion) - eine feste Override hier wuerde das jedes Mal ueberschreiben,
    // inklusive waehrend des asynchronen Push-Registrierungs-Events oben.
    await StatusBar.setOverlaysWebView({ overlay: true });
    updateStatusBarStyle();
    watch(() => settingsStore.theme, updateStatusBarStyle);
    prefersDark.addEventListener('change', updateStatusBarStyle);

    // Fängt Deep Links ab: velotag://strava-callback (Backend springt nach dem
    // Strava-Login zurück in die App) sowie Gruppeneinladungslinks, egal ob als
    // velotag://join?token=... oder als normaler http-Link geöffnet (siehe
    // AndroidManifest.xml für die zugehörigen Intent-Filter).
    const handleAppUrl = (url) => {
      if (url.startsWith('velotag://strava-callback')) {
        router.push('/map');
        showStravaImport.value = true;
        return;
      }

      const joinToken = url.includes('/join/')
        ? url.split('/join/')[1]
        : new URL(url).searchParams.get('token');
      if (joinToken) {
        router.push(`/join/${joinToken}`);
      }
    };

    CapacitorApp.addListener('appUrlOpen', ({ url }) => handleAppUrl(url));

    // Wird die App per Deep Link erst frisch gestartet (statt nur aus dem
    // Hintergrund geholt), kann appUrlOpen feuern bevor der Listener oben
    // registriert ist - getLaunchUrl() liefert die Start-URL in diesem Fall
    // zusätzlich explizit nach.
    const launch = await CapacitorApp.getLaunchUrl();
    if (launch?.url) {
      handleAppUrl(launch.url);
    }
  }

  setAppHeight();
  window.addEventListener('resize', setAppHeight);
  swipeBack.start();
  const token = localStorage.getItem('auth_token');
  if (token && token !== 'undefined') {
    try {

      await userStore.ensureProfile();

      // Die Root-Route leitet beim (Kalt-)Start immer erst auf /login um (siehe
      // router/index.js) - mit gültigem Token wollen wir stattdessen direkt zur Karte,
      // statt den Nutzer bei jedem App-Neustart erneut das Login-Formular sehen zu lassen.
      if (route.path === '/login' || route.path === '/') {
        router.push(consumePendingRedirect() ?? '/map');
      }

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
  <template v-if="!route.meta.hideMenu && !showStravaImport">
    <AppHeader v-if="isMobile" />
    <DesktopNavBar v-else />
  </template>

  <RouterView v-slot="{ Component }">
    <!-- sessionKey wechselt beim Logout und wirft die zwischengespeicherte Karte weg,
         die sonst die Daten des vorherigen Accounts weiterzeigen würde (siehe userStore).
         Der Key MUSS am <keep-alive> hängen, nicht am <component>: innen drin würde
         nur eine zweite Instanz unter neuem Key entstehen, während die alte im Cache
         liegen bleibt und lediglich deaktiviert wird - ihr onUnmounted (und damit das
         Aufräumen der Leaflet-Instanz in Karte.vue) liefe dann nie. -->
    <keep-alive include="Karte" :key="userStore.sessionKey">
      <component :is="Component" />
    </keep-alive>
  </RouterView>

  <AppTabBar v-if="isMobile && !route.meta.hideMenu && !showStravaImport" />

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
</style>
