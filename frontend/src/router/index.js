import { createRouter, createWebHistory } from 'vue-router';

import LoginView from '../components/LoginView.vue'; 

const routes = [
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