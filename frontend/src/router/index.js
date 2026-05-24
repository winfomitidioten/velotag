
import { createRouter, createWebHistory } from 'vue-router';
import ProfileView from '../components/ProfileView.vue'

import Karte from '../views/Karte.vue';
import LoginView from '../components/LoginView.vue'; 

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
  }, // <-- Hier fehlte das Komma
  { // <-- Hier fehlte die öffnende geschweifte Klammer
    path: '/',
    redirect: '/login',
  },
  {   
    path: '/login',
    name: 'login',
    component: LoginView
  },
];

export default router;
