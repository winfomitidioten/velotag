
import { createRouter, createWebHistory } from 'vue-router';
import ProfileView from '../views/ProfileView.vue'
import Karte from '../views/Karte.vue';
import LoginRegister from '@/views/LoginRegister.vue';
import GroupView from '../views/GroupView.vue'
import GroupDetailView from '../views/GroupDetailView.vue'
import GroupInviteView from '../views/GroupInviteView.vue'
import ComingSoon from '@/components/ComingSoon.vue';

const routes = [
  {
    path: '/map',
    name: 'map',
    component: Karte,
    meta: { requiresAuth: true }
  },
  {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true, showBack: true }
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
    meta: { requiresAuth: true, showBack: true }
  },
  {
    path: '/group/:id',
    name: 'group-detail',
    component: GroupDetailView,
    meta: { requiresAuth: true, showBack: true, backTo: '/group' }
  },
  {
    path: '/group/invites',
    name: 'group-invites',
    component: GroupInviteView,
    meta: { requiresAuth: true, showBack: true }
  },
  {
    path: '/settings',
    name: 'settings',
    component: ComingSoon,
    meta: { requiresAuth: true, showBack: true, title: 'Einstellungen' }
  },
  {
    path: '/rides',
    name: 'rides',
    component: () => import('../views/StreckenView.vue'),
    meta: { requiresAuth: true, showBack: true }
  }
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
