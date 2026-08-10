<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { goBack } from '@/composables/useBackNavigation';
import { usePageTitle } from '@/composables/usePageTitle';

const route = useRoute();
const router = useRouter();
const { titleOverride } = usePageTitle();

const title = computed(() => titleOverride.value ?? route.meta.title ?? '');

const handleBack = () => goBack(router, route);
</script>

<template>
  <header class="app-header">
    <div class="app-header-inner">
      <div class="header-left">
        <button
          v-if="route.meta.showBack"
          type="button"
          class="back-button"
          @click="handleBack"
          aria-label="Zurück zur vorherigen Seite"
        >
          <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
            <path d="M560-240 320-480l240-240 56 56-184 184 184 184-56 56Z"/>
          </svg>
        </button>
      </div>

      <span v-if="!route.meta.hideTitle" class="header-title">{{ title }}</span>

      <!-- Teleport-Ziel für seitenspezifische Aktions-Buttons (z.B. "Gruppe
           löschen", Einstellungen-Icon auf dem Profil) - existiert immer,
           da AppHeader vor RouterView gemountet wird -->
      <div id="app-header-actions" class="header-right"></div>
    </div>
  </header>
</template>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  /* Muss über Karte.vues schwebenden Controls liegen (z-index 9999) -
     ein z-index weiter unten reicht dafür nicht, da er nur innerhalb des
     hier durch position:fixed + z-index erzeugten Stacking-Contexts zählt */
  z-index: 10000;
  background: var(--color-bg-card);
  padding-top: var(--safe-top, 0px);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.app-header-inner {
  height: var(--app-header-height);
  display: flex;
  align-items: center;
  padding: 0 0.5rem;
}

.header-left {
  width: 48px;
  flex-shrink: 0;
  display: flex;
  align-items: center;
}

.back-button {
  width: 44px;
  height: 44px;
  padding: 0;
  border: none;
  background: none;
  color: var(--color-primary);
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: var(--radius-md);
  -webkit-tap-highlight-color: transparent;
}
/* Nur auf Geräten mit echtem Zeiger: auf Touch löst ein Tap :hover aus und die
   graue Fläche bleibt nach dem Antippen sichtbar hängen. */
@media (hover: hover) {
  .back-button:hover {
    background-color: var(--color-bg-page);
  }
}

.header-title {
  flex: 1;
  min-width: 0;
  text-align: center;
  font-size: 1.05rem;
  font-weight: 600;
  color: var(--color-text);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.header-right {
  flex-shrink: 0;
  min-width: 48px;
  /* Immer fest rechtsbündig, unabhängig davon ob .header-title Inhalt hat */
  margin-left: auto;
  display: flex;
  align-items: center;
  justify-content: flex-end;
  gap: 0.5rem;
}
</style>
