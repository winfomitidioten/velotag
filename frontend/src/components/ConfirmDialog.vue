<script setup>
defineProps({
    title: { type: String, default: 'Bist du sicher?' },
    message: { type: String, default: '' },
    confirmLabel: { type: String, default: 'Bestätigen' },
    cancelLabel: { type: String, default: 'Abbrechen' },
    danger: { type: Boolean, default: false },   // rote statt grüner Bestätigen-Button
    busy: { type: Boolean, default: false }
});
defineEmits(['confirm', 'cancel']);
</script>

<template>
    <!-- Teleport, damit der Dialog immer über dem Modal liegt, aus dem er geöffnet wurde -->
    <Teleport to="body">
        <div class="confirm-overlay" @click.self="$emit('cancel')">
            <div class="confirm-box" role="alertdialog" aria-modal="true">
                <h3 class="confirm-title">{{ title }}</h3>
                <p v-if="message" class="confirm-message">{{ message }}</p>

                <div class="confirm-actions">
                    <button type="button" class="confirm-button confirm-cancel" :disabled="busy" @click="$emit('cancel')">
                        {{ cancelLabel }}
                    </button>
                    <button type="button" class="confirm-button" :class="danger ? 'confirm-danger' : 'confirm-primary'" :disabled="busy" @click="$emit('confirm')">
                        {{ confirmLabel }}
                    </button>
                </div>
            </div>
        </div>
    </Teleport>
</template>

<style scoped>
.confirm-overlay {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1100; /* über den Modals (1001) */
}

.confirm-box {
    background-color: white;
    border-radius: 12px;
    padding: 24px 20px 20px;
    width: min(340px, 88vw);
    text-align: center;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.2);
}

.confirm-title {
    margin: 0;
    font-size: 17px;
    color: var(--color-text, #1a1a1a);
}

.confirm-message {
    margin: 8px 0 0;
    font-size: 14px;
    line-height: 1.4;
    color: var(--color-text-muted, #888888);
}

.confirm-actions {
    display: flex;
    gap: 8px;
    margin-top: 20px;
}

.confirm-button {
    flex: 1;
    padding: 11px;
    border-radius: 8px;
    border: 1px solid transparent;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: background-color 0.15s;
}

.confirm-button:disabled {
    opacity: 0.5;
    cursor: not-allowed;
}

.confirm-cancel {
    background-color: white;
    border-color: var(--color-border, #e5e7eb);
    color: var(--color-text, #1a1a1a);
}

.confirm-primary {
    background-color: var(--color-primary, #3db897);
    color: white;
}

.confirm-primary:hover:not(:disabled) {
    background-color: var(--color-primary-dark, #35a684);
}

.confirm-danger {
    background-color: #e53e3e;
    color: white;
}

.confirm-danger:hover:not(:disabled) {
    background-color: #c53030;
}
</style>
