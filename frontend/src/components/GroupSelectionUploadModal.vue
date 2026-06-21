<script setup>
import { ref, onMounted, onUnmounted, watch } from 'vue'
import api from '@/api/api'

//hier die Logik zur Gruppenabfrage an die DB für den eingelogten User, damit die Gruppen in der Dropdown-Liste angezeigt werden können

const emit = defineEmits(['update:selectedGroup'])

const groups = ref([])
const loading = ref(false)
// Definieren der Variable für das v-model im Template (als Array für das 'multiple' Select)
const selectedGroup = ref([])

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
  <div class="group-selection-info">
    <img src="@/assets/infoButton.png" alt="Info" width="20" height="20" title="Bitte wähle optional eine Gruppe aus, der du die Strecke zuordnen möchtest."/>
    <p>Optional - Gruppenauswahl:</p>
  </div>

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
        <span class="chevron" :class="{ open: isOpen }">&#9662;</span>
      </div>
      
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
    </div>
  </div>
</template>

<style scoped>
.group-selection-info {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px; /* Abstand zwischen Bild und Text */
  margin-top: 15px; 
  margin-bottom: 10px;
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
  min-height: 44px;
  padding: 8px 12px;
  background-color: var(--color-background-soft, #f9f9f9);
  border: 1px solid var(--color-border, #ccc);
  border-radius: 8px;
  cursor: pointer;
  transition: border-color 0.2s;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
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
  padding: 4px 8px;
  border-radius: 12px;
  font-size: 0.85rem;
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
  transition: transform 0.3s ease;
  font-size: 0.8rem;
  margin-left: 8px;
  color: var(--color-text);
  opacity: 0.7;
}

.chevron.open {
  transform: rotate(180deg);
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
  max-height: 250px;
  overflow-y: auto;
  z-index: 1000; /* Damit es über anderen Elementen liegt */
  box-shadow: 0 4px 12px rgba(0,0,0,0.15);
}

.dropdown-list li {
  display: flex;
  align-items: center;
  padding: 10px 12px;
  cursor: pointer;
  border-bottom: 1px solid var(--color-border, #eee);
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
  margin-right: 10px;
  width: 18px;
  height: 18px;
  cursor: pointer;
  accent-color: var(--color-primary, #3db897); /* Velotag Grün */
}
</style>