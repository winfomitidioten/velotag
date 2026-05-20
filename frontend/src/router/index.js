import { createRouter, createWebHistory } from 'vue-router'
import ProfileView from '../components/ProfileView.vue'

const routes = [
    {
        path: '/profile',
        name: 'profile',
        component: ProfileView
    }
]

const router = createRouter({
    history: createWebHistory(),
    routes: routes
})

export default router