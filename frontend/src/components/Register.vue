<template>
    <form @submit.prevent="handleRegister">
        <div class="field">
            <label>E-Mail</label>
            <div class="input-wrapper">
                <span class="input-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                        <path d="M160-160q-33 0-56.5-23.5T80-240v-480q0-33 23.5-56.5T160-800h640q33 0 56.5 23.5T880-720v480q0 33-23.5 56.5T800-160H160Zm320-280L160-640v400h640v-400L480-440Zm0-80 320-200H160l320 200ZM160-640v-80 480-400Z"/>
                    </svg>
                </span>
                <input type="email" v-model="email" required placeholder="max.mustermann@velotag.de" />
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
                <input type="password" v-model="password" required placeholder="********" />
            </div>
            <small class="hint">min. 8 Zeichen, max. 20 Zeichen<br>min. 1 Großbuchstabe<br>min. 1 Zahl<br>min. 1 Sonderzeichen</small>
        </div>
        <div class="field">
            <label>Passwort wiederholen</label>
            <div class="input-wrapper">
                <span class="input-icon">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                        <path d="M240-80q-33 0-56.5-23.5T160-160v-400q0-33 23.5-56.5T240-640h40v-80q0-83 58.5-141.5T480-920q83 0 141.5 58.5T680-720v80h40q33 0 56.5 23.5T800-560v400q0 33-23.5 56.5T720-80H240Zm0-80h480v-400H240v400Zm296.5-143.5Q560-327 560-360t-23.5-56.5Q513-440 480-440t-56.5 23.5Q400-393 400-360t23.5 56.5Q447-280 480-280t56.5-23.5ZM360-640h240v-80q0-50-35-85t-85-35q-50 0-85 35t-35 85v80ZM240-160v-400 400Z"/>
                    </svg>
                </span>
                <input type="password" v-model="passwordRepeat" required placeholder="********" />
            </div>
        </div>
        <button type="submit" class="btn-primary" :disabled="loading">
            {{ loading ? 'Ihr Konto wird erstellt...' : 'Registrieren' }}
        </button>

        <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
    </form>
</template>

<script setup>
import { ref } from 'vue';
import api from '../api/api';

const email = ref('');
const password = ref('');
const passwordRepeat = ref('');
const loading = ref(false);
const errorMessage = ref('');
const emit = defineEmits(['registered']);

const validateEmail = (emailStr) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(emailStr);
};

const validatePassword = (pwdStr) => {
    if (pwdStr.length < 8 || pwdStr.length > 20) {
        return false;
    }
    if (!/[A-Z]/.test(pwdStr)) {
        return false;
    }
    if (!/[0-9]/.test(pwdStr)) {
        return false;
    }
    if (!/[!@#$%^&*(),.?":{}|<>]/.test(pwdStr)) {
        return false;
    }
    return true;
};

const handleRegister = async () => {
    errorMessage.value = '';

    if (!validateEmail(email.value)) {
        errorMessage.value = 'Bitte geben Sie eine gültige E-Mail-Adresse ein.';
        return;
    }
    if (!validatePassword(password.value)) {
        errorMessage.value = 'Das Passwort erfüllt die Sicherheitskriterien nicht.';
        return;
    }
    if (password.value !== passwordRepeat.value) {
        errorMessage.value = 'Die Passwörte stimmen nicht überein.';
        return;
    }

    loading.value = true;
    try {
        const response = await api.post('register/', {
            email: email.value,
            password: password.value,
        });

        // Ohne Token ist kein Konto entstanden, egal welchen Status die Antwort trug.
        // Sonst landete der String "undefined" im localStorage und der Nutzer bekäme
        // eine Erfolgsmeldung, obwohl er sich anschließend nicht anmelden kann.
        if (!response.data?.token) {
            errorMessage.value = response.data?.error
                ?? 'Registrierung ist fehlgeschlagen. Bitte versuchen Sie es später noch einmal.';
            return;
        }

        localStorage.setItem('auth_token', response.data.token);
        emit('registered');
    } catch (error) {
        if (error.response && error.response.data.error) {
            errorMessage.value = error.response.data.error;
        } else {
            errorMessage.value = 'Registrierung ist fehlgeschlagen. Bitte versuchen Sie es später noch einmal oder wenden Sie sich an den Support.';
        }
    } finally {
        loading.value = false;
    }
};
</script>

<style scoped>
.field { margin-bottom: 1.1rem; }
.field label { display: block; font-size: 13px; font-weight: 500; color: var(--color-text-muted); margin-bottom: 6px; }
.input-wrapper { display: flex; align-items: center; border: 1.5px solid var(--color-border); border-radius: 10px; padding: 0 14px; background: var(--color-bg-card); transition: border-color 0.2s; }
.input-wrapper:focus-within { border-color: var(--color-primary); }
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
.input-wrapper input { flex: 1; border: none; outline: none; padding: 11px 0; font-size: 14px; color: var(--color-text); background: transparent; }
.hint { display: block; color: var(--color-text-muted); font-size: 11px; margin-top: 8px; line-height: 1.3; padding-left: 8px;}
.btn-primary { width: 100%; padding: 13px; background: var(--color-primary); color: var(--color-on-primary); border: none; border-radius: 10px; font-size: 15px; font-weight: 600; cursor: pointer; margin-top: 0.5rem; transition: background 0.2s, transform 0.1s; }
.btn-primary:hover  { background: var(--color-primary-dark); }
.btn-primary:active { transform: scale(0.98); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: var(--color-danger); font-size: 13px; text-align: center; margin-top: 0.75rem; }
</style>