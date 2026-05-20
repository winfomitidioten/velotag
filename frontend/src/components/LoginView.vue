<template>
    <div class="login-container">
        <h2>Login</h2>
        <form @submit.prevent="handleLogin">
            <div class="form">
                <label>E-Mail:
                    <input type="email" v-model="email" required placeholder="max.mustermann@beispiel.com">
                </label>
            </div>
            <div class="form">
                <label>Passwort:
                    <input type="password" v-model="password" required placeholder="**********">
                </label>
            </div>

            <button type="submit" :disabled="loading">
                {{ loading ? 'Lädt...' : 'Einloggen' }}
            </button>

            <p v-if="errorMessage" class="error">{{ errorMessage }}</p>
        </form>
    </div>
</template>

<script setup>
import { ref } from 'vue';
import api from '@/api/api';

const email = ref('');
const password = ref('');
const loading = ref(false);
const errorMessage = ref('');

const handleLogin = async () => {
    loading.value = true;
    errorMessage.value = '';

    try {
        const payload = {
        username: email.value,
        password: password.value,
    };

    const response = await api.post('login/', payload);

    const token = response.data.token;
    localStorage.setItem('auth_token', token);

    } catch (error) {
        console.error('Fehler beim Login:', error);
        if (error.response) {
            const data = error.response.data;

            if (data.non_field_errors) {
                errorMessage.value = 'E-Mail oder Passwort ist falsch!';
            } else if (data.detail) {
                errorMessage.value = data.detail;
            } else {
                errorMessage.value = 'Ungültige Anmeldedaten.'
            }
        } else if (error.request) {
            errorMessage.value = 'Es konnte keine Verbindung zum Server hergestellt werden.'
        } else {
            errorMessage.value = 'Ein unerwarteter Fehler ist aufgetreten.'
        }
    } finally {
        loading.value = false;
    }
}
</script>
