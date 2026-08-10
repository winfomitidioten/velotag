<script setup>
    import { ref, onMounted } from 'vue'
    import api from '@/api/api'
    import RouteEditModal from '@/components/RouteEditModal.vue'
    import RouteOutline from '@/components/RouteOutline.vue'
    import { usePageTitle } from '@/composables/usePageTitle'

    const { setPageTitle } = usePageTitle()

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
        setPageTitle('Meine Fahrten')
        fetchStrecken()
    })


</script>

<template>
    <div class="page-container">
        <div class="strecken-meta-row">
            <span class="count-badge">{{ strecken.length }} Fahrten</span>
        </div>

        <main class="page-content">

      <p v-if="loading" class="status-text">Fahrten werden geladen...</p>

      <p v-else-if="strecken.length === 0" class="status-text">
        Noch keine Fahrten hochgeladen. Gehe zur Karte und lade eine GPX-Datei hoch.
      </p>

      <div v-else class="table-card">

        <div class="table-header">
          <span>Name</span>
          <span>Datum</span>
          <span>Dauer</span>
          <span>Ø Herzfrequenz</span>
          <span>Ø Watt</span>
          <span>Likes</span>
          <span></span>
        </div>

        <div
          v-for="strecke in strecken"
          :key="strecke.strecken_id"
          class="table-row"
        >
          <div class="row-name">
            <RouteOutline :polyline="strecke.polyline_map" :size="40" class="row-thumb" />
            <div class="row-name-text">
              <span>{{ strecke.strecken_name }}</span>
              <div v-if="strecke.groups && strecke.groups.length" class="group-badges">
                <span v-for="g in strecke.groups" :key="g.id" class="group-badge">{{ g.name }}</span>
              </div>
            </div>
          </div>
          <!-- Auf Desktop löst sich dieser Wrapper per display:contents auf, seine Kinder
               sitzen dann direkt in den Tabellenspalten. Auf Mobil wird er zum eigenen
               Raster mit Beschriftungen, da dort die Kopfzeile ausgeblendet ist. -->
          <div class="row-stats">
            <span class="stat">
              <span class="stat-label">Datum</span>
              <span class="stat-value">{{ formatDate(strecke.created_at) }}</span>
            </span>
            <span class="stat">
              <span class="stat-label">Dauer</span>
              <span class="stat-value">{{ formatDuration(strecke.duration_seconds) }}</span>
            </span>
            <span class="stat">
              <span class="stat-label">Ø HF</span>
              <span class="stat-value">{{ strecke.avg_puls != null ? strecke.avg_puls + ' BPM' : '—' }}</span>
            </span>
            <span class="stat">
              <span class="stat-label">Ø Watt</span>
              <span class="stat-value">{{ strecke.avg_watt != null ? strecke.avg_watt + ' W' : '—' }}</span>
            </span>
          </div>
          <span class="like-count">
              <svg viewBox="0 -960 960 960" class="heart-icon">
                <path d="M480-120 435-165Q276-311 172-427.5T68-643Q68-729 125-786t141-57Q312-843 355-802t125 118Q521-763 564-802t143-41Q783-843 840-786t57 143Q897-524 793-427.5T525-165l-45 45Z"/>
              </svg>
            {{ strecke.like_count }}
          </span>
          <button class="edit-btn" @click.stop="editingRoute = strecke" title="Bearbeiten">
            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
              <path d="M200-200h57l391-391-57-57-391 391v57Zm-80 80v-170l528-527q12-11 26.5-17t30.5-6q16 0 31 6t26 18l55 56q12 11 17.5 26t5.5 30q0 16-5.5 30.5T817-647L290-120H120Zm640-584-56-56 56 56Zm-141 85-28-29 57 57-29-28Z"/>
            </svg>
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
  /* flex-shrink: 0, da #app ein Flex-Container mit fester Höhe ist - ohne das
     wird der Container auf die Fensterhöhe gestaucht, der Inhalt läuft darüber
     hinaus und das padding-bottom sitzt nicht mehr unter der letzten Zeile
     (die dann hinter der TabBar verschwindet). */
  flex-shrink: 0;
  padding-top: calc(var(--safe-top, 0px) + var(--app-header-height));
  padding-bottom: calc(var(--safe-bottom, 0px) + var(--tab-bar-height) + 22px);
  background-color: var(--color-bg-page);
  display: flex;
  flex-direction: column;
  box-sizing: border-box;
}

/* Sitzt direkt unter dem fixierten AppHeader - kein eigener top-Offset nötig,
   da .page-container bereits per --app-header-height genau bis dorthin
   Platz macht und diese Zeile einfach im normalen Fluss direkt danach folgt.
   Ändert sich die Header-Höhe, verschiebt sich das automatisch mit. */
.strecken-meta-row {
  display: flex;
  justify-content: center;
  padding: 0.75rem 2rem 0;
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
  /* Datum bekommt mehr Anteil als die kurzen Zahlenspalten, die Likes-Spalte ("♥ 3")
     entsprechend weniger - sonst reicht die Breite für "13. Aug. 2026" nicht. */
  grid-template-columns: 2fr 1.5fr 1fr 1fr 1fr 0.7fr 2.5rem;
  padding: 0.9rem 1.5rem;
  gap: 1rem;
  align-items: left;
}
.like-btn {
  display: flex;
  align-items: center;
  gap: 4px;
  background: none;
  border: none;
  cursor: pointer;
  padding: 4px 10px;
  margin-top: 8px;
  border-radius: 12px;
  color: var(--color-text-muted);
  transition: color 0.15s, background-color 0.15s;
}

.like-btn:hover {
  background-color: color-mix(in srgb, #e53e3e 12%, white);
  color: #e53e3e;
}

.like-btn.liked {
  color: #e53e3e;
}

.heart-icon {
  width: 18px;
  height: 18px;
  fill: currentColor;
}

.like-count {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 0.75rem;
  font-weight: 600;
  /* Gleiche Farbe wie .like-btn in PublicUserProfile.vue - ohne diese Angabe erbt
     das Herz über fill: currentColor die Textfarbe der Tabellenzeile. */
  color: var(--color-text-muted);
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
  justify-content: flex-start;
  text-align: left;
  gap: 0.75rem;
  font-weight: 600;
  min-width: 0;
}

/* Streckenvorschau statt generischem Pin-Icon - gleiche Darstellung wie in der Lasche */
.row-thumb {
  width: 2.5rem;
  height: 2.5rem;
  flex-shrink: 0;
  color: var(--color-primary);
  background-color: var(--color-primary-soft);
  border-radius: 0.5rem;
  padding: 2px;
}

.row-name-text {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  text-align: left;
  gap: 0.25rem;
  min-width: 0;
}

.group-badges {
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}

.group-badge {
  font-size: 0.7rem;
  font-weight: 500;
  background-color: var(--color-primary-soft);
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
  background-color: var(--color-primary-soft);
  color: var(--color-primary);
}

/* Auf Desktop nehmen die vier Werte direkt an den Tabellenspalten teil,
   die Beschriftungen stehen in der Kopfzeile. */
.row-stats {
  display: contents;
}
.stat-label {
  display: none;
}

/* --- Mobil: aus jeder Tabellenzeile wird eine eigene Karte ---
   Sechs Spalten nebeneinander sind auf Handybreite nicht lesbar, daher stapeln
   sich hier Name und Werte, und die Kopfzeile entfällt zugunsten von Labels. */
@media (max-width: 768px) {
  .page-content {
    padding: 1rem;
  }

  .table-card {
    background-color: transparent;
    box-shadow: none;
    border-radius: 0;
    overflow: visible;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .table-header {
    display: none;
  }

  .table-row {
    position: relative;
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
    padding: 0.9rem 1rem;
    background-color: var(--color-bg-card);
    border: 1px solid var(--color-border);
    border-left: 3px solid var(--color-primary);
    border-radius: var(--radius-md);
  }

  .row-name {
    /* Platz für den Bearbeiten-Button oben rechts freihalten */
    padding-right: 2.5rem;
  }

  .row-name-text > span {
    font-size: 0.95rem;
  }

  .row-stats {
    display: grid;
    /* Nicht repeat(4, 1fr): das Datum braucht spürbar mehr Platz als "1:23 h" oder
       "142 BPM" - mit gleich breiten Spalten musste ausgerechnet es umbrechen. */
    grid-template-columns: 1.5fr 1fr 1fr 1fr;
    gap: 0.5rem;
    padding-top: 0.75rem;
    border-top: 1px solid var(--color-border);
    align-items: start;
  }

  .stat {
    display: flex;
    flex-direction: column;
    gap: 0.15rem;
    min-width: 0;
  }

  .stat-label {
    display: block;
    font-size: 0.65rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.04em;
    color: var(--color-text-muted);
  }

  .stat-value {
    font-size: 0.85rem;
    font-weight: 600;
    /* Kein nowrap/ellipsis mehr: bei vier gleich breiten Spalten war das Datum der
       längste Wert und wurde als einziger abgeschnitten ("13. Aug. 2..."). Es darf
       jetzt hinter dem Monat umbrechen, statt Information zu verlieren. */
    overflow-wrap: break-word;
  }

  .edit-btn {
    position: absolute;
    top: 0.6rem;
    right: 0.6rem;
    justify-self: auto;
  }
}


</style>
