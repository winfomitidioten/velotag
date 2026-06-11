<script setup>
  import { ref, onMounted, watch } from 'vue'
  import api from '@/api/api'

//hier die Logik zur Gruppenabfrage an die DB für den eingelogten User, damit die Gruppen in der Dropdown-Liste angezeigt werden können

const emit = defineEmits(['update:selectedGroup'])

const groups = ref([])
const loading = ref(false)
// Definieren der Variable für das v-model im Template (als Array für das 'multiple' Select)
const selectedGroup = ref([])

// Überwacht die Variable auf Änderungen und loggt den neuen Wert in die Konsole
watch(selectedGroup, (newValue) => {
  console.log("Ausgewählte Gruppe(n):", newValue)
  emit('update:selectedGroup', newValue)
})

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

onMounted(() => {
        fetchGroups()
    })
</script>

<template>

    <div class="group-selection-info">
        <img src="@/assets/infoButton.png" alt="Info" width="20" height="20" title="Bitte wähle optional eine Gruppe aus, der du die Strecke zuordnen möchtest."/>
        <p>Optional - Gruppenauswahl: </p>
      </div>

      <form>
        <select v-model="selectedGroup" class="group-dropdown" multiple>
          <option disabled value="">Bitte wählen</option>
          <option v-for="group in groups" :key="group.id" :value="group.id">  <!-- Hier binden wir jetzt die ID statt des Namens -->
            {{ group.name }}
          </option>
        </select>
      </form>

</template>

<style scoped>

.group-selection-info {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px; /* Abstand zwischen Bild und Text */
    margin-top: 15px; 
  }

  .group-selection-info p {
    margin: 0; /* Verhindert, dass das p-Tag durch Standard-Abstände das Layout verzerrt */
  }

</style>