<template>
    <div class="login-page">
        <div class="login-box">

            <!-- Logo & Tagline -->
             <div class="header">
                <img src="@/assets/logo.png" alt="velotag logo" class="logo" />
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

              <LoginView v-if="activeTab === 'login'" />
              <RegisterView v-if="activeTab === 'register'" />
              
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import LoginView from '@/components/LoginView.vue';
import RegisterView from '@/components/RegisterView.vue';

const activeTab = ref('login'); // steuert welcher Tab aktiv ist  
</script>


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
.tagline {
    font-size: 14px;
    color: #888;
    margin: 0;
}

/* --- Tabs --- */
.tabs {
    display: flex;
    background: #f0f2f5;   /* grauer Hintergrund für inaktive Seite */
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
    color: #888;
    cursor: pointer;
    transition: all 0.2s;
}
.tab--active {
    background: var(--color-primary);   /* Grün wenn aktiv */
    color: #ffffff;
    box-shadow: 0 2px 8px rgba(61, 184, 151, 0.3);
}
</style>

