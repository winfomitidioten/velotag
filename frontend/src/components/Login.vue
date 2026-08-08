<template>
    <form @submit.prevent="handleLogin">
        <div class="field">
            <label>E-Mail</label>
            <div class="input-wrapper">
                <span class="input-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                        <path d="M160-160q-33 0-56.5-23.5T80-240v-480q0-33 23.5-56.5T160-800h640q33 0 56.5 23.5T880-720v480q0 33-23.5 56.5T800-160H160Zm320-280L160-640v400h640v-400L480-440Zm0-80 320-200H160l320 200ZM160-640v-80 480-400Z"/>
                    </svg>
                </span>
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
                <span class="input-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                        <path d="M240-80q-33 0-56.5-23.5T160-160v-400q0-33 23.5-56.5T240-640h40v-80q0-83 58.5-141.5T480-920q83 0 141.5 58.5T680-720v80h40q33 0 56.5 23.5T800-560v400q0 33-23.5 56.5T720-80H240Zm0-80h480v-400H240v400Zm296.5-143.5Q560-327 560-360t-23.5-56.5Q513-440 480-440t-56.5 23.5Q400-393 400-360t23.5 56.5Q447-280 480-280t56.5-23.5ZM360-640h240v-80q0-50-35-85t-85-35q-50 0-85 35t-35 85v80ZM240-160v-400 400Z"/>
                    </svg>
                </span>
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
import { consumePendingRedirect } from '@/utils/pendingRedirect';

const router = useRouter();
const userStore = useUserStore();

const email = ref('');
const password = ref('');
const loading = ref(false);
const errorMessage = ref('');

const handleLogin = async () => {
    loading.value = true;
    errorMessage.value = '';
    localStorage.removeItem('auth_token');

    try {
        const response = await api.post('login/', {
            username: email.value,
            password: password.value,
        });
        localStorage.setItem('auth_token', response.data.token);
        await userStore.fetchProfile();
        // Onboarding-Pflicht greift beim nächsten Routenwechsel automatisch über den
        // Router-Guard (router/index.js) - das gemerkte Ziel (z.B. Einladungslink)
        // bleibt dabei erhalten, siehe OnboardingView.vue.
        router.push(consumePendingRedirect() ?? '/map');
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
    color: var(--color-text-muted);
    margin-bottom: 6px;
}

/* input-wrapper: Icon + Input nebeneinander */
.input-wrapper {
    display: flex;
    align-items: center;
    border: 1.5px solid var(--color-border);
    border-radius: 10px;
    padding: 0 14px;
    background: var(--color-bg-card);
    transition: border-color 0.2s;
}
.input-wrapper:focus-within {
    border-color: var(--color-primary);  /* grüner Rand wenn Input fokussiert */
}
.input-icon {
    display: flex;
    align-items: center;
    flex-shrink: 0;
    margin-right: 10px;
    color: var(--color-primary);
}
.input-icon svg {
    width: 16px;
    height: 16px;
}
.input-wrapper input {
    flex: 1;
    border: none;
    outline: none;
    padding: 11px 0;
    font-size: 14px;
    color: var(--color-text);
    background: transparent;
}

/* --- Button --- */
.btn-primary {
    width: 100%;
    padding: 13px;
    background: var(--color-primary);
    color: var(--color-on-primary);
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
    color: var(--color-text-muted);
    margin-top: 1rem;
    cursor: pointer;
}
.forgot:hover { color: var(--color-primary); }

.error {
    color: var(--color-danger);
    font-size: 13px;
    text-align: center;
    margin-top: 0.75rem;
}
</style>

