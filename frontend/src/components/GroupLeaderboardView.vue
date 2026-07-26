<script setup>
import { useRoute } from 'vue-router'
import { ref, onMounted, watch, computed } from 'vue'
import api from '@/api/api';
import PageHeader from '@/components/PageHeader.vue';
import GroupTabsMenu from '@/components/GroupTabsMenu.vue';


const route = useRoute()

// Group-ID kommt direkt aus der Route, ist also sofort verfügbar -
// dadurch können Header und Tabs schon vor dem ersten API-Response gerendert werden.
const groupId = computed(() => route.params.id)
const group = ref(null)
const leaderboard = ref([])
const loading = ref(false)

/**
 * TODO: Sobald der echte Endpoint für "alle Aktivitäten eines Users" steht,
 * diese Funktion ersetzen. Erwartetes Verhalten:
 *
 *   const res = await api.get(`users/${memberId}/activities/`)
 *   const totalKm = res.data.reduce((sum, activity) => sum + activity.distance_km, 0)
 *
 * Wichtig laut Anforderung: hier müssen ALLE Aktivitäten der Person rein,
 * nicht nur die in dieser Gruppe (also auch privat + andere Gruppen).
 * Falls die API stattdessen bereits eine aggregierte km-Summe pro User
 * zurückgibt (z.B. über /users/{id}/stats/), kann man direkt das Feld
 * nehmen statt selbst zu summieren.
 */
const fetchTotalKmForMember = async (memberId) => {
    // ---- MOCK START ----
    // Simuliert Netzwerk-Latenz + zufällige, aber stabile km-Werte pro Mitglied,
    // damit das Leaderboard beim Reload nicht wild durcheinander springt.
    await new Promise((resolve) => setTimeout(resolve, 50));
    const seed = String(memberId).split('').reduce((acc, c) => acc + c.charCodeAt(0), 0);
    const pseudoRandom = (seed * 9301 + 49297) % 233280 / 233280;
    return Math.round(pseudoRandom * 950 + 15); // 15 - 965 km
    // ---- MOCK END ----
}

// Lädt die Gruppe (inkl. Mitgliederliste) und baut danach die Bestenliste.
// `loading` steuert nur den Ladezustand INNERHALB der Leaderboard-Karte
// (siehe Template) - Header und Tabs bleiben davon unberührt, damit sie
// nicht bei jedem Reload mit verschwinden/neu aufbauen.
const fetchGroup = async () => {
    try {
        loading.value = true;
        const response = await api.get(`groups/${groupId.value}/`);
        group.value = response.data;
        await buildLeaderboard();
    } catch (err) {
        console.error('Fehler beim Laden der Gruppe: ', err)
    } finally {
        loading.value = false;
    }
}

// Holt für jedes Mitglied die Gesamt-km (aktuell gemockt, siehe oben)
// und sortiert die Mitglieder absteigend danach, um die Ränge zu vergeben.
const buildLeaderboard = async () => {
    if (!group.value?.members) return;

    const withKm = await Promise.all(
        group.value.members.map(async (member) => ({
            ...member,
            totalKm: await fetchTotalKmForMember(member.id),
        }))
    );

    leaderboard.value = withKm
        .sort((a, b) => b.totalKm - a.totalKm)
        .map((member, index) => ({
            ...member,
            rank: index + 1,
        }));
}

// Rang 1-3 bekommen eine Medaille statt einer Rang-Zahl im Template.
const medalForRank = (rank) => {
    if (rank === 1) return 'gold';
    if (rank === 2) return 'silver';
    if (rank === 3) return 'bronze';
    return null;
}

// Voller Name falls vorhanden, sonst Fallback auf den Usernamen.
const displayName = (member) => {
    if (member.first_name || member.last_name) {
        return `${member.first_name ?? ''} ${member.last_name ?? ''}`.trim();
    }
    return member.username;
}

watch(() => route.params.id, (newId) => {
    if (newId) fetchGroup();
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
        <PageHeader title="Bestenliste" />
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

                        <img v-if="member.profilbild" :src="member.profilbild" alt="Profilbild" class="member-avatar-img"/>
                        <div v-else class="member-avatar">
                            {{ displayName(member).charAt(0).toUpperCase() }}
                        </div>

                        <div class="member-info-text">
                            <span class="member-name">{{ displayName(member) }}</span>
                            <span v-if="member.email === group.admin_email" class="admin-badge">Admin</span>
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
    .page-container {
        min-height: 100vh;
        background-color: var(--color-bg-page);
        display: flex;
        flex-direction: column;
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
        background-color: #e8f7f3;
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
        border-color: #f6c85f;
        background-color: #fdf7e8;
    }
    .leaderboard-item.silver {
        border-color: #c7ccd1;
        background-color: #f4f5f6;
    }
    .leaderboard-item.bronze {
        border-color: #d79b6a;
        background-color: #fbf1e8;
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
        color: #b8860b;
        background-color: #f6e3a1;
    }
    .medal.silver {
        color: #6b7280;
        background-color: #e5e7eb;
    }
    .medal.bronze {
        color: #8b4513;
        background-color: #edd0b3;
    }

    .member-avatar-img {
        width: 2.2rem;
        height: 2.2rem;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid var(--color-primary);
        flex-shrink: 0;
    }

    .member-avatar {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 2.2rem;
        height: 2.2rem;
        background-color: #e8f7f3;
        color: var(--color-primary);
        font-weight: 600;
        font-size: 0.95rem;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .member-info-text {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        flex-grow: 1;
        min-width: 0;
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
        background-color: #e8f7f3;
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
    }
</style>