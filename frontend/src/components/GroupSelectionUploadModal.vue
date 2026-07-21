<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import api from '@/api/api'

//hier die Logik zur Gruppenabfrage an die DB für den eingelogten User, damit die Gruppen in der Dropdown-Liste angezeigt werden können

// modelValue erlaubt das Vorbelegen der Auswahl (z.B. beim Bearbeiten eines Fotos).
// Beim Upload ohne Wert bleibt es leer.
const props = defineProps({
  modelValue: { type: Array, default: () => [] },
  // Beim Bearbeiten wird nur das reine Dropdown gebraucht (ohne Trennlinie + "Optional"-Label)
  showHeader: { type: Boolean, default: true }
})

const emit = defineEmits(['update:selectedGroup'])

const groups = ref([])
const loading = ref(false)
// Definieren der Variable für das v-model im Template (als Array für das 'multiple' Select)
const selectedGroup = ref([...props.modelValue])

const isOpen = ref(false)
const dropdownRef = ref(null)

// Überwacht die Variable auf Änderungen und loggt den neuen Wert in die Konsole
watch(selectedGroup, (newValue) => {
  console.log("Ausgewählte Gruppe(n):", newValue)
  emit('update:selectedGroup', [...newValue])
}, { deep: true })

const fetchGroups = async () => {
    try {
        loading.value = true;
        const response = await api.get('groups/');
        groups.value = response.data;
    } catch(err) {
        console.error('Fehler: ', err)
    } finally {
        loading.value = false;
    }
}

const toggleSelection = (groupId) => {
  const index = selectedGroup.value.indexOf(groupId)
  if (index > -1) {
    selectedGroup.value.splice(index, 1) // Entfernen, wenn schon ausgewählt
  } else {
    selectedGroup.value.push(groupId) // Hinzufügen, wenn noch nicht ausgewählt
  }
}

// Schließt das Dropdown, wenn außerhalb geklickt wird
const handleClickOutside = (event) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target)) {
    isOpen.value = false
  }
}

onMounted(() => {
    fetchGroups()
    document.addEventListener('click', handleClickOutside)
})

onUnmounted(() => {
    document.removeEventListener('click', handleClickOutside)
})
</script>

<template>
  <template v-if="showHeader">
    <hr>
    <div class="group-selection-info">
      <svg xmlns="http://www.w3.org/2000/svg" height="22px" viewBox="0 -960 960 960" width="22px" fill="var(--color-text-muted)">
        <path d="M440-280h80v-240h-80v240Zm68.5-331.5Q520-623 520-640t-11.5-28.5Q497-680 480-680t-28.5 11.5Q440-657 440-640t11.5 28.5Q463-600 480-600t28.5-11.5ZM480-80q-83 0-156-31.5T197-197q-54-54-85.5-127T80-480q0-83 31.5-156T197-763q54-54 127-85.5T480-880q83 0 156 31.5T763-763q54 54 85.5 127T880-480q0 83-31.5 156T763-197q-54 54-127 85.5T480-80Zm0-80q134 0 227-93t93-227q0-134-93-227t-227-93q-134 0-227 93t-93 227q0 134 93 227t227 93Zm0-320Z"/>
      </svg>
      <p aria-label="Gruppenauswahl" title="Bitte wähle optional eine Gruppe aus, der du die Strecke zuordnen möchtest.">Optional - Gruppenauswahl:</p>
    </div>
  </template>

  <div class="custom-dropdown-container">
    <div class="custom-dropdown" ref="dropdownRef">
      <div class="dropdown-header" @click="isOpen = !isOpen">
        <span v-if="selectedGroup.length === 0" class="placeholder">Bitte wählen</span>
        <div v-else class="selected-items">
          <span v-for="id in selectedGroup" :key="id" class="badge" @click.stop>
            {{ groups.find(g => g.id === id)?.name || id }}
            <button type="button" class="remove-btn" @click.stop="toggleSelection(id)">&times;</button>
          </span>
        </div>
        <span class="chevron" :class="{ open: isOpen }">
          <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="var(--color-text)">
            <path d="M480-344 240-584l56-56 184 184 184-184 56 56-240 240Z"/>
          </svg>
        </span>
      </div>
      
      <Transition name="dropdown-fade">
        <ul v-show="isOpen" class="dropdown-list">
          <li 
            v-for="group in groups" 
            :key="group.id" 
            @click.stop="toggleSelection(group.id)" 
            :class="{ selected: selectedGroup.includes(group.id) }"
          >
            <input 
              type="checkbox" 
              :checked="selectedGroup.includes(group.id)" 
              @change="toggleSelection(group.id)" 
              @click.stop 
            />
            <span>{{ group.name }}</span>
          </li>
        </ul>
      </Transition>
    </div>
  </div>
</template>

<style scoped>
hr {
  margin-top: 18px;
  margin-bottom: 15px;
  border: none;
  border-top: 1px solid var(--color-text-muted);
  opacity: 0.5;
}

.group-selection-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px; /* Abstand zwischen Bild und Text */
  margin-top: 15px; 
  margin-bottom: 10px;
  color: var(--color-text-muted);
}

.group-selection-info p {
  margin: 0; /* Verhindert, dass das p-Tag durch Standard-Abstände das Layout verzerrt */
}

/* Custom Dropdown Styling */
.custom-dropdown-container {
  display: flex;
  justify-content: center;
  width: 100%;
}

.custom-dropdown {
  position: relative;
  width: 100%;
  max-width: 400px; /* Anpassen nach Bedarf, damit es nicht zu breit wird */
  font-family: inherit;
  color: var(--color-text); /* Nimmt var aus main.css / base.css an */
}

.dropdown-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  min-height: 32px;
  padding: 4px 10px;
  background-color: var(--color-background-soft, #f9f9f9);
  border: 1px solid var(--color-border, #ccc);
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.2s;
  /* box-shadow: 0 2px 4px rgba(0,0,0,0.05); */
}

.dropdown-header:hover {
  border-color: var(--color-border-hover, #888);
}

.placeholder {
  color: var(--color-text);
  opacity: 0.7;
}

.selected-items {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  flex: 1;
}

.badge {
  display: flex;
  align-items: center;
  background-color: var(--color-primary, #3db897); /* Velotag Grün als Akzentfarbe */
  color: white;
  padding: 3px 8px;
  border-radius: 35px;
  font-size: 0.8rem;
}

.remove-btn {
  background: none;
  border: none;
  color: white;
  margin-left: 6px;
  cursor: pointer;
  font-size: 1.1rem;
  line-height: 1;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chevron {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  transition: transform 0.18s ease, opacity 0.18s ease, color 0.18s ease;
  font-size: 0.8rem;
  margin-left: 8px;
  color: var(--color-text);
  opacity: 0.7;
}

.chevron.open {
  transform: rotate(180deg);
  opacity: 1;
  color: var(--color-text);
}

.dropdown-list {
  position: absolute;
  top: 100%;
  left: 0;
  right: 0;
  margin: 4px 0 0 0;
  padding: 0;
  list-style: none;
  background-color: var(--color-background, #fff);
  border: 1px solid var(--color-border, #ccc);
  border-radius: 8px;
  max-height: 200px;
  overflow-y: auto;
  z-index: 1000; /* Damit es über anderen Elementen liegt */
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.dropdown-fade-enter-active,
.dropdown-fade-leave-active {
  transition: opacity 0.18s ease, transform 0.18s ease;
}

.dropdown-fade-enter-from,
.dropdown-fade-leave-to {
  opacity: 0;
  transform: translateY(-6px);
}

.dropdown-list li {
  display: flex;
  align-items: center;
  padding: 6px 12px;
  cursor: pointer;
  /* border-bottom: 1px solid var(--color-border, #eee); */
  transition: background-color 0.2s;
}

.dropdown-list li:last-child {
  border-bottom: none;
}

.dropdown-list li:hover {
  background-color: var(--color-background-mute, #f1f1f1);
}

.dropdown-list li.selected {
  background-color: rgba(61, 184, 151, 0.15); /* Helles Velotag-Grün als Hintergrund */
}

.dropdown-list input[type="checkbox"] {
  margin-right: 8px;
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--color-primary, #3db897); /* Velotag Grün */
}
</style>