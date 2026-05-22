
import { createRouter, createWebHistory } from 'vue-router';
import ProfileView from '../components/ProfileView.vue'

import Karte from '../views/Karte.vue';

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
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes: routes
});

export default router;
