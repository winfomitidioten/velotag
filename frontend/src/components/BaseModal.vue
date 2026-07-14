<script setup>
import { onMounted, onUnmounted } from 'vue';

const props = defineProps({
    // 'center' = klassisches Fenster in der Bildschirmmitte, 'sheet' = fährt von unten hoch
    variant: { type: String, default: 'center' },
    // Breite der Box; bei 'sheet' wirkt der Wert als max-width
    width: { type: String, default: 'min(420px, 82vw)' },
    // Solange true, lässt sich das Fenster nicht schließen (z.B. während eines laufenden Uploads)
    busy: { type: Boolean, default: false },
    showClose: { type: Boolean, default: true }
});
const emit = defineEmits(['close']);

// Eine einzige Schließen-Geste: X-Button, Klick auf den Hintergrund und Escape landen alle hier
const requestClose = () => {
    if (!props.busy) emit('close');
};

const onKeydown = (event) => {
    if (event.key === 'Escape') requestClose();
};

onMounted(() => document.addEventListener('keydown', onKeydown));
onUnmounted(() => document.removeEventListener('keydown', onKeydown));
</script>

<template>
    <!-- Teleport to body: das Modal hängt damit immer ganz oben im DOM und wird nicht
         vom overflow oder z-index seines Eltern-Elements beschnitten -->
    <Teleport to="body">
        <div class="popup" :class="`popup-${variant}`" @click.self="requestClose">
            <div
                class="popup-content"
                :style="variant === 'sheet' ? { maxWidth: width } : { width }"
            >
                <button v-if="showClose" @click="requestClose" class="popup-close-button" aria-label="Schließen" title="Schließen">
                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
                        <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/>
                    </svg>
                </button>

                <slot />
            </div>
        </div>
    </Teleport>
</template>

<style scoped>
.popup {
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5);
    display: flex;
    justify-content: center;
    z-index: 1001;
    animation: fadeIn 0.2s ease-out;
}

.popup-center {
    align-items: center;
}

.popup-sheet {
    align-items: flex-end; /* Box klebt am unteren Bildschirmrand */
}

.popup-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
    position: relative;
    max-height: 85vh;
    overflow-y: auto;
    box-sizing: border-box;
}

.popup-sheet .popup-content {
    width: 100%;
    padding: 24px 24px 40px 24px; /* Mehr Platz unten, z.B. für Wischgesten auf dem Smartphone */
    border-radius: 24px 24px 0 0;  /* Nur die oberen Ecken abrunden */
    box-shadow: 0 -5px 15px rgba(0, 0, 0, 0.2);
    animation: slideUp 0.3s cubic-bezier(0.16, 1, 0.3, 1) forwards;
}

.popup-close-button {
    position: absolute;
    top: 16px;
    right: 16px;
    background-color: var(--color-primary, #3db897);
    border: none;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: white;
    border-radius: 50%;
    transition: background-color 0.15s;
    z-index: 3000;
}

.popup-close-button:hover {
    background-color: var(--color-primary-dark, #35a684);
}

.popup-close-button svg {
    width: 24px;
    height: 24px;
}

@keyframes slideUp {
    from { transform: translateY(100%); }
    to { transform: translateY(0); }
}

@keyframes fadeIn {
    from { opacity: 0; }
    to { opacity: 1; }
}
</style>
