<template>
    <div class="login-page">
        <div class="login-box">

            <!-- Logo & Tagline -->
             <div class="header">
                <img src="@/assets/logo.png" alt="velotag logo" class="logo" />
                <p class="tagline">Document your rides</p>
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
                >Register</button>
              </div>

              <!-- Login-Formular -->
               <form v-if="activeTab == 'login'" @submit.prevent="handleLogin">
                    <div class="field">
                        <label>Email</label>
                        <div class="input-wrapper">
                            <span class="input-icon">✉</span>
                            <input
                                type="email"
                                v-model="email"
                                required
                                placeholder="your@email.com"
                            />
                        </div>
                    </div>
                    <div class="field">
                    <label>Password</label>
                    <div class="input-wrapper">
                        <span class="input-icon">🔒</span>
                        <input
                            type="password"
                            v-model="password"
                            required
                            placeholder="••••••••"
                        />
                    </div>
                </div>

                <button type="submit" class="btn-primary" :disabled="loading">
                    {{ loading ? 'Loading...' : 'Sign In' }}
                </button>

                <a class="forgot">Forgot password?</a>
                <p v-if="errorMessage" class="error">{{ errorMessage }}</p>

               </form>

               <!-- Register-Formular (Platzhalter) -->
                <form v-if="activeTab === 'register'" @submit.prevent="">
                    <div class="field">
                        <label>Email</label>
                        <div class="input-wrapper">
                            <span class="input-icon">✉</span>
                            <input type="email" placeholder="your@email.com" />
                        </div>
                    </div>
                    <div class="field">
                        <label>Password</label>
                        <div class="input-wrapper">
                            <span class="input-icon">🔒</span>
                            <input type="password" placeholder="••••••••" />
                        </div>
                    </div>
                    <button type="submit" class="btn-primary">Register</button>
                </form>
        </div>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '@/api/api';

const activeTab = ref('login'); // steuert welcher Tab aktiv ist 
const email = ref('');
const password = ref('');
const loading = ref(false);
const errorMessage = ref('');

const handleLogin = async () => {
    loading.value = true;
    errorMessage.value = '';

    try {
        const response = await api.post('login/', {
            username: email.value,
            password: password.value,
        });
        localStorage.setItem('auth_token', response.data.token);
    } catch (error) {
        if (error.response?.data?.non_field_errors) {
            errorMessage.value = 'E-Mail oder Passwort ist falsch!';
        } else if (error.response?.data?.detail) {
            errorMessage.value = error.response.data.detail;
        } else if (error.request) {
            errorMessage.value = 'Keine Verbindung zum Server.';
        } else {
            errorMessage.value = 'Ein unerwarteter Fehler ist aufgetreten.';
        }
    } finally {
        loading.value = false;
    }
};  
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

/* --- Felder --- */
.field {
    margin-bottom: 1.1rem;
}
.field label {
    display: block;
    font-size: 13px;
    font-weight: 500;
    color: #555;
    margin-bottom: 6px;
}

/* input-wrapper: Icon + Input nebeneinander */
.input-wrapper {
    display: flex;
    align-items: center;
    border: 1.5px solid #e5e7eb;
    border-radius: 10px;
    padding: 0 14px;
    background: #fff;
    transition: border-color 0.2s;
}
.input-wrapper:focus-within {
    border-color: var(--color-primary);  /* grüner Rand wenn Input fokussiert */
}
.input-icon {
    font-size: 15px;
    margin-right: 10px;
    color: #aaa;
}
.input-wrapper input {
    flex: 1;
    border: none;
    outline: none;
    padding: 11px 0;
    font-size: 14px;
    color: #1a1a1a;
    background: transparent;
}

/* --- Button --- */
.btn-primary {
    width: 100%;
    padding: 13px;
    background: var(--color-primary); 
    color: #fff;
    border: none;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    margin-top: 0.5rem;
    transition: background 0.2s, transform 0.1s;
}
.btn-primary:hover  { background: var(--color-primary-dark); }
.btn-primary:active { transform: scale(0.98); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

/* --- Forgot / Error --- */
.forgot {
    display: block;
    text-align: center;
    font-size: 13px;
    color: #888;
    margin-top: 1rem;
    cursor: pointer;
}
.forgot:hover { color: #3db897; }

.error {
    color: #e53e3e;
    font-size: 13px;
    text-align: center;
    margin-top: 0.75rem;
}
</style>

