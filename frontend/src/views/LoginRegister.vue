<script setup>
import { ref } from 'vue';
import Login from '@/components/Login.vue';
import Register from '@/components/Register.vue';

const activeTab = ref('login'); // steuert welcher Tab aktiv ist  

const registeredMessage = ref('');
const onRegistered = () => {
    registeredMessage.value = 'Ihre Registrierung war erfolgreich. Bitte melden Sie sich nun an.';
    activeTab.value = 'login';
}
</script>

<template>
    <div class="login-page">
        <div class="login-box">

            <!-- Logo & Tagline -->
             <div class="header">
                <img src="@/assets/logo-light.png" alt="velotag logo" class="logo logo--light" />
                <img src="@/assets/logo-dark.png" alt="velotag logo" class="logo logo--dark" />
                <p class="tagline">Deine Touren - alle auf einen Blick</p>
             </div>
             
             <!-- Tab-Switcher (Login/Register) -->
              <div class="tabs">
                <button
                    :class="['tab', activeTab === 'login' ? 'tab--active' : '']"
                    @click="activeTab = 'login'"
                >Login</button>
                <button
                    :class="['tab', activeTab === 'register' ? 'tab--active' : '']"
                    @click="activeTab = 'register'"
                >Registrierung</button>
              </div>

              <Register v-if="activeTab === 'register'" @registered="onRegistered" />
              <p v-if="registeredMessage && activeTab === 'login'" class="success-message">
                {{ registeredMessage }}
              </p>
              <Login v-if="activeTab === 'login'" />
        </div>
    </div>
</template>

<style scoped>
/* --- Seite --- */
.login-page {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh; 
    background-color: var(--color-bg-page);
    padding: 1rem;
}

/* --- Box: hebt sich vom Hintergrund ab --- */
.login-box {
    background: var(--color-bg-card);
    border-radius: var(--radius-lg); 
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
    padding: 2.5rem 2rem;
    width: 100%;
    max-width: 440px;
}

/* --- Media Queries: "wenn Bildschirm kleiner als X" --- */

/* Tablet (unter 768px) */
@media (max-width: 768px) {
    .login-box {
        padding: 2rem 1.5rem;
    }
}

/* Handy (unter 480px) */
@media (max-width: 480px) {
    .login-box {
        padding: 1.5rem 1rem;
        border-radius: 12px;
        box-shadow: none;      /* auf Handy wirkt Box ohne Schatten cleaner */
    }
}

/* --- Logo & Tagline --- */
.header {
    text-align: center;
    margin-bottom: 1.75rem;
}
.logo {
    height: 100px;
    margin-bottom: 0.5rem;
}

/* Wortmarke ist dunkel eingefärbt -> im Dunkel-Modus die helle Variante zeigen,
   sonst wäre der Schriftzug auf dunklem Karten-Hintergrund unlesbar */
.logo--dark {
    display: none;
}
:root[data-theme='dark'] .logo--light {
    display: none;
}
:root[data-theme='dark'] .logo--dark {
    display: inline;
}
@media (prefers-color-scheme: dark) {
    :root:not([data-theme]) .logo--light {
        display: none;
    }
    :root:not([data-theme]) .logo--dark {
        display: inline;
    }
}

.tagline {
    font-size: 14px;
    color: var(--color-text-muted);
    margin: 0;
}

/* --- Tabs --- */
.tabs {
    display: flex;
    background: var(--color-bg-page);   /* grauer Hintergrund für inaktive Seite */
    border-radius: 10px;
    padding: 4px;
    margin-bottom: 1.75rem;
}
.tab {
    flex: 1;
    padding: 10px;
    border: none;
    border-radius: 8px;
    background: transparent;
    font-size: 14px;
    font-weight: 500;
    color: var(--color-text-muted);
    cursor: pointer;
    transition: all 0.2s;
}
.tab--active {
    background: var(--color-primary);   /* Grün wenn aktiv */
    color: var(--color-on-primary);
    box-shadow: 0 2px 8px rgba(var(--color-primary-rgb), 0.3);
}
.success-message {
    background: rgba(var(--color-primary-rgb), 0.1);
    color: var(--color-primary);
    border: 1px solid rgba(var(--color-primary-rgb), 0.3);
    border-radius: 8px;
    padding: 10px 14px;
    font-size: 13px;
    text-align: center;
    margin-bottom: 1rem;
}
</style>

