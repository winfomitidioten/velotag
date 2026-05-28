
import { createRouter, createWebHistory } from 'vue-router';
import ProfileView from '../components/ProfileView.vue'

import Karte from '../views/Karte.vue';
import LoginView from '../components/LoginView.vue'; 
import GroupView from '../components/GroupView.vue'

const routes = [
  {
    path: '/karte',
    name: 'karte',
    component: Karte
  },
  {
      path: '/profile',
      name: 'profile',
      component: ProfileView
  }, 
  { 
    path: '/',
    redirect: '/login',
  },
  {   
    path: '/login',
    name: 'login',
    component: LoginView
  },
  {
    path: '/group',
    name: 'group',
    component: GroupView
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes: routes
});

export default router;
