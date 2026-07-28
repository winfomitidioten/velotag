<script setup>
    import { ref, watch, onMounted, onUnmounted } from 'vue'
    import api from '@/api/api'

    const props = defineProps({ route: { type: Object, required: true }})
    const emit = defineEmits(['close', 'saved', 'deleted'])

    const editName = ref('')
    const selectedGroupIds = ref([])
    const groups = ref([]) // Alle verfügbaren Gruppen des Users
    const saving = ref(false)
    const confirmDelete = ref(false)
    const isOpen = ref(false) // Dropdown offen/zu
    const dropdownRef = ref(null)

    // Vorbelegung beim öffnen
    watch(() => props.route, (r) => {
        editName.value = r.strecken_name
        selectedGroupIds.value = r.group_id ? [...r.group_id] : []
        confirmDelete.value = false
    }, { immediate: true })

    // Gruppen laden
    const fetchGroups = async () => {
        const res = await api.get('groups/')
        groups.value = res.data
    }   

    const toggleGroup = (id) => {
        const i = selectedGroupIds.value.indexOf(id) 
        i > -1 ? selectedGroupIds.value.splice(i, 1) : selectedGroupIds.value.push(id)
    }

    const handleClickOutside = (e) => {
        if (dropdownRef.value && !dropdownRef.value.contains(e.target)) isOpen.value = false
    }

    const saveChanges = async () => {
        saving.value = true
        await api.patch(`routes/${props.route.strecken_id}/`, {
            strecken_name: editName.value,
            group_id: selectedGroupIds.value
        })
        emit('saved')
    }

    const deleteRoute = async () => {
        await api.delete(`routes/${props.route.strecken_id}/`)
        emit('deleted')
    }

    onMounted(() => { fetchGroups(); document.addEventListener('click', handleClickOutside) })
    onUnmounted(() => document.removeEventListener('click', handleClickOutside))

</script>



<template>
  <!-- Overlay: Klick auf Hintergrund schließt Modal -->
  <div class="popup-overlay" @click.self="emit('close')">
    <div class="popup-content">

      <h3>Strecke bearbeiten</h3>

      <!-- ── Name ── -->
      <div class="field">
        <label>Name</label>
        <input v-model="editName" type="text" />
      </div>

      <!-- ── Gruppen Multi-Select (gleiche Logik wie GroupSelectionUploadModal) ── -->
      <div class="field">
        <label>Gruppen (optional)</label>
        <div class="custom-dropdown" ref="dropdownRef">

          <div class="dropdown-header" @click="isOpen = !isOpen">
            <span v-if="selectedGroupIds.length === 0" class="placeholder">Keine Gruppe</span>
            <div v-else class="selected-items">
              <span v-for="id in selectedGroupIds" :key="id" class="badge" @click.stop>
                {{ groups.find(g => g.id === id)?.name || id }}
                <button type="button" class="remove-btn" @click.stop="toggleGroup(id)">&times;</button>
              </span>
            </div>
            <span class="chevron" :class="{ open: isOpen }">&#9662;</span>
          </div>

          <ul v-show="isOpen" class="dropdown-list">
            <li v-for="group in groups" :key="group.id"
                @click.stop="toggleGroup(group.id)"
                :class="{ selected: selectedGroupIds.includes(group.id) }">
              <input type="checkbox"
                     :checked="selectedGroupIds.includes(group.id)"
                     @change="toggleGroup(group.id)" @click.stop />
              <span>{{ group.name }}</span>
            </li>
          </ul>

        </div>
      </div>

      <!-- ── Aktionen ── -->
      <div class="modal-actions">
        <button class="btn-secondary" @click="emit('close')">Abbrechen</button>
        <button class="btn-primary" @click="saveChanges" :disabled="saving">
          {{ saving ? 'Speichern…' : 'Speichern' }}
        </button>
      </div>

      <!-- ── Löschen (zweistufig) ── -->
      <div class="delete-section">
        <template v-if="!confirmDelete">
          <button class="btn-danger-ghost" @click="confirmDelete = true">
            Strecke löschen
          </button>
        </template>
        <template v-else>
          <p class="confirm-text">Strecke wirklich löschen?</p>
          <div class="modal-actions">
            <button class="btn-secondary" @click="confirmDelete = false">Abbrechen</button>
            <button class="btn-danger" @click="deleteRoute">Ja, löschen</button>
          </div>
        </template>
      </div>

    </div>
  </div>
</template>

<style scoped>
.popup-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.4);
  backdrop-filter: blur(4px);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.popup-content {
  background: var(--color-bg-card);
  border-radius: var(--radius-lg);
  max-width: 28rem;
  width: 90%;
  padding: 2rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
  box-shadow: 0 1rem 3rem rgba(0, 0, 0, 0.2);
}

.popup-content h3 {
  margin: 0;
  font-size: 1.1rem;
  font-weight: 600;
  color: var(--color-text);
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.field label {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.04em;
}

.field input[type="text"] {
  padding: 0.6rem 0.8rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  font-size: 0.95rem;
  color: var(--color-text);
  background: var(--color-bg-page);
  outline: none;
  transition: border-color 0.15s;
}

.field input[type="text"]:focus {
  border-color: var(--color-primary);
}

/* Dropdown */
.custom-dropdown {
  position: relative;
  font-family: inherit;
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 2.75rem;
  padding: 0.5rem 0.75rem;
  background: var(--color-bg-page);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  cursor: pointer;
  transition: border-color 0.15s;
}

.dropdown-header:hover {
  border-color: var(--color-primary);
}

.placeholder {
  color: var(--color-text-muted);
  font-size: 0.9rem;
}

.selected-items {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  flex: 1;
}

.badge {
  display: flex;
  align-items: center;
  background: var(--color-primary);
  color: white;
  padding: 0.2rem 0.6rem;
  border-radius: 1rem;
  font-size: 0.82rem;
}

.remove-btn {
  background: none;
  border: none;
  color: white;
  margin-left: 0.35rem;
  cursor: pointer;
  font-size: 1rem;
  line-height: 1;
  padding: 0;
}

.chevron {
  transition: transform 0.2s;
  font-size: 0.8rem;
  margin-left: 0.5rem;
  color: var(--color-text-muted);
}

.chevron.open {
  transform: rotate(180deg);
}

.dropdown-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin: 4px 0 0;
  padding: 0;
  list-style: none;
  background: var(--color-bg-card);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.12);
}

.dropdown-list li {
  display: flex;
  align-items: center;
  padding: 0.6rem 0.75rem;
  cursor: pointer;
  border-bottom: 1px solid var(--color-border);
  transition: background 0.15s;
  font-size: 0.9rem;
}

.dropdown-list li:last-child {
  border-bottom: none;
}

.dropdown-list li:hover {
  background: var(--color-bg-page);
}

.dropdown-list li.selected {
  background: color-mix(in srgb, var(--color-primary) 10%, white);
}

.dropdown-list input[type="checkbox"] {
  margin-right: 0.6rem;
  accent-color: var(--color-primary);
  width: 16px;
  height: 16px;
}

/* Buttons */
.modal-actions {
  display: flex;
  gap: 0.75rem;
  justify-content: flex-end;
}

button {
  padding: 0.55rem 1.1rem;
  border-radius: var(--radius-md);
  cursor: pointer;
  font-size: 0.9rem;
  font-weight: 500;
  border: none;
  transition: opacity 0.15s;
}

button:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-dark);
}

.btn-secondary {
  background: #f1f5f9;
  color: #64748b;
}

.btn-secondary:hover {
  background: #e2e8f0;
}

.btn-danger {
  background: #ef4444;
  color: white;
}

.btn-danger:hover {
  background: #dc2626;
}

.btn-danger-ghost {
  background: none;
  border: 1px solid #ef4444;
  color: #ef4444;
  width: 100%;
}

.btn-danger-ghost:hover {
  background: #fef2f2;
}

/* Löschen-Bereich */
.delete-section {
  border-top: 1px solid var(--color-border);
  padding-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.75rem;
}

.confirm-text {
  margin: 0;
  font-size: 0.9rem;
  color: #ef4444;
  font-weight: 500;
}
</style>