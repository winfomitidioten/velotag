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
    background-color: rgba(15, 23, 42, 0.6); /* Moderneres, kühleres Overlay */
    backdrop-filter: blur(4px); /* Schicker Blur-Effekt für den Hintergrund */
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
    padding: 40px 32px;
    border-radius: 20px; /* Schön abgerundet, einheitlich mit dem GPX-Upload-Modal */
    text-align: center;
    position: relative;
    max-height: 85vh;
    overflow-y: auto;
    box-sizing: border-box;
    box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 8px 10px -6px rgba(0, 0, 0, 0.1);
}

/* Slot-Inhalt: Überschrift einheitlich stylen, ohne dass jedes Modal sie selbst definieren muss */
:slotted(h2) {
    margin: 0;
    color: #1e293b;
    font-size: 1.5rem;
    font-weight: 700;
    text-align: center;
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
    top: 20px;
    right: 20px;
    background-color: #f1f5f9; /* Dezentes Grau statt auffälligem Grün */
    color: #64748b;
    border: none;
    width: 36px;
    height: 36px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    border-radius: 50%;
    transition: all 0.2s ease;
    z-index: 3000;
}

.popup-close-button:hover {
    background-color: #e2e8f0;
    color: #0f172a;
    transform: rotate(90deg); /* Kleine, spielerische Animation beim Hover */
}

.popup-close-button svg {
    width: 20px;
    height: 20px;
    color: #3db897;
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
