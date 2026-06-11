
import { createRouter, createWebHistory } from 'vue-router';
import ProfileView from '../components/ProfileView.vue'

import Karte from '../views/Karte.vue';
import LoginRegister from '@/views/LoginRegister.vue';
import GroupView from '../components/GroupView.vue'
import GroupDetailView from '../components/GroupDetailView.vue'
import GroupInviteView from '../components/GroupInviteView.vue'

const routes = [
  {
    path: '/karte',
    name: 'karte',
    component: Karte,
    meta: { requiresAuth: true }
  },
  {
      path: '/profile',
      name: 'profile',
      component: ProfileView,
      meta: { requiresAuth: true }
  }, 
  { 
    path: '/',
    redirect: '/login',
  },
  {   
    path: '/login',
    name: 'login',
    component: LoginRegister
  },
  {
    path: '/register',
    name: 'register',
    component: LoginRegister
  },
  {
    path: '/group',
    name: 'group',
    component: GroupView
  },
  {
    path: '/group/:id',
    name: 'group-detail',
    component: GroupDetailView
  },
  {
    path: '/group/invites',
    name: 'group-invites',
    component: GroupInviteView
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes: routes
});

router.beforeEach((to, from) => {
  const token = localStorage.getItem('auth_token');

  if (to.matched.some(record => record.meta.requiresAuth)) {
    if (!token) {
      return { name: 'login' };
    }
  }
});

export default router;
