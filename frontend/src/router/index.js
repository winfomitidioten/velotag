import { createRouter, createWebHistory } from 'vue-router';

import Karte from '../views/Karte.vue';
import LoginView from '../components/LoginView.vue'; 

const routes = [
  {
    path: '/karte',
    name: 'karte',
    component: Karte
  },
  {
    path: '/',
    redirect: '/login', //Leitet direkt auf die /login weiter wenn man localhost aufruft
  },
  {  
    path: '/login',
    name: 'login',
    component: LoginView
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes: routes
});

export default router;