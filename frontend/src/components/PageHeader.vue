<script setup>
defineProps({
    title: {
        type: String,
        required: true,
    },
});
</script>

<template>
    <header class="page-header">
        <div class="header-inner">
            <!-- Reserviert den Platz für Hamburger + Zurück-Button -->
            <div class="header-left"></div>
            <span class="header-title">{{ title }}</span>
            <div class="header-right">
                <slot />
            </div>
        </div>
    </header>
</template>

<style scoped>
.page-header {
    position: sticky;
    top: 0;
    z-index: 100;
    background: #f8f9fa;
    padding-top: var(--safe-top, 0px);
    flex-shrink: 0;
}

.header-inner {
    position: relative;
    display: flex;
    align-items: center;
    justify-content: space-between;
    height: 56px;
    padding: 0 1rem;
}

/* Breite = Hamburger (44px) + Lücke (0.75rem) + Zurück-Button (44px) */
.header-left {
    width: calc(88px + 0.75rem);
    flex-shrink: 0;
}

.header-title {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    max-width: 55%;
    font-size: 1.05rem;
    font-weight: 600;
    color: #1a1a1a;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
    pointer-events: none;
}

.header-right {
    flex-shrink: 0;
    display: flex;
    align-items: center;
    gap: 0.5rem;
    margin-left: auto;
}
</style>
