<template>    
    <button class="menu-button" @click="toggleMenu" aria-label="Menü öffnen">☰</button>
    
    <transition name="fade">
        <div v-if="isOpen" class="overlay" @click="closeMenu"></div>
    </transition>

    <aside class="sidebar" :class="{ 'is-open': isOpen }">
        <button class="close-button" @click="closeMenu" aria-label="Menü schließen">✕</button>
        
        <nav>
            <ul>
                <li><a href="#" @click="closeMenu">Profil</a></li>
                <li><a href="#" @click="closeMenu">Gruppen</a></li>
                <li><a href="#" @click="closeMenu">Einstellungen</a></li>
                <li><a href="#" @click="closeMenu">Logout</a></li>
            </ul>
        </nav>
    </aside>
    
</template>

<script setup>
import { ref } from 'vue';

const isOpen = ref(false);

const toggleMenu = () => {
    isOpen.value = !isOpen.value;
};
const closeMenu = () => {
    isOpen.value = false;
};
</script>

<style scoped>
.menu-button {
    position: fixed;
    top: 1rem;
    left: 1rem;
    z-index: 1010;
    display: flex;
    align-items: center;
    justify-content: center;
    width: 44px;
    height: 44px;
    font-size: 1.4rem;
    cursor: pointer;
    border: none;
    border-radius: var(--radius-lg);
    background: var(--color-primary);   /* Grün wie aktive Tab */
    color: #ffffff;
    box-shadow: 0 2px 8px rgba(61, 184, 151, 0.3);
    transition: all 0.2s;
}
.menu-button:hover {
    box-shadow: 0 4px 12px rgba(61, 184, 151, 0.4);
}

.sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    width: 280px;
    background: var(--color-bg-card);
    padding: 2.5rem 1.5rem;
    box-sizing: border-box;
    z-index: 1030;
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);  /* gleicher Schatten wie .login-box */

    transform: translateX(-100%);
    transition: transform 0.3s ease;
}
.sidebar.is-open {
    transform: translateX(0);
}

.close-button {
    position: absolute;
    top: 1rem;
    right: 1rem;
    width: 32px;
    height: 32px;
    border: none;
    border-radius: 8px;
    background: #f0f2f5;
    color: #888;
    font-size: 1rem;
    cursor: pointer;
    transition: all 0.2s;
}
.close-button:hover {
    background: #e4e7eb;
    color: #555;
}

nav ul {
    list-style: none;
    padding: 0;
    margin: 2rem 0 0;
}
nav li {
    margin-bottom: 0.5rem;
}
nav a {
    display: block;
    padding: 10px 14px;
    border-radius: 8px;
    color: #888;
    text-decoration: none;
    font-size: 14px;
    font-weight: 500;
    transition: all 0.2s;
}
nav a:hover {
    background: #f0f2f5;
    color: #333;
}
nav a.is-active {
    background: var(--color-primary);
    color: #ffffff;
    box-shadow: 0 2px 8px rgba(61, 184, 151, 0.3);
}

.overlay {
    position: fixed;
    inset: 0;
    background: rgba(0, 0, 0, 0.4);
    z-index: 1020;
}
.fade-enter-active,
.fade-leave-active {
    transition: opacity 0.3s ease;
}
.fade-enter-from,
.fade-leave-to {
    opacity: 0;
}

@media (max-width: 480px) {
    .sidebar {
        width: 85%;   /* auf dem Handy schmaler Bildschirm nutzen */
    }
}
</style>