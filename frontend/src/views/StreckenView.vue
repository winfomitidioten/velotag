<script setup>
    import { ref, onMounted } from 'vue'
    import api from '@/api/api'
    import RouteEditModal from '@/components/RouteEditModal.vue'
    import PageHeader from '@/components/PageHeader.vue'

    const strecken = ref([])       // Array der Strecken vom Backend
    const loading = ref(false)     // Ladeindikator
    const editingRoute = ref(null)

    const onRouteSaved = async () => {
        editingRoute.value = null
        await fetchStrecken()
    }

    const onRouteDeleted = async () => {
        editingRoute.value = null
        await fetchStrecken()
    }

    // Daten laden sobald die Seite aufgerufen wird
    const fetchStrecken = async () => {
        try {
            loading.value = true
            const response = await api.get('routes/list/')  // GET /api/routes/list/
            strecken.value = response.data
        } catch (err) {
            console.error('Fehler beim Laden der Strecken:', err)
        } finally {
            loading.value = false
        }
    }

    // Hilfsfunktion: Sekunden in Stundenformat
    const formatDuration = (seconds) => {
        if (!seconds) return '—'
        const h = Math.floor(seconds / 3600)
        const m = Math.floor((seconds % 3600) / 60)
        return `${h}:${String(m).padStart(2, '0')} h`
    }

    // Hilfsfunktion ISO Datum
    const formatDate = (isoString) => {
        return new Date(isoString).toLocaleDateString('de-DE', {
        day: 'numeric', month: 'short', year: 'numeric'
    })}

    onMounted(() => {
        fetchStrecken()
    })


</script>

<template>
    <div class="page-container">
        <PageHeader title="Meine Strecken">
            <span class="count-badge">{{ strecken.length }} Strecken</span>
        </PageHeader>

        <main class="page-content">

      <p v-if="loading" class="status-text">Strecken werden geladen...</p>

      <p v-else-if="strecken.length === 0" class="status-text">
        Noch keine Strecken hochgeladen. Gehe zur Karte und lade eine GPX-Datei hoch.
      </p>

      <div v-else class="table-card">

        <div class="table-header">
          <span>Name</span>
          <span>Datum</span>
          <span>Dauer</span>
          <span>Ø Herzfrequenz</span>
          <span>Ø Watt</span>
          <span></span>
        </div>

        <div
          v-for="strecke in strecken"
          :key="strecke.strecken_id"
          class="table-row"
        >
          <div class="row-name">
            <div class="row-icon">
              <svg xmlns="http://www.w3.org/2000/svg" height="16px" viewBox="0 -960 960 960" width="16px">
                <path d="M480-480q33 0 56.5-23.5T560-560q0-33-23.5-56.5T480-640q-33 0-56.5 23.5T400-560q0 33 23.5 56.5T480-480Zm0 294q122-112 181-203.5T720-560q0-117-76.5-188.5T480-820q-87 0-163.5 71.5T240-560q0 75 59 166.5T480-186Zm0 106Q319-217 239.5-334.5T160-560q0-150 96.5-245T480-900q127 0 223.5 95T800-560q0 112-79.5 229.5T480-80Zm0-480Z"/>
              </svg>
            </div>
            <div class="row-name-text">
              <span>{{ strecke.strecken_name }}</span>
              <div v-if="strecke.groups && strecke.groups.length" class="group-badges">
                <span v-for="g in strecke.groups" :key="g.id" class="group-badge">{{ g.name }}</span>
              </div>
            </div>
          </div>
          <span>{{ formatDate(strecke.created_at) }}</span>
          <span>{{ formatDuration(strecke.duration_seconds) }}</span>
          <span>{{ strecke.avg_puls != null ? strecke.avg_puls + ' BPM' : '—' }}</span>
          <span>{{ strecke.avg_watt != null ? strecke.avg_watt + ' W' : '—' }}</span>
          <button class="edit-btn" @click.stop="editingRoute = strecke" title="Bearbeiten">
            ✏️
          </button>
        </div>

      </div>

    </main>

    <RouteEditModal
      v-if="editingRoute"
      :route="editingRoute"
      @close="editingRoute = null"
      @saved="onRouteSaved"
      @deleted="onRouteDeleted"
    />
    </div>
</template>

<style scoped>
.page-container {
  min-height: 100vh;
  background-color: var(--color-bg-page);
  display: flex;
  flex-direction: column;
}

.count-badge {
  background-color: var(--color-primary-soft);
  color: var(--color-primary);
  font-size: 0.85rem;
  font-weight: 600;
  padding: 0.3rem 0.8rem;
  border-radius: 1rem;
}

.page-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  padding: 3rem 2rem;
  box-sizing: border-box;
}

.status-text {
  color: var(--color-text-muted);
  font-size: 0.95rem;
  margin-top: 4rem;
}

.table-card {
  background-color: var(--color-bg-card);
  border-radius: var(--radius-md);
  box-shadow: 0 0.4rem 1.2rem rgba(0, 0, 0, 0.02);
  overflow: hidden;
  width: 100%;
  max-width: 70rem;
}

.table-header,
.table-row {
  display: grid;
  grid-template-columns: 2fr 1.2fr 1fr 1fr 1fr 2.5rem;
  padding: 0.9rem 1.5rem;
  gap: 1rem;
  align-items: center;
}

.table-header {
  background-color: var(--color-bg-page);
  border-bottom: 2px solid var(--color-border);
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.05em;
}

.table-row {
  border-bottom: 1px solid var(--color-border);
  font-size: 0.9rem;
  color: var(--color-text);
  transition: background 0.15s, border-left 0.15s;
  border-left: 3px solid transparent;
}

.table-row:last-child {
  border-bottom: none;
}

.table-row:hover {
  background-color: var(--color-bg-page);
  border-left-color: var(--color-primary);
}

.row-name {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  font-weight: 600;
}

.row-icon {
  width: 2.2rem;
  height: 2.2rem;
  background-color: var(--color-primary-soft);
  border-radius: 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.row-icon svg {
  fill: var(--color-primary);
}

.row-name-text {
  display: flex;
  flex-direction: column;
  gap: 0.25rem;
}

.group-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.group-badge {
  font-size: 0.7rem;
  font-weight: 500;
  background-color: color-mix(in srgb, var(--color-primary) 15%, white);
  color: var(--color-primary);
  padding: 0.1rem 0.5rem;
  border-radius: 0.8rem;
}

.edit-btn {
  background: none;
  border: none;
  cursor: pointer;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  font-size: 1rem;
  color: var(--color-text-muted);
  transition: background-color 0.15s, color 0.15s;
  flex-shrink: 0;
  justify-self: end;
}

.edit-btn:hover {
  background-color: color-mix(in srgb, var(--color-primary) 12%, white);
  color: var(--color-primary);
}


</style>
