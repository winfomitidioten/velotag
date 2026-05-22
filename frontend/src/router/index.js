import { createRouter, createWebHistory } from 'vue-router';

import Karte from '../views/Karte.vue';

const routes = [
  {
    path: '/karte',
    name: 'karte',
    component: Karte
  },
];

const router = createRouter({
  history: createWebHistory(),
  routes: routes
});

export default router;