<template>
    <form @submit.prevent="handleRegister">
        <div class="field-row">
            <div class="field">
                <label>Vorname</label>
                <div class="input-wrapper">
                    <span class="input-icon"> </span>
                    <input type="text" v-model="firstName" required placeholder="Max" />
                </div>
            </div>
            <div class="field">
                <label>Nachname</label>
                <div class="input-wrapper">
                    <span class="input-icon"> </span>
                    <input type="text" v-model="lastName" required placeholder="Mustermann" />
                </div>
            </div>
        </div>
        <div class="field">
            <label>E-Mail</label>
            <div class="input-wrapper">
                <span class="input-icon"> </span>
                <input type="email" v-model="email" required placeholder="max.mustermann@velotag.de" />
            </div>
        </div>
        <div class="field">
            <label>Passwort</label>
            <div class="input-wrapper">
                <span class="input-icon"> </span>
                <input type="password" v-model="password" required placeholder="********" />
            </div>
            <small class="hint">min. 8 Zeichen, max. 20 Zeichen<br>min. 1 Großbuchstabe<br>min. 1 Zahl<br>min. 1 Sonderzeichen</small>
        </div>
        <div class="field">
            <label>Passwort wiederholen</label>
            <div class="input-wrapper">
                <span class="input-icon"> </span>
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
import { useRouter } from 'vue-router';
import api from '../api/api';

const router = useRouter();

const firstName = ref('');
const lastName = ref('');
const email = ref('');
const password = ref('');
const passwordRepeat = ref('');
const loading = ref(false);
const errorMessage = ref('');

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
            first_name: firstName.value,
            last_name: lastName.value,
            email: email.value,
            password: password.value,
        });

        localStorage.setItem('auth_token', response.data.token);
        router.push('/login');
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
.field-row {
    display: flex;
    gap: 12px;
}
.field-row .field {
    flex: 1;
}
.field { margin-bottom: 1.1rem; }
.field label { display: block; font-size: 13px; font-weight: 500; color: #555; margin-bottom: 6px; }
.input-wrapper { display: flex; align-items: center; border: 1.5px solid #e5e7eb; border-radius: 10px; padding: 0 14px; background: #fff; transition: border-color 0.2s; }
.input-wrapper:focus-within { border-color: var(--color-primary); }
.input-icon { font-size: 15px; margin-right: 10px; color: #aaa; }
.input-wrapper input { flex: 1; border: none; outline: none; padding: 11px 0; font-size: 14px; color: #1a1a1a; background: transparent; }
.hint { display: block; color: #888; font-size: 11px; margin-top: 4px; line-height: 1.3; }
.btn-primary { width: 100%; padding: 13px; background: var(--color-primary); color: #fff; border: none; border-radius: 10px; font-size: 15px; font-weight: 600; cursor: pointer; margin-top: 0.5rem; transition: background 0.2s, transform 0.1s; }
.btn-primary:hover  { background: var(--color-primary-dark); }
.btn-primary:active { transform: scale(0.98); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }
.error { color: #e53e3e; font-size: 13px; text-align: center; margin-top: 0.75rem; }
</style>