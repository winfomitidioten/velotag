
import { createRouter, createWebHistory } from 'vue-router';
import ProfileView from '../views/ProfileView.vue'
import Karte from '../views/Karte.vue';
import LoginRegister from '@/views/LoginRegister.vue';
import GroupView from '../views/GroupView.vue'
import GroupDetailView from '../views/GroupDetailView.vue'
import GroupEditView from '../views/GroupEditView.vue'
import GroupInviteView from '../views/GroupInviteView.vue'
import ComingSoon from '@/components/ComingSoon.vue';
import PublicUserProfile from '../components/PublicUserProfile.vue'

import SettingsView from '@/views/SettingsView.vue';

const routes = [
  {
    path: '/map',
    name: 'map',
    component: Karte,
    meta: { requiresAuth: true, title: 'Karte', hideTitle: true }
  },
  {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true, title: 'Profil' }
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
    path: '/group/invites',
    name: 'group-invites',
    component: GroupInviteView,
    meta: { requiresAuth: true, title: 'Einladungen' }
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
    meta: { requiresAuth: true, showBack: true }
  },
  {
  path: '/user/:id',
  name: 'user-profile',
  component: PublicUserProfile,
  meta: { requiresAuth: true, showBack: true }
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
      return { name: 'login' };
    }
  }
});

export default router;
