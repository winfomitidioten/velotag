<script setup>
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useUserStore } from '@/store/userStore';
import api from '@/api/api';
import CreateGroupModal from '@/components/CreateGroupModal.vue';

const userStore = useUserStore();
const route = useRoute();
const router = useRouter();

// /group/:id ist eine eigene Top-Level-Route (kein Kind von /group), daher würde
// vue-router den Gruppen-Tab sonst nicht als aktiv markieren, obwohl man sich
// inhaltlich noch "in" den Gruppen befindet (gleiches Problem wie in AppTabBar.vue).
const isGroupsActive = computed(() => ['group', 'group-detail'].includes(route.name));

const showCreateGroup = ref(false);

const userInitials = computed(() => userStore.initials || '?');
const userProfileImage = computed(() => userStore.profileImage || '');

const groups = ref([]);
const favoriteGroup = computed(() => groups.value.find(g => g.is_favorite) || null);
const showGroupsMenu = ref(false);
const showProfileMenu = ref(false);
const groupsMenuRef = ref(null); // Trigger-Button (für Klick-außerhalb-Erkennung)
const groupsDropdownRef = ref(null); // teleportete Liste (liegt nicht mehr im selben DOM-Ast)
const groupsDropdownStyle = ref({});
const profileMenuRef = ref(null);
let groupsCloseTimer = null;

const fetchGroups = async () => {
  try {
    const response = await api.get('groups/');
    groups.value = response.data;
  } catch (err) {
    console.error('Fehler beim Abrufen der Gruppen:', err);
  }
};

const closeMenus = () => {
  showGroupsMenu.value = false;
  showProfileMenu.value = false;
};

const openCreateGroup = () => {
  closeMenus();
  showCreateGroup.value = true;
};

const handleGroupCreated = (newGroup) => {
  groups.value.push(newGroup);
  showCreateGroup.value = false;
};

// Berechnet die Bildschirmposition des Dropdowns aus der tatsächlichen Position
// des Trigger-Buttons, da die Liste per Teleport außerhalb der scrollenden
// Nav-Leiste gerendert wird (siehe Kommentar bei .nav-dropdown-list)
const updateGroupsDropdownPosition = () => {
  if (!groupsMenuRef.value) return;
  const rect = groupsMenuRef.value.getBoundingClientRect();
  groupsDropdownStyle.value = {
    top: `${rect.bottom + 6}px`,
    left: `${rect.left}px`
  };
};

const openGroupsMenu = async () => {
  clearTimeout(groupsCloseTimer);
  if (showGroupsMenu.value) return;
  showProfileMenu.value = false;
  showGroupsMenu.value = true;
  await nextTick();
  updateGroupsDropdownPosition();
};

// Kurze Verzögerung statt sofortigem Schließen: der Mauszeiger muss den Weg vom
// Trigger-Button zur (per Teleport separat gerenderten) Liste zurücklegen können,
// ohne dass das Dropdown dazwischen zuklappt
const scheduleCloseGroupsMenu = () => {
  clearTimeout(groupsCloseTimer);
  groupsCloseTimer = setTimeout(() => {
    showGroupsMenu.value = false;
  }, 200);
};

const toggleProfileMenu = () => {
  const next = !showProfileMenu.value;
  closeMenus();
  showProfileMenu.value = next;
};

const handleClickOutside = (event) => {
  const insideGroupsTrigger = groupsMenuRef.value && groupsMenuRef.value.contains(event.target);
  const insideGroupsDropdown = groupsDropdownRef.value && groupsDropdownRef.value.contains(event.target);
  if (!insideGroupsTrigger && !insideGroupsDropdown) {
    showGroupsMenu.value = false;
  }
  if (profileMenuRef.value && !profileMenuRef.value.contains(event.target)) {
    showProfileMenu.value = false;
  }
};

const handleLogout = async () => {
  localStorage.removeItem('auth_token');
  userStore.clearUser();
  closeMenus();
  await router.push('/login');
};

const handleReposition = () => {
  if (showGroupsMenu.value) updateGroupsDropdownPosition();
};

onMounted(() => {
  fetchGroups();
  document.addEventListener('click', handleClickOutside);
  window.addEventListener('resize', handleReposition);
  window.addEventListener('scroll', handleReposition, true);
});
onUnmounted(() => {
  clearTimeout(groupsCloseTimer);
  document.removeEventListener('click', handleClickOutside);
  window.removeEventListener('resize', handleReposition);
  window.removeEventListener('scroll', handleReposition, true);
});
</script>

<template>
  <header class="app-header">
    <div class="app-header-inner">
      <RouterLink to="/map" class="app-logo" @click="closeMenus">
        <img src="@/assets/logo-light.png" alt="velotag logo" class="logo-img logo-img--light" />
        <img src="@/assets/logo-dark.png" alt="velotag logo" class="logo-img logo-img--dark" />
      </RouterLink>

      <nav class="app-nav">
        <RouterLink to="/map" class="nav-link" @click="closeMenus">
          <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
            <path d="M480-480q33 0 56.5-23.5T560-560q0-33-23.5-56.5T480-640q-33 0-56.5 23.5T400-560q0 33 23.5 56.5T480-480Zm0 294q122-112 181-203.5T720-552q0-109-69.5-178.5T480-800q-101 0-170.5 69.5T240-552q0 71 59 162.5T480-186Zm0 106Q319-217 239.5-334.5T160-552q0-150 96.5-249T480-880q127 0 223.5 99T800-552q0 100-79.5 217.5T480-80Zm0-480Z"/>
          </svg>
          <span>Karte</span>
        </RouterLink>

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
          <RouterLink to="/group" class="nav-link nav-link--button" :class="{ open: showGroupsMenu || isGroupsActive }" @click="closeMenus">
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
          </RouterLink>
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

      </nav>

      <div class="profile-menu" ref="profileMenuRef">
        <button type="button" class="profile-trigger" @click="toggleProfileMenu" aria-label="Profilmenü öffnen">
          <span class="avatar">
            <img v-if="userProfileImage" :src="userProfileImage" alt="Profilbild" class="avatar-img" />
            <span v-else>{{ userInitials }}</span>
          </span>
        </button>

        <ul v-if="showProfileMenu" class="profile-dropdown-list">
          <li>
            <RouterLink to="/profile" class="profile-dropdown-item" @click="closeMenus">Zum Profil</RouterLink>
          </li>
          <li>
            <RouterLink to="/settings" class="profile-dropdown-item" @click="closeMenus">Einstellungen</RouterLink>
          </li>
          <li class="profile-dropdown-divider" role="separator"></li>
          <li>
            <button type="button" class="profile-dropdown-item profile-dropdown-item--danger" @click="handleLogout">Abmelden</button>
          </li>
        </ul>
      </div>
    </div>

    <CreateGroupModal
      v-if="showCreateGroup"
      @close="showCreateGroup = false"
      @created="handleGroupCreated"
    />
  </header>
</template>

<style scoped>
.app-header {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  /* Muss über Karte.vues schwebenden Controls liegen (Toggle-Switch/Gruppen-Dropdown: z-index 9999) -
     ein z-index an den Dropdown-Listen weiter unten reicht dafür nicht, da er nur innerhalb des
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
  gap: 0.75rem;
  padding: 0 0.75rem;
}

.app-logo {
  flex-shrink: 0;
  display: flex;
  align-items: center;
}
.app-logo img {
  height: 60px;
  width: auto;
  object-fit: contain;
}

/* Wortmarke ist dunkel eingefärbt -> im Dunkel-Modus die helle Variante zeigen,
   sonst wäre der Schriftzug auf dunklem Hintergrund unlesbar */
.logo-img--dark {
  display: none;
}
:root[data-theme='dark'] .logo-img--light {
  display: none;
}
:root[data-theme='dark'] .logo-img--dark {
  display: block;
}
@media (prefers-color-scheme: dark) {
  :root:not([data-theme]) .logo-img--light {
    display: none;
  }
  :root:not([data-theme]) .logo-img--dark {
    display: block;
  }
}

/* Mittlerer Navigationsbereich: scrollt horizontal, statt umzubrechen,
   damit er auf schmalen Handy-Bildschirmen nicht überläuft */
.app-nav {
  flex: 1;
  min-width: 0;
  display: flex;
  align-items: center;
  gap: 0.35rem;
  overflow-x: auto;
  scrollbar-width: none;
}
.app-nav::-webkit-scrollbar {
  display: none;
}

.nav-link {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.7rem 0.9rem;
  border-radius: 10px;
  text-decoration: none;
  color: var(--color-text-muted, #666);
  font-size: 0.95rem;
  font-weight: 600;
  white-space: nowrap;
  border: none;
  background: none;
  cursor: pointer;
  transition: background-color 0.15s, color 0.15s;
}
.nav-link svg {
  width: 21px;
  height: 21px;
  flex-shrink: 0;
}
.nav-link:hover {
  background-color: var(--color-bg-page, #f0f2f5);
}
.nav-link.router-link-active,
.nav-link.open {
  color: var(--color-primary);
  background-color: rgba(var(--color-primary-rgb), 0.1);
}

.chevron {
  width: 20px !important;
  height: 20px !important;
  transition: transform 0.2s ease;
}
.chevron.rotated {
  transform: rotate(180deg);
}

.nav-dropdown {
  flex-shrink: 0;
}

/* position:fixed statt absolute: die Liste wird per Teleport außerhalb von .app-nav
   gerendert (siehe Template-Kommentar), top/left kommen daher aus groupsDropdownStyle */
.nav-dropdown-list {
  position: fixed;
  width: 280px;
  margin: 0;
  padding: 8px;
  list-style: none;
  background-color: var(--color-bg-card);
  border-radius: 14px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  z-index: 10001;
}

.nav-dropdown-item {
  display: block;
  box-sizing: border-box;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  color: var(--color-text, #1a1a1a);
  text-decoration: none;
  font-size: 1rem;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  border: none;
  background: none;
  width: 100%;
  text-align: left;
  cursor: pointer;
}
.nav-dropdown-item:hover {
  background-color: var(--color-bg-page, #f0f2f5);
}
.nav-dropdown-item--create {
  color: var(--color-primary);
  font-weight: 600;
}

.nav-dropdown-item--favorite {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.favorite-star {
  width: 18px;
  height: 18px;
  flex-shrink: 0;
  color: var(--color-warning);
}

.nav-dropdown-empty {
  padding: 0.85rem 1rem;
  font-size: 1rem;
  color: var(--color-text-muted, #888);
}

.nav-dropdown-divider {
  height: 1px;
  background: var(--color-border, #e5e7eb);
  margin: 4px 4px;
}

/* Profil */
.profile-menu {
  position: relative;
  flex-shrink: 0;
}
.profile-trigger {
  border: none;
  background: none;
  padding: 0;
  cursor: pointer;
  display: flex;
}
.avatar {
  width: 42px;
  height: 42px;
  border-radius: 50%;
  background: var(--color-primary);
  color: var(--color-on-primary);
  font-weight: 600;
  font-size: 0.95rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  overflow: hidden;
}
.avatar-img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.profile-dropdown-list {
  position: absolute;
  top: calc(100% + 6px);
  right: 0;
  width: 150px;
  margin: 0;
  padding: 8px;
  list-style: none;
  background-color: var(--color-bg-card);
  border-radius: 14px;
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
  z-index: 10001;
}
.profile-dropdown-item {
  display: block;
  box-sizing: border-box;
  width: 100%;
  padding: 0.85rem 1rem;
  border-radius: 10px;
  color: var(--color-text, #1a1a1a);
  text-decoration: none;
  font-size: 1rem;
  font-weight: 500;
  text-align: left;
  border: none;
  background: none;
  cursor: pointer;
}
.profile-dropdown-item:hover {
  background-color: var(--color-bg-page, #f0f2f5);
}
.profile-dropdown-item--danger {
  color: var(--color-danger);
}

.profile-dropdown-divider {
  height: 1px;
  background: var(--color-border, #e5e7eb);
  margin: 4px 4px;
}
</style>
