<script setup>
import { computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { goBack } from '@/composables/useBackNavigation';
import { usePageTitle } from '@/composables/usePageTitle';
import { useMap } from '@/composables/useMap.js';

const route = useRoute();
const router = useRouter();
const { resetToHome } = useMap();

// Heimatposition = der im Profil hinterlegte Standort; ohne gesetzten Standort
// greift innerhalb von resetToHome() der Standard-Fallback (siehe useMap.js)
const homeCenter = computed(() => {
  return (userStore.latitude !== null && userStore.longitude !== null)
    ? [userStore.latitude, userStore.longitude]
    : undefined;
});

const handleLogoClick = () => {
  closeMenus();
  resetToHome(homeCenter.value);
};
const { titleOverride } = usePageTitle();

const title = computed(() => titleOverride.value ?? route.meta.title ?? '');

const handleBack = () => goBack(router, route);
</script>

<template>
  <header class="app-header">
    <div class="app-header-inner">
      <RouterLink to="/map" class="app-logo" @click="handleLogoClick">
        <img src="@/assets/logo-light.png" alt="velotag logo" class="logo-img logo-img--light" />
        <img src="@/assets/logo-dark.png" alt="velotag logo" class="logo-img logo-img--dark" />
      </RouterLink>

      <nav class="app-nav">
        <RouterLink to="/rides" class="nav-link" @click="closeMenus">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
            <path d="M196-160q-82.33 0-139.17-57.17Q0-274.33 0-356.67 0-439 57.52-495.83q57.53-56.84 139.15-56.84 73 0 126.16 45.67Q376-461.33 388-392h42.67L352-613.33h-72V-680h192v66.67h-49.33l22 60.66h212L590-733.33H485.33V-800H586q24.67 0 42.5 12t26.17 34.67l73.33 200h36q81.34 0 138.67 56.99Q960-439.35 960-358.5q0 81.83-56.84 140.17Q846.32-160 764-160q-71.73 0-126.03-47t-67.3-118.33H388q-12 71-65.67 118.16Q268.67-160 196-160Zm0-66.67q45.67 0 79.17-28.16 33.5-28.17 45.5-70.5H204V-392h116.67q-12-42-45.84-68-33.83-26-78.16-26-54.34 0-92.17 37.5t-37.83 91.83q0 54.17 37.5 92.09 37.5 37.91 91.83 37.91ZM502-392h69.33q4.34-23 14.84-48.33 10.5-25.34 28.5-45.67H468l34 94Zm262 165.33q54.33 0 91.83-37.91 37.5-37.92 37.5-92.09 0-54.33-37.5-91.83T764-486h-12l39.33 110.67-62.66 22-41.34-110q-26 17-39.33 45.33-13.33 28.33-13.33 61.33 0 54.17 37.5 92.09 37.5 37.91 91.83 37.91Zm-570-130Zm570 0Z"/>
          </svg>
          <span>Fahrten</span>
        </RouterLink>

        <div
          class="nav-dropdown"
          ref="groupsMenuRef"
          @mouseenter="openGroupsMenu"
          @mouseleave="scheduleCloseGroupsMenu"
        >
          <button type="button" class="nav-link nav-link--button" :class="{ open: showGroupsMenu }" @click="toggleGroupsMenu">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
              <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
              <circle cx="9" cy="7" r="4"/>
              <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
              <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
            </svg>
            <span>Gruppen</span>
            <svg class="chevron" viewBox="0 -960 960 960" fill="currentColor" :class="{ rotated: showGroupsMenu }">
              <path d="M480-344 240-584l56-56 184 184 184-184 56 56-240 240Z"/>
            </svg>
          </button>
        </div>

        <!-- Teleport: .app-nav scrollt horizontal (overflow-x: auto), was laut CSS-Spezifikation
             automatisch auch overflow-y auf 'auto' erzwingt - eine absolut positionierte Liste
             würde dort also abgeschnitten statt sichtbar aufzuklappen. Deshalb wird sie hier
             gerendert und über groupsDropdownStyle (aus getBoundingClientRect) frei positioniert. -->
        <Teleport to="body">
          <ul
            v-if="showGroupsMenu"
            ref="groupsDropdownRef"
            class="nav-dropdown-list"
            :style="groupsDropdownStyle"
            @mouseenter="openGroupsMenu"
            @mouseleave="scheduleCloseGroupsMenu"
          >
            <li>
              <RouterLink
                v-if="favoriteGroup"
                :to="`/group/${favoriteGroup.id}`"
                class="nav-dropdown-item nav-dropdown-item--favorite"
                @click="closeMenus"
              >
                <svg class="favorite-star" xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
                  <path d="m233-120 65-281L80-590l288-25 112-265 112 265 288 25-218 189 65 281-247-149-247 149Z"/>
                </svg>
                {{ favoriteGroup.name }}
              </RouterLink>
              <span v-else class="nav-dropdown-empty">Keine Favoritengruppe</span>
            </li>
            <li class="nav-dropdown-divider" role="separator"></li>
            <li>
              <RouterLink to="/group" class="nav-dropdown-item" @click="closeMenus">Zu den Gruppen</RouterLink>
            </li>
            <li>
              <button type="button" class="nav-dropdown-item nav-dropdown-item--create" @click="openCreateGroup">
                + Neue Gruppe erstellen
              </button>
            </li>
          </ul>
        </Teleport>

        <RouterLink to="/group/invites" class="nav-link" @click="closeMenus">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <rect x="3" y="5" width="18" height="14" rx="2"/>
            <path d="m3 7 9 6 9-6"/>
          </svg>
          <span>Einladungen</span>
        </RouterLink>

        <RouterLink to="/settings" class="nav-link" @click="closeMenus">
          <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
            <circle cx="12" cy="12" r="3"/>
            <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
          </svg>
        </button>

        <ul v-if="showProfileMenu" class="profile-dropdown-list">
          <li>
            <RouterLink :to="{ name: 'user-profile', params: { id: userStore.id } }" class="profile-dropdown-item" @click="closeMenus">Zum Profil</RouterLink>
          </li>
          <li class="profile-dropdown-divider" role="separator"></li>
          <li>
            <button type="button" class="profile-dropdown-item profile-dropdown-item--danger" @click="handleLogout">Abmelden</button>
          </li>
        </ul>
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
}
.back-button:hover {
  background-color: var(--color-bg-page, #f0f2f5);
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
