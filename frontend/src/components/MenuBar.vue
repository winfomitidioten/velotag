<template>
  <button class="menu-button" @click="toggleMenu" aria-label="Menü öffnen">
    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#e3e3e3">
      <path d="M120-240v-80h720v80H120Zm0-200v-80h720v80H120Zm0-200v-80h720v80H120Z"/>
    </svg>
  </button>

  <transition name="fade">
    <div v-if="isOpen" class="overlay" @click="closeMenu"></div>
  </transition>

  <aside class="sidebar" :class="{ 'is-open': isOpen }">
    <!-- Header: Logo & Close -->
    <div class="sidebar-header">
      <img src="@/assets/logo.png" alt="velotag logo" class="logo" />
      <button class="close-button" @click="closeMenu" aria-label="Menü schließen">
        <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#000000">
          <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/>
        </svg>
      </button>
    </div>

    <!-- Profil-Karte -->
    <div class="profile-card">
      <div class="avatar">
        <img v-if="userProfileImage" :src="userProfileImage" alt="Profilbild" class="avatar-img"/>
        <span v-else>{{ userInitials }}</span>
      </div>
      <div class="user-info">
        <span class="user-name">{{ userName}}</span>
        <span class="user-email">{{ userEmail }}</span>
      </div>
    </div>

    <!-- Navigation -->
    <nav>
      <ul>
        <li>
          <RouterLink to="/profile" @click="closeMenu" class="nav-item">
            <span class="icon-wrap icon-green">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
            </span>
            <span class="nav-label">Profil</span>
          </RouterLink>
        </li>
        <li class="nav-divider"></li>
        <li>
          <RouterLink to="/group" @click="closeMenu" class="nav-item">
            <span class="icon-wrap icon-green">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"/>
                <circle cx="9" cy="7" r="4"/>
                <path d="M23 21v-2a4 4 0 0 0-3-3.87"/>
                <path d="M16 3.13a4 4 0 0 1 0 7.75"/>
              </svg>
            </span>
            <span class="nav-label">Gruppen</span>
          </RouterLink>
        </li>
        <li class="nav-divider"></li>
        <li>
          <!-- TODO: Route einfügen wenn Einstellungen-Seite bereit ist -->
          <RouterLink to="#" @click="closeMenu" class="nav-item">
            <span class="icon-wrap icon-blue">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
              </svg>
            </span>
            <span class="nav-label">Einstellungen</span>
          </RouterLink>
        </li>
        <li class="nav-divider"></li>
        <li>
          <!-- TODO: Logout-Logik (Store leeren, Session beenden) einbauen -->
          <button @click="handleLogout" class="nav-item nav-item--button">
            <span class="icon-wrap icon-red">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"/>
                <polyline points="16 17 21 12 16 7"/>
                <line x1="21" y1="12" x2="9" y2="12"/>
              </svg>
            </span>
            <span class="nav-label">Log-Out</span>
          </button>
        </li>
      </ul>
    </nav>

    <!-- Footer Stats -->
    <!-- TODO: rideCount und totalKm später noch einfügen -->
    <div class="sidebar-footer">
      <div class="stat">
        <span class="stat-value">{{ rideCount }}</span>
        <span class="stat-label">Rides</span>
      </div>
      <div class="stat">
        <span class="stat-value">{{ totalKm }}</span>
        <span class="stat-label">km</span>
      </div>
    </div>
  </aside>
</template>

<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { useUserStore } from '@/store/userStore';

const isOpen = ref(false);

const userStore = useUserStore();

const userName = computed(() => `${userStore.firstname} ${userStore.lastname}`.trim() || 'Kein Name');
const userEmail = computed(() => userStore.mail || '');
const userInitials = computed(() => userStore.initials || '?');
const userProfileImage = computed(() => userStore.profileImage || '');

// TODO: Durch echte Statistiken aus Store/API ersetzen
const rideCount = ref();
const totalKm = ref();

// Logout
const router = useRouter();

const handleLogout = async () => {
  localStorage.removeItem('auth_token');
  userStore.clearUser();
  closeMenu();
  await router.push('/login');
};

const toggleMenu = () => { isOpen.value = !isOpen.value; };
const closeMenu = () => { isOpen.value = false; };
</script>

