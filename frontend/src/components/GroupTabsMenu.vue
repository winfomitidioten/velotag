<script setup>
defineProps({
    groupId: {
        type: [String, Number],
        required: true,
    },
    active: {
        type: String, // 'members' | 'leaderboard'
        required: true,
    },
})
</script>

<template>
    <nav class="group-tabs">
        <router-link :to="`/group/${groupId}`" class="tab" :class="{ active: active === 'members' }">
            Mitglieder
        </router-link>
        <router-link :to="`/group/${groupId}/leaderboard`" class="tab" :class="{ active: active === 'leaderboard' }">
            Bestenliste
        </router-link>
    </nav>
</template>

<style scoped>
    .group-tabs {
        display: flex;
        gap: 0.5rem;
        padding: 0 1rem;
        margin: 1rem auto 0;
        width: 100%;
        max-width: 45rem;
        box-sizing: border-box;
    }

    .tab {
        flex: 1;
        text-align: center;
        text-decoration: none;
        padding: 0.65rem 1rem;
        border-radius: var(--radius-md);
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--color-text-muted);
        background-color: var(--color-bg-card);
        border: 1px solid var(--color-border);
        transition: all 0.15s ease;
    }

    .tab.active {
        color: white;
        background-color: var(--color-primary);
        border-color: var(--color-primary);
    }

    .tab:hover:not(.active) {
        background-color: var(--color-bg-page);
    }

    @media (min-width: 480px) {
        .group-tabs {
            padding: 0 2rem;
            margin-top: 1.5rem;
        }
        .tab {
            flex: none;
            padding: 0.65rem 1.5rem;
        }
    }
</style>