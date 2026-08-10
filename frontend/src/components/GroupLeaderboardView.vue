<script setup>
import { useRoute, useRouter } from 'vue-router'
import { onMounted, ref, watch, computed } from 'vue'
import api from '@/api/api';
import PageHeader from '@/components/PageHeader.vue';
import HeaderButton from '@/components/HeaderButton.vue';
import GroupTabsMenu from '@/components/GroupTabsMenu.vue';
import { usePageTitle } from '@/composables/usePageTitle';
import { useCurrentGroup } from '@/composables/useCurrentGroup';
import { isMobile } from '@/composables/viewport';

const { setPageTitle } = usePageTitle()

const route = useRoute()
const router = useRouter()

// Group-ID kommt direkt aus der Route, ist also sofort verfügbar -
// dadurch können Header und Tabs schon vor dem ersten API-Response gerendert werden.
const groupId = computed(() => route.params.id)

// Geteilt mit GroupDetailView: kommt man von den Mitgliedern herüber, stehen Name und
// is_admin bereits - Titel und Bearbeiten-Button bleiben beim Tab-Wechsel unverändert
// stehen, statt kurz zu verschwinden. Nur die Bestenliste selbst lädt sichtbar nach.
const { currentGroup: group, enterGroup } = useCurrentGroup()
enterGroup(groupId.value)

// router.afterEach leert titleOverride bei jeder Navigation. Mit immediate steht der
// Name direkt wieder da, wenn die Gruppe schon geladen ist - ohne Warten auf den Fetch.
watch(group, (g) => { if (g) setPageTitle(g.name) }, { immediate: true })

const leaderboard = ref([])
const loading = ref(true)

// Lädt die Gruppe (für Name/Admin-Badge im Header) und die Bestenliste parallel.
// `loading` steuert nur den Ladezustand INNERHALB der Leaderboard-Karte
// (siehe Template) - Header und Tabs bleiben davon unberührt, damit sie
// nicht bei jedem Reload mit verschwinden/neu aufbauen.
const fetchGroup = async () => {
    try {
        loading.value = true;
        const [groupResponse, leaderboardResponse] = await Promise.all([
            api.get(`groups/${groupId.value}/`),
            api.get(`groups/${groupId.value}/leaderboard/`),
        ]);
        group.value = groupResponse.data; // watch oben setzt den Titel nach
        // Bestenliste kommt bereits sortiert + gerankt vom Backend (Gesamt-km über
        // ALLE Fahrten des Mitglieds, nicht nur die in dieser Gruppe).
        leaderboard.value = leaderboardResponse.data;
    } catch (err) {
        console.error('Fehler beim Laden der Bestenliste: ', err)
    } finally {
        loading.value = false;
    }
}

// Rang 1-3 bekommen eine Medaille statt einer Rang-Zahl im Template.
const medalForRank = (rank) => {
    if (rank === 1) return 'gold';
    if (rank === 2) return 'silver';
    if (rank === 3) return 'bronze';
    return null;
}

// from= merkt sich die Bestenliste, damit "Zurück" im Profil hierher führt und nicht
// auf die Karte (ausgewertet in der backTo-Funktion der user-profile-Route).
const goToProfile = (member) => {
    router.push({
        name: 'user-profile',
        params: { id: member.id },
        query: { from: route.fullPath }
    })
}

// Voller Name falls vorhanden, sonst Fallback auf den Usernamen.
const displayName = (member) => {
    if (member.first_name || member.last_name) {
        return `${member.first_name ?? ''} ${member.last_name ?? ''}`.trim();
    }
    return member.username;
}

watch(() => route.params.id, (newId) => {
    if (!newId) return;
    enterGroup(newId); // Stand der vorher geöffneten Gruppe verwerfen
    fetchGroup();
})

onMounted(() => {
    fetchGroup();
})
</script>

<template>
    <div class="page-container">
        <!-- Generischer Seitentitel wie bei den anderen Tabs (Meine Gruppen, Meine Strecken, ...).
             Header und Tabs werden unabhängig vom Ladezustand der Gruppe gerendert,
             damit sie beim Reload/Wechsel der Gruppe nicht mit verschwinden. -->
        <!-- Header-Inhalt identisch zu GroupDetailView, damit beim Wechsel zwischen
             Mitgliedern und Bestenliste nichts im AppHeader springt oder verschwindet. -->
        <Teleport v-if="isMobile" to="#app-header-actions">
            <HeaderButton v-if="group?.is_admin" class="desktop-edit-btn mobile-edit-btn" @click="router.push(`/group/${groupId}/edit`)">
                <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                    <path d="M200-200h57l391-391-57-57-391 391v57Zm-80 80v-170l528-527q12-11 26.5-17t30.5-6q16 0 31 6t26 18l55 56q12 11 17.5 26t5.5 30q0 16-5.5 30.5T817-647L290-120H120Zm640-584-56-56 56 56Zm-141 85-28-29 57 57-29-28Z"/>
                </svg>
                <span>Bearbeiten</span>
            </HeaderButton>
        </Teleport>
        <!-- Auf Mobile trägt der globale AppHeader den Titel; ein zusätzlicher
             PageHeader würde die Tab-Leiste um seine Höhe nach unten schieben. -->
        <PageHeader v-else>
            <HeaderButton v-if="group?.is_admin" class="desktop-edit-btn" @click="router.push(`/group/${groupId}/edit`)">
                <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                    <path d="M200-200h57l391-391-57-57-391 391v57Zm-80 80v-170l528-527q12-11 26.5-17t30.5-6q16 0 31 6t26 18l55 56q12 11 17.5 26t5.5 30q0 16-5.5 30.5T817-647L290-120H120Zm640-584-56-56 56 56Zm-141 85-28-29 57 57-29-28Z"/>
                </svg>
                <span>Bearbeiten</span>
            </HeaderButton>
        </PageHeader>
        <GroupTabsMenu :group-id="groupId" active="leaderboard" />

        <main class="page-content">
            <div class="leaderboard-card">
                <!-- Gruppenname im gleichen Icon-Karten-Stil wie in der Mitgliederansicht,
                     statt (wie vorher) im Header-Slot, wo er rechtsbündig/unformatiert landete. -->
                <div v-if="group" class="leaderboard-card-header">
                    <div class="group-icon-box">
                        <svg xmlns="http://www.w3.org/2000/svg" height="22px" viewBox="0 -960 960 960" width="22px">
                            <path d="M40-160v-112q0-34 17.5-62.5T104-378q62-31 126-46.5T360-440q66 0 130 15.5T616-378q29 15 46.5 43.5T680-272v112H40Zm720 0v-120q0-44-24.5-84.5T666-434q51 6 96 20.5t84 35.5q36 20 55 44.5t19 53.5v120H760ZM247-527q-47-47-47-113t47-113q47-47 113-47t113 47q47 47 47 113t-47 113q-47 47-113 47t-113-47Zm466 0q-47 47-113 47-11 0-28-2.5t-28-5.5q27-32 41.5-71t14.5-81q0-42-14.5-81T544-792q14-5 28-6.5t28-1.5q66 0 113 47t47 113q0 66-47 113ZM120-240h480v-32q0-11-5.5-20T580-306q-54-27-109-40.5T360-360q-56 0-111 13.5T140-306q-9 5-14.5 14t-5.5 20v32Zm296.5-343.5Q440-607 440-640t-23.5-56.5Q393-720 360-720t-56.5 23.5Q280-673 280-640t23.5 56.5Q327-560 360-560t56.5-23.5ZM360-240Zm0-400Z"/>
                        </svg>
                    </div>
                    <div class="group-info">
                        <h3>{{ group.name }}</h3>
                        <span>Bestenliste</span>
                    </div>
                </div>

                <!-- Nur dieser Bereich hängt am Ladezustand - der Rest der Seite bleibt stehen. -->
                <div v-if="loading" class="loading-state">
                    <p>Bestenliste wird geladen...</p>
                </div>

                <ul v-else class="leaderboard-list">
                    <li
                        v-for="member in leaderboard"
                        :key="member.id"
                        class="leaderboard-item"
                        :class="medalForRank(member.rank)"
                    >
                        <div class="rank-box">
                            <span v-if="medalForRank(member.rank)" class="medal" :class="medalForRank(member.rank)">
                                <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                                    <path d="m387-412 35-114-92-74h114l36-112 36 112h114l-93 74 35 114-92-71-93 71ZM240-40v-309q-38-42-59-96t-21-115q0-134 93-227t227-93q134 0 227 93t93 227q0 61-21 115t-59 96v309l-240-80-240 80Zm410-350q70-70 70-170t-70-170q-70-70-170-70t-170 70q-70 70-70 170t70 170q70 70 170 70t170-70ZM320-159l160-41 160 41v-124q-35 20-75.5 31.5T480-240q-44 0-84.5-11.5T320-283v124Zm160-62Z"/>
                                </svg>
                            </span>
                            <span v-else class="rank-number">{{ member.rank }}</span>
                        </div>

                        <img v-if="member.profilbild" :src="member.profilbild" alt="Profilbild"
                             class="member-avatar-img" @click="goToProfile(member)"/>
                        <div v-else class="member-avatar" @click="goToProfile(member)">
                            {{ displayName(member).charAt(0).toUpperCase() }}
                        </div>

                        <div class="member-info-text" @click="goToProfile(member)" role="button" tabindex="0"
                             @keydown.enter="goToProfile(member)" @keydown.space.prevent="goToProfile(member)">
                            <span class="member-name">{{ displayName(member) }}</span>
                            <span v-if="member.email === group?.admin_email" class="admin-badge">Admin</span>
                        </div>

                        <div class="km-box">
                            <span class="km-value">{{ member.totalKm.toLocaleString('de-DE') }}</span>
                            <span class="km-unit">km</span>
                        </div>
                    </li>
                </ul>
            </div>
        </main>
    </div>
