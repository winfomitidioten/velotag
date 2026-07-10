<script setup>
import { ref, computed } from 'vue';

const props = defineProps({
    photos: { type: Array, required: true }
});
const emit = defineEmits(['close']);

const activeIndex = ref(null);

const activePhoto = computed(() =>
    activeIndex.value !== null ? props.photos[activeIndex.value] : null
);

const openSlide = (index) => {
    activeIndex.value = index;
};

const backToGrid = () => {
    activeIndex.value = null;
};

const showPrev = () => {
    activeIndex.value = (activeIndex.value - 1 + props.photos.length) % props.photos.length;
};

const showNext = () => {
    activeIndex.value = (activeIndex.value + 1) % props.photos.length;
};
</script>

<template>
    <div class="popup">
        <div class="popup-content">
            <button @click="$emit('close')" class="popup-close-button" aria-label="Schließen">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
                    <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/>
                </svg>
            </button>

            <!-- Grid-Ansicht für die Fotos an einem Punkt -->
            <template v-if="activePhoto === null">
                <h2>{{ photos.length > 1 ? `${photos.length} Fotos` : '1 Foto' }}</h2>
                <div class="gallery-grid">
                    <button
                        v-for="(photo, index) in photos"
                        :key="photo.id"
                        type="button"
                        class="gallery-grid-item"
                        @click="openSlide(index)"
                    >
                        <img :src="photo.image" :alt="photo.description || 'Foto'" />
                    </button>
                </div>
            </template>

            <!-- Slide-Ansicht für einzelne Fotos (mit Vor und Zurück) -->
            <template v-else>
                <button type="button" class="gallery-back-button" @click="backToGrid" aria-label="Zurück zur Übersicht">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                        <path d="M560-240 320-480l240-240 56 56-184 184 184 184-56 56Z"/>
                    </svg>
                    <span>Übersicht</span>
                </button>

                <div class="gallery-slide">
                    <button v-if="photos.length > 1" type="button" class="gallery-nav gallery-nav-prev" @click="showPrev" aria-label="Vorheriges Foto">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="15 6 9 12 15 18" />
                        </svg>
                    </button>

                    <img :src="activePhoto.image" :alt="activePhoto.description || 'Foto'" class="gallery-slide-image" />

                    <button v-if="photos.length > 1" type="button" class="gallery-nav gallery-nav-next" @click="showNext" aria-label="Nächstes Foto">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <polyline points="9 6 15 12 9 18" />
                        </svg>
                    </button>
                </div>

                <p v-if="activePhoto.description" class="gallery-description">{{ activePhoto.description }}</p>
                <p class="gallery-counter">{{ activeIndex + 1 }} / {{ photos.length }}</p>
            </template>
        </div>
    </div>
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
    align-items: center;
    z-index: 1001;
}

.popup-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
    position: relative;
    width: min(480px, 92vw);
    max-height: 85vh;
    overflow-y: auto;
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

.gallery-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 8px;
    margin-top: 15px;
}

.gallery-grid-item {
    padding: 0;
    border: none;
    background: none;
    cursor: pointer;
    aspect-ratio: 1 / 1;
}

.gallery-grid-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    border-radius: 8px;
}

.gallery-back-button {
    display: flex;
    align-items: center;
    gap: 4px;
    margin: 0 auto 10px 0;
    padding: 6px 10px 6px 6px;
    border: none;
    border-radius: 20px;
    background-color: var(--color-bg-page, #f0f2f5);
    color: var(--color-text, #1a1a1a);
    cursor: pointer;
    font-size: 13px;
}

.gallery-back-button svg {
    width: 20px;
    height: 20px;
}

.gallery-slide {
    display: flex;
    align-items: center;
    gap: 8px;
}

.gallery-slide-image {
    flex: 1;
    max-height: 60vh;
    width: 100%;
    object-fit: contain;
    border-radius: 8px;
    background-color: #000;
}

.gallery-nav {
    flex-shrink: 0;
    width: 36px;
    height: 36px;
    border-radius: 50%;
    border: none;
    background-color: var(--color-bg-page, #f0f2f5);
    color: var(--color-text, #1a1a1a);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
}

.gallery-nav svg {
    width: 20px;
    height: 20px;
}

.gallery-description {
    margin: 12px 0 0;
    font-size: 14px;
    color: var(--color-text, #1a1a1a);
}

.gallery-counter {
    margin: 4px 0 0;
    font-size: 12px;
    color: var(--color-text-muted, #888888);
}
</style>