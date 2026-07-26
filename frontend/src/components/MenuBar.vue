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
      <RouterLink to="/map" @click="closeMenu" class="logo">
        <img src="@/assets/logo.png" alt="velotag logo" class="logo" />
      </RouterLink>
      <button class="close-button" @click="closeMenu" aria-label="Menü schließen">
        <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="#000000">
          <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/>
        </svg>
      </button>
    </div>

    <!-- Profil-Karte -->
    <div class="profile-card">
      <RouterLink :to="{ name: 'user-profile', params: { id: userStore.id } }" @click="closeMenu" class="nav-item">
        <div class="avatar">
          <img v-if="userProfileImage" :src="userProfileImage" alt="Profilbild" class="avatar-img"/>
          <span v-else>{{ userInitials }}</span>
        </div>
        <div class="user-info">
          <span class="user-name">{{ userName}}</span>
          <span class="user-email">{{ userEmail }}</span>
        </div>
      </RouterLink>
    </div>

    <!-- Navigation -->
    <nav>
      <ul>
        <li>
        
          <RouterLink to="/rides" @click="closeMenu" class="nav-item">
            <span class="icon-wrap icon-green">
              <svg xmlns="http://www.w3.org/2000/svg" height="40px" viewBox="0 -960 960 960" width="40px" fill="#3db897">
                <path d="M196-160q-82.33 0-139.17-57.17Q0-274.33 0-356.67 0-439 57.52-495.83q57.53-56.84 139.15-56.84 73 0 126.16 45.67Q376-461.33 388-392h42.67L352-613.33h-72V-680h192v66.67h-49.33l22 60.66h212L590-733.33H485.33V-800H586q24.67 0 42.5 12t26.17 34.67l73.33 200h36q81.34 0 138.67 56.99Q960-439.35 960-358.5q0 81.83-56.84 140.17Q846.32-160 764-160q-71.73 0-126.03-47t-67.3-118.33H388q-12 71-65.67 118.16Q268.67-160 196-160Zm0-66.67q45.67 0 79.17-28.16 33.5-28.17 45.5-70.5H204V-392h116.67q-12-42-45.84-68-33.83-26-78.16-26-54.34 0-92.17 37.5t-37.83 91.83q0 54.17 37.5 92.09 37.5 37.91 91.83 37.91ZM502-392h69.33q4.34-23 14.84-48.33 10.5-25.34 28.5-45.67H468l34 94Zm262 165.33q54.33 0 91.83-37.91 37.5-37.92 37.5-92.09 0-54.33-37.5-91.83T764-486h-12l39.33 110.67-62.66 22-41.34-110q-26 17-39.33 45.33-13.33 28.33-13.33 61.33 0 54.17 37.5 92.09 37.5 37.91 91.83 37.91Zm-570-130Zm570 0Z"/>
                <circle cx="12" cy="7" r="4"/>
              </svg>
            </span>
            <span class="nav-label">Fahrten</span>
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
          <RouterLink to="/settings" @click="closeMenu" class="nav-item">
            <span class="icon-wrap icon-blue">
              <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8" stroke-linecap="round" stroke-linejoin="round">
                <circle cx="12" cy="12" r="3"/>
                <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 0 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 0 1-2.83-2.83l.06-.06A1.65 1.65 0 0 0 4.68 15a1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 0 1 2.83-2.83l.06.06A1.65 1.65 0 0 0 9 4.68a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 0 1 2.83 2.83l-.06.06A1.65 1.65 0 0 0 19.4 9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z"/>
              </svg>
            </span>
            <span class="nav-label">Einstellungen</span>
          </RouterLink>
        </li>
      </ul>
    </nav>

    <!-- Footer: Log-Out -->
    <div class="sidebar-footer">
      <button @click="handleLogout" class="logout-btn">Abmelden</button>
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
  top: calc(var(--safe-top) + 0.5rem);
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
  padding: calc(var(--safe-top) + 0.75rem) 1.25rem 0.75rem;
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

/* Footer Log-Out */
.sidebar-footer {
  border-top: 1px solid #f0f2f5;
  padding: 1rem 1.25rem;
  flex-shrink: 0;
}
.logout-btn {
  display: block;
  width: 100%;
  padding: 0.55rem 1rem;
  background: none;
  border: 1.5px solid #dde1e7;
  border-radius: 8px;
  color: #888;
  font-size: 0.85rem;
  font-weight: 500;
  text-align: center;
  cursor: pointer;
  transition: color 0.15s, border-color 0.15s;
}
.logout-btn:hover {
  color: #ef4444;
  border-color: #ef4444;
}
</style>
