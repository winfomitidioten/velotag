<script setup>
// Ersatz für window.alert(): kurze, nicht-blockierende Erfolgs-/Fehlermeldung.
// Wird einmalig in App.vue gerendert; jede Komponente löst sie über useToast().showToast() aus.
import { useToast } from '@/composables/useToast';

const { message, type, visible } = useToast();
</script>

<template>
    <Teleport to="body">
        <transition name="toast-fade">
            <div v-if="visible" class="app-toast" :class="`app-toast-${type}`" role="status">
                {{ message }}
            </div>
        </transition>
    </Teleport>
</template>

<style scoped>
.app-toast {
    position: fixed;
    left: 50%;
    bottom: calc(env(safe-area-inset-bottom, 0px) + 5.5rem);
    transform: translateX(-50%);
    max-width: min(90vw, 24rem);
    padding: 0.85rem 1.25rem;
    border-radius: var(--radius-md);
    color: white;
    font-size: 0.9rem;
    font-weight: 600;
    text-align: center;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
    z-index: 10004; /* über ConfirmDialog (10003), BaseModal und Strava-Picker (10002) */
}

.app-toast-success {
    background-color: var(--color-primary, #3db897);
}

.app-toast-error {
    background-color: #e53e3e;
}

.toast-fade-enter-active,
.toast-fade-leave-active {
    transition: opacity 0.2s ease, transform 0.2s ease;
}
.toast-fade-enter-from,
.toast-fade-leave-to {
    opacity: 0;
    transform: translate(-50%, 8px);
}

@media (min-width: 480px) {
    .app-toast {
        bottom: 2rem;
    }
}
</style>
