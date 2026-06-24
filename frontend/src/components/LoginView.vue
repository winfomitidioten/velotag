<template>
    <form @submit.prevent="handleLogin">
        <div class="field">
            <label>E-Mail</label>
            <div class="input-wrapper">
                <span class="input-icon">✉</span>
                <input
                    type="email"
                    v-model="email"
                    required
                    placeholder="deine@email.com"
                />
            </div>
        </div>
        <div class="field">
            <label>Passwort</label>
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
            {{ loading ? 'Lädt...' : 'Anmelden' }}
        </button>

        <a class="forgot">Passwort vergessen?</a>
        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </form>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store/userStore';
import api from '@/api/api';

const router = useRouter();
const userStore = useUserStore();

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
        await userStore.fetchProfile();
        router.push('/karte');
    } catch (error) {
        if (error.response) {
            const data = error.response.data;

            if (data.non_field_errors) {
                errorMessage.value = 'Es wurde kein Konto mit dieser E-Mail-Adresse gefunden.';
            } else {
                errorMessage.value = 'Ungültige Eingabe. Bitte überprüfe deine Daten.';
            }
        } else if (error.request) {
            errorMessage.value = 'Verbindung zum Server fehlgeschlagen. Bitte versuche es später noch einmal.';
        } else {
            errorMessage.value = 'Ein unerwarteter Fehler ist aufgetreten. Versuche es später noch einmal.';
        }
    } finally {
        loading.value = false;
    }
};  
</script>


<style scoped>
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

