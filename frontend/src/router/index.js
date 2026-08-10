import { createRouter, createWebHistory } from 'vue-router';
import ProfileView from '../views/ProfileView.vue'
import Karte from '../views/Karte.vue';
import LoginRegister from '@/views/LoginRegister.vue';
import GroupView from '../views/GroupView.vue'
import GroupDetailView from '../views/GroupDetailView.vue'
import GroupLeaderboardView from '../components/GroupLeaderboardView.vue'
import GroupEditView from '../views/GroupEditView.vue'
import GroupInviteView from '../views/GroupInviteView.vue'
import JoinGroupView from '../views/JoinGroupView.vue'
import ComingSoon from '@/components/ComingSoon.vue';
import PublicUserProfile from '../views/PublicUserProfile.vue'
import { useUserStore } from '@/store/userStore';
import { setPendingRedirect } from '@/utils/pendingRedirect';

import SettingsView from '@/views/SettingsView.vue';

const routes = [
  {
    path: '/map',
    name: 'map',
    component: Karte,
    meta: { requiresAuth: true, title: 'Karte', hideTitle: true }
  },
  {
      // Das eigene Profil nutzt dieselbe Ansicht wie fremde Profile (/user/:id),
      // nur ohne :id - die eigene ID kommt dort aus dem userStore.
      path: '/profile',
      name: 'profile',
      component: PublicUserProfile,
      meta: { requiresAuth: true, title: 'Profil' }
  },
  {
      path: '/profile/edit',
      name: 'profile-edit',
      component: ProfileView,
      meta: { requiresAuth: true, showBack: true, backTo: '/profile', title: 'Profil bearbeiten' }
  },
  {
    path: '/',
    redirect: '/login',
    meta: { hideMenu: true }
  },
  {
    path: '/login',
    name: 'login',
    component: LoginRegister,
    meta: { hideMenu: true }
  },
  {
    path: '/register',
    name: 'register',
    component: LoginRegister,
    meta: { hideMenu: true }
  },
  {
    path: '/group',
    name: 'group',
    component: GroupView,
    meta: { requiresAuth: true, title: 'Meine Gruppen' }
  },
  {
    path: '/group/:id',
    name: 'group-detail',
    component: GroupDetailView,
    meta: { requiresAuth: true, showBack: true, backTo: '/group', title: 'Gruppe' }
  },
  {
    path: '/group/:id/edit',
    name: 'group-edit',
    component: GroupEditView,
    meta: {
      requiresAuth: true,
      showBack: true,
      backTo: (route) => `/group/${route.params.id}`,
      title: 'Gruppe bearbeiten'
    }
  },
  {
    path: '/group/:id/leaderboard',
    name: 'group-leaderboard',
    component: GroupLeaderboardView,
    meta: { requiresAuth: true, showBack: true, backTo: '/group' }
  },
  {
    path: '/group/invites',
    name: 'group-invites',
    component: GroupInviteView,
    // Kein showBack: Einladungen ist ein eigener Haupt-Tab in der AppTabBar,
    // genau wie /group und /rides - dort gibt es nichts, wohin man "zurück" ginge.
    meta: { requiresAuth: true, title: 'Einladungen' }
  },
  {
    // Ziel des Einladungslinks/QR-Codes aus GroupDetailView.vue (VEL-74).
    path: '/join/:token',
    name: 'group-join',
    component: JoinGroupView,
    meta: { requiresAuth: true, showBack: true }
  },
  {
    path: '/settings',
    name: 'settings',
    component: SettingsView,
    meta: { requiresAuth: true, showBack: true, backTo: '/profile', title: 'Einstellungen' }
  },
  {
    path: '/rides',
    name: 'rides',
    component: () => import('../views/StreckenView.vue'),
    meta: { requiresAuth: true, title: 'Meine Strecken' }
  },
  {
    path: '/datenschutz',
    name: 'privacy',
    component: ComingSoon,
    meta: { requiresAuth: true, showBack: true, backTo: '/settings', title: 'Datenschutz' }
  },
  {
    path: '/impressum',
    name: 'imprint',
    component: ComingSoon,
    meta: { requiresAuth: true, showBack: true, backTo: '/settings', title: 'Impressum' }
  },
  {
    path: '/user/:id',
    name: 'user-profile',
    component: PublicUserProfile,
    meta: {
      requiresAuth: true,
      showBack: true,
      // Fremde Profile werden aus verschiedenen Ansichten geöffnet (Gruppe,
      // Bestenliste). Der Aufrufer hängt seinen Pfad als ?from= an, damit "Zurück"
      // dorthin führt statt auf die Karte. Nur interne Pfade zulassen - ein
      // absoluter Wert aus der URL soll die Navigation nicht umlenken können.
      backTo: (route) => {
        const from = route.query.from;
        return typeof from === 'string' && from.startsWith('/') && !from.startsWith('//')
          ? from
          : '/map';
      }
    }
  },
  {
    path: '/onboarding',
    name: 'onboarding',
    component: () => import('../views/OnboardingView.vue'),
    meta: { requiresAuth: true, hideMenu: true }
  },

];

const router = createRouter({
  history: createWebHistory(),
  routes: routes
});

router.beforeEach((to) => {
  const token = localStorage.getItem('auth_token');

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!token) {
      // Ziel merken (z.B. Einladungslink), damit Login.vue nach erfolgreichem
      // Login/Registrieren dorthin statt zur Karte springen kann.
      setPendingRedirect(to.fullPath);
      return { name: 'login' };
    }

    const userStore = useUserStore();
    // Tri-state: null heißt "Profil noch nicht geladen" und wird hier bewusst NICHT
    // umgeleitet (sonst Redirect-Flackern vor Abschluss von fetchProfile) - nur explizit
    // false/true lösen eine Weiterleitung aus.
    if (userStore.onboardingCompleted === false && to.name !== 'onboarding') {
      // Gleiches Prinzip, falls schon eingeloggt aber Onboarding noch offen ist.
      setPendingRedirect(to.fullPath);
      return { name: 'onboarding' };
    }
    if (userStore.onboardingCompleted === true && to.name === 'onboarding') {
      return { name: 'map' };
    }
  }
});

export default router;