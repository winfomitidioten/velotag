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
    /* Bleibt direkt unter dem fixierten, globalen AppHeader stehen */
    top: calc(var(--safe-top, 0px) + var(--app-header-height));
    margin-top: calc(var(--safe-top, 0px) + var(--app-header-height));
    z-index: 100;
    background: var(--color-bg-page);
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

/* Breite = Zurück-Button (44px); Hamburger ist mit dem AppHeader entfallen */
.header-left {
    width: 44px;
    flex-shrink: 0;
}

.header-title {
    position: absolute;
    left: 50%;
    transform: translateX(-50%);
    max-width: 55%;
    font-size: 1.15rem;
    font-weight: 600;
    color: var(--color-text);
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
    min-width: calc(88px + 0.75rem);
    justify-content: flex-end;
}

</style>