</template>

<style scoped>
    /* Abstände identisch zu GroupDetailView, damit die Tab-Leiste in beiden
       Ansichten auf derselben Höhe sitzt. */
    .page-container {
        min-height: 100vh;
        padding-top: calc(var(--safe-top, 0px) + var(--app-header-height));
        padding-bottom: calc(var(--safe-bottom, 0px) + var(--tab-bar-height));
        background-color: var(--color-bg-page);
        display: flex;
        flex-direction: column;
        box-sizing: border-box;
    }

    /* Ab Desktop-Breite übernimmt PageHeader (sticky, eigener margin-top) den
       Versatz unter der DesktopNavBar - sonst würde der Abstand doppelt zählen.
       768px ist derselbe Umschaltpunkt wie MOBILE_BREAKPOINT in viewport.js,
       ab dem oben der PageHeader gerendert wird. */
    @media (min-width: 768px) {
        .page-container {
            padding-top: 0;
        }
    }

    /* Header-Button 1:1 wie in GroupDetailView, sonst würde er beim Tab-Wechsel
       seine Optik ändern. Teleport-Inhalt landet zwar im AppHeader, bleibt aber
       im Scope dieser Komponente - das Styling muss also hier stehen. */
    .desktop-edit-btn {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        background-color: var(--color-bg-page);
        color: var(--color-text);
        border: 1px solid var(--color-border);
        padding: 0.5rem;
        border-radius: var(--radius-md);
        cursor: pointer;
        font-weight: 600;
    }
    .desktop-edit-btn:hover {
        border-color: var(--color-primary);
        color: var(--color-primary);
    }

    /* Text-Label erst ab Tablet-Breite, damit im schmalen Header nichts überläuft */
    .desktop-edit-btn span {
        display: none;
    }

    /* Mobiler Header-Button als reines Icon ohne Rahmen/Hintergrund */
    .mobile-edit-btn {
        background-color: transparent;
        border: none;
        padding: 0.4rem;
    }
    .mobile-edit-btn:hover {
        background-color: var(--color-bg-page);
    }

    .leaderboard-card-header {
        display: flex;
        align-items: center;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }

    .group-icon-box {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 3rem;
        height: 3rem;
        background-color: var(--color-primary-soft);
        border-radius: var(--radius-md);
        flex-shrink: 0;
    }
    .group-icon-box svg {
        width: 1.5rem;
        height: 1.5rem;
        fill: var(--color-primary);
    }

    .group-info {
        display: flex;
        flex-direction: column;
        gap: 0.1rem;
        min-width: 0;
    }
    .group-info h3 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--color-text);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .group-info span {
        font-size: 0.85rem;
        color: var(--color-text-muted);
    }

    .page-content {
        flex: 1;
        display: flex;
        justify-content: center;
        padding: 1rem;
        box-sizing: border-box;
    }

    .leaderboard-card {
        background-color: var(--color-bg-card);
        padding: 1.25rem;
        border-radius: var(--radius-md);
        box-shadow: 0 0.2rem 0.8rem rgba(0, 0, 0, 0.03);
        box-sizing: border-box;
        width: 100%;
        max-width: 45rem;
        align-self: start;
    }

    .leaderboard-list {
        list-style: none;
        padding: 0;
        margin: 0;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .leaderboard-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.6rem 0.8rem;
        background-color: var(--color-bg-page);
        border-radius: var(--radius-md);
        border: 1px solid var(--color-border);
    }

    .leaderboard-item.gold {
        border-color: var(--color-gold-border);
        background-color: var(--color-gold-bg);
    }
    .leaderboard-item.silver {
        border-color: var(--color-silver-border);
        background-color: var(--color-silver-bg);
    }
    .leaderboard-item.bronze {
        border-color: var(--color-bronze-border);
        background-color: var(--color-bronze-bg);
    }

    .rank-box {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 2rem;
        flex-shrink: 0;
    }

    .rank-number {
        font-weight: 700;
        font-size: 0.95rem;
        color: var(--color-text-muted);
    }

    .medal {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
    }
    .medal.gold {
        color: var(--color-gold);
        background-color: var(--color-gold-soft);
    }
    .medal.silver {
        color: var(--color-silver);
        background-color: var(--color-silver-soft);
    }
    .medal.bronze {
        color: var(--color-bronze);
        background-color: var(--color-bronze-soft);
    }

    .member-avatar-img {
        width: 2.2rem;
        height: 2.2rem;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid var(--color-primary);
        flex-shrink: 0;
        cursor: pointer;
    }

    .member-avatar {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 2.2rem;
        height: 2.2rem;
        background-color: var(--color-primary-soft);
        color: var(--color-primary);
        font-weight: 600;
        font-size: 0.95rem;
        border-radius: 50%;
        flex-shrink: 0;
        cursor: pointer;
    }

    /* Bild und Name führen zum öffentlichen Profil, wie in der Mitgliederansicht.
       Die km-Angabe rechts liegt außerhalb und löst das nicht mit aus. */
    .member-info-text {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        flex-grow: 1;
        min-width: 0;
        cursor: pointer;
    }

    .member-info-text:hover .member-name,
    .member-info-text:focus-visible .member-name {
        color: var(--color-primary);
    }

    .member-name {
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--color-text);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .admin-badge {
        font-size: 0.7rem;
        background-color: var(--color-primary-soft);
        color: var(--color-primary);
        padding: 0.1rem 0.4rem;
        border-radius: var(--radius-sm);
        font-weight: 500;
        flex-shrink: 0;
    }

    .km-box {
        display: flex;
        align-items: baseline;
        gap: 0.25rem;
        flex-shrink: 0;
    }

    .km-value {
        font-size: 1rem;
        font-weight: 700;
        color: var(--color-text);
    }

    .km-unit {
        font-size: 0.75rem;
        color: var(--color-text-muted);
    }

    /* Nur die Karte zeigt den Ladezustand, deshalb hier keine 100vh-Höhe mehr -
       Header und Tabs stehen bereits fest, wenn dieser Text erscheint. */
    .loading-state {
        display: flex;
        justify-content: center;
        align-items: center;
        padding: 2rem 0;
        color: var(--color-text-muted);
    }

    @media (min-width: 480px) {
        .page-content {
            padding: 3rem 2rem;
        }
        .leaderboard-card {
            padding: 2rem;
        }
        .desktop-edit-btn {
            padding: 0.5rem 1rem;
        }
        .desktop-edit-btn span {
            display: inline;
        }
    }
</style>