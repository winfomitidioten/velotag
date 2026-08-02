<script setup>
import { computed } from 'vue';
import { useRoute } from 'vue-router';
import { useUserStore } from '@/store/userStore';

const route = useRoute();
const userStore = useUserStore();

const userInitials = computed(() => userStore.initials || '?');
const userProfileImage = computed(() => userStore.profileImage || '');

// Manuelle Aktiv-Ermittlung statt active-class: /group/:id und /settings sind
// eigene Top-Level-Routen (kein Kind von /group bzw. /profile), daher würde
// vue-router den zugehörigen Tab sonst nicht als aktiv markieren, obwohl man
// sich inhaltlich noch "in" Gruppen bzw. Profil befindet.
const activeTab = computed(() => {
  if (route.name === 'map') return 'map';
  if (route.name === 'rides') return 'rides';
  if (route.name === 'group' || route.name === 'group-detail') return 'group';
  if (route.name === 'group-invites') return 'group-invites';
  if (route.name === 'profile' || route.name === 'settings') return 'profile';
  return null;
});
</script>

<template>
  <nav class="app-tab-bar">
    <RouterLink to="/map" class="tab-item" :class="{ active: activeTab === 'map' }">
      <span class="tab-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
          <path d="M480-480q33 0 56.5-23.5T560-560q0-33-23.5-56.5T480-640q-33 0-56.5 23.5T400-560q0 33 23.5 56.5T480-480Zm0 294q122-112 181-203.5T720-552q0-109-69.5-178.5T480-800q-101 0-170.5 69.5T240-552q0 71 59 162.5T480-186Zm0 106Q319-217 239.5-334.5T160-552q0-150 96.5-249T480-880q127 0 223.5 99T800-552q0 100-79.5 217.5T480-80Zm0-480Z"/>
        </svg>
      </span>
      <span class="tab-label">Karte</span>
    </RouterLink>

    <RouterLink to="/rides" class="tab-item" :class="{ active: activeTab === 'rides' }">
      <span class="tab-icon">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
          <path d="M196-160q-82.33 0-139.17-57.17Q0-274.33 0-356.67 0-439 57.52-495.83q57.53-56.84 139.15-56.84 73 0 126.16 45.67Q376-461.33 388-392h42.67L352-613.33h-72V-680h192v66.67h-49.33l22 60.66h212L590-733.33H485.33V-800H586q24.67 0 42.5 12t26.17 34.67l73.33 200h36q81.34 0 138.67 56.99Q960-439.35 960-358.5q0 81.83-56.84 140.17Q846.32-160 764-160q-71.73 0-126.03-47t-67.3-118.33H388q-12 71-65.67 118.16Q268.67-160 196-160Zm0-66.67q45.67 0 79.17-28.16 33.5-28.17 45.5-70.5H204V-392h116.67q-12-42-45.84-68-33.83-26-78.16-26-54.34 0-92.17 37.5t-37.83 91.83q0 54.17 37.5 92.09 37.5 37.91 91.83 37.91ZM502-392h69.33q4.34-23 14.84-48.33 10.5-25.34 28.5-45.67H468l34 94Zm262 165.33q54.33 0 91.83-37.91 37.5-37.92 37.5-92.09 0-54.33-37.5-91.83T764-486h-12l39.33 110.67-62.66 22-41.34-110q-26 17-39.33 45.33-13.33 28.33-13.33 61.33 0 54.17 37.5 92.09 37.5 37.91 91.83 37.91Zm-570-130Zm570 0Z"/>
        </svg>
      </span>
      <span class="tab-label">Fahrten</span>
    </RouterLink>

    <RouterLink to="/group" class="tab-item" :class="{ active: activeTab === 'group' }">
      <span class="tab-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
          <circle cx="9" cy="7" r="4"/>
          <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
          <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
        </svg>
      </span>
      <span class="tab-label">Gruppen</span>
    </RouterLink>

    <RouterLink to="/group/invites" class="tab-item" :class="{ active: activeTab === 'group-invites' }">
      <span class="tab-icon">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
          <rect x="3" y="5" width="18" height="14" rx="2"/>
          <path d="m3 7 9 6 9-6"/>
        </svg>
      </span>
      <span class="tab-label">Einladungen</span>
    </RouterLink>

    <RouterLink to="/profile" class="tab-item" :class="{ active: activeTab === 'profile' }">
      <span class="tab-icon tab-icon--avatar">
        <span class="avatar">
          <img v-if="userProfileImage" :src="userProfileImage" alt="Profilbild" class="avatar-img" />
          <span v-else>{{ userInitials }}</span>
        </span>
      </span>
      <span class="tab-label">Profil</span>
    </RouterLink>
  </nav>
</template>

<style scoped>
.app-tab-bar {
  position: fixed;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 10000;
  display: flex;
  align-items: stretch;
  height: calc(var(--tab-bar-height) + var(--safe-bottom, 0px));
  padding-bottom: var(--safe-bottom, 0px);
  background-color: rgba(var(--color-bg-card-rgb));
  border-top: 1px solid var(--color-border);
}

.tab-item {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 2px;
  text-decoration: none;
  color: var(--color-text-muted, #888);
}

.tab-icon {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 48px;
  height: 34px;
  border-radius: 14px;
  transition: background-color 0.2s ease, color 0.2s ease;
}
.tab-icon svg {
  width: 30px;
  height: 30px;
}

.tab-label {
  font-size: 0.68rem;
  font-weight: 600;
  line-height: 1;
}

/* M3-artiger Pill-Indikator hinter dem aktiven Icon */
.tab-item.active .tab-icon {
  background-color: rgba(var(--color-primary-rgb), 0.15);
  color: var(--color-primary);
}
.tab-item.active .tab-label {
  color: var(--color-primary);
}

.tab-icon--avatar {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  overflow: visible;
}
.tab-item.active .tab-icon--avatar {
  background-color: transparent;
  box-shadow: 0 0 0 2px var(--color-primary);
}

.avatar {
  width: 26px;
  height: 26px;
  border-radius: 50%;
  background: var(--color-primary);
  color: var(--color-on-primary);
  font-weight: 600;
  font-size: 0.68rem;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}
.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
</style>