<style scoped>
/* Hamburger Button */
.menu-button {
  position: fixed;
  top: 1rem;
  left: 1rem;
  z-index: 1010;
  display: flex;
  align-items: center;
  justify-content: center;
  width: 44px;
  height: 44px;
  font-size: 1.4rem;
  cursor: pointer;
  border: none;
  border-radius: var(--radius-lg);
  background: var(--color-primary);
  color: #ffffff;
  box-shadow: 0 2px 8px rgba(61, 184, 151, 0.3);
  transition: all 0.2s;
}
.menu-button:hover {
  box-shadow: 0 4px 12px rgba(61, 184, 151, 0.4);
}

/* Overlay */
.overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  z-index: 1020;
}
.fade-enter-active,
.fade-leave-active { transition: opacity 0.3s ease; }
.fade-enter-from,
.fade-leave-to { opacity: 0; }

/* Sidebar Shell */
.sidebar {
  position: fixed;
  top: 0;
  left: 0;
  height: 100vh;
  width: 280px;
  background: var(--color-bg-card);
  display: flex;
  flex-direction: column;
  z-index: 1030;
  box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
  transform: translateX(-100%);
  transition: transform 0.3s ease;
  overflow: hidden;
}
.sidebar.is-open { transform: translateX(0); }

@media (max-width: 480px) {
  .sidebar { width: 85%; }
}

/*  Header: Logo & Close */
.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 1.25rem 1.25rem 0.75rem;
  flex-shrink: 0;
}
.logo {
  height: 45px;
  width: auto;
  object-fit: contain;
}
.close-button {
  width: 32px;
  height: 32px;
  padding: 0;
  border: none;
  border-radius: 8px;
  background: #f0f2f5;
  color: #888;
  font-size: 1rem;
  line-height: 1;
  cursor: pointer;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}
.close-button:hover {
  background: #e4e7eb;
  color: #555;
}

/* Profilkarte */
.profile-card {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0.75rem 1rem 1rem;
  padding: 0.85rem 1rem;
  background: #f5f7fa;
  border-radius: 12px;
  flex-shrink: 0;
}
.avatar {
  width: 44px;
  height: 44px;
  border-radius: 50%;
  background: var(--color-primary);
  color: #fff;
  font-weight: 600;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
}
.user-info {
  display: flex;
  flex-direction: column;
  gap: 2px;
  overflow: hidden;
}
.user-name {
  font-size: 0.9rem;
  font-weight: 600;
  color: #1a1a1a;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.user-email {
  font-size: 0.75rem;
  color: #888;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* Navigation */
nav {
  flex: 1;
  overflow-y: auto;
}
nav ul {
  list-style: none;
  padding: 0 1rem;
  margin: 0;
}
.nav-item {
  display: flex;
  align-items: center;
  gap: 0.9rem;
  padding: 0.85rem 0.5rem;
  text-decoration: none;
  color: #333;
  font-size: 0.95rem;
  font-weight: 500;
  border-radius: 10px;
  transition: background 0.15s;
}
.nav-item:hover {
  background: #f5f7fa;
}
.nav-item.router-link-active {
  color: var(--color-primary);
}
.nav-item--button {
  width: 100%;
  background: none;
  border: none;
  cursor: pointer;
  text-align: left;
}
.nav-label {
  flex: 1;
}

/* Icon wrapper (abgerundete Ecken) */
.icon-wrap {
  width: 38px;
  height: 38px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}
.icon-wrap svg {
  width: 20px;
  height: 20px;
}
.icon-green {
  background: rgba(61, 184, 151, 0.12);
  color: var(--color-primary);
}
.icon-blue {
  background: rgba(99, 102, 241, 0.12);
  color: #6366f1;
}
.icon-red {
  background: rgba(239, 68, 68, 0.12);
  color: #ef4444;
}
.nav-divider {
  height: 1px;
  background: #f0f2f5;
  margin: 0 0.5rem;
}

/* Footer Stats */
.sidebar-footer {
  display: flex;
  border-top: 1px solid #f0f2f5;
  padding: 1.1rem 1rem;
  flex-shrink: 0;
}
.stat {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 2px;
}
.stat-value {
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--color-primary);
  line-height: 1;
}
.stat-label {
  font-size: 0.75rem;
  color: #888;
}
</style>
