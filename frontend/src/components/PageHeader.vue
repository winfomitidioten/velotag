<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { usePageTitle } from '@/composables/usePageTitle';

// Titel kommt aus derselben Quelle wie im mobilen AppHeader (route.meta.title,
// überschreibbar per usePageTitle) - kein eigener Prop nötig, damit Titel auf
// Mobile und Desktop garantiert übereinstimmen.
const route = useRoute();
const { titleOverride } = usePageTitle();
const title = computed(() => titleOverride.value ?? route.meta.title ?? '');
</script>

<template>
    <header class="page-header">
        <div class="header-inner">
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
    /* Bleibt direkt unter der fixierten DesktopNavBar stehen */
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
