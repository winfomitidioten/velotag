<script setup>
  import { ref } from 'vue'
  import api from '@/api/api'
  import { useGPXVerarbeitung } from '@/composables/useGPXVerarbeitung'
  import BaseModal from '@/components/BaseModal.vue'
  import GroupSelectionUploadModal from '@/components/GroupSelectionUploadModal.vue'
  import { useStravaImport } from '@/composables/useStravaImport'

  const emit = defineEmits(['close'])

  // NEU: Wir entpacken nun auch selectedGroupIds, um die ausgewählte Gruppe zu speichern
  const { isDragging, onFileDrop, errorMessage, erfolgsMessage, selectedGroupIds } = useGPXVerarbeitung()
  const { showStravaImport } = useStravaImport()

  const fileInput = ref(null)

  const openFileChooser = () => {
    fileInput.value.click()
  }

  const handleFileChange = (event) => {
    onFileDrop(event)
    event.target.value = '' // Setzt das Input-Feld zurück, damit dieselbe Datei ggf. nochmal ausgewählt werden kann
  }

  // Die Strava-Logik bleibt hier, da sie ein völlig anderer Geschäftsprozess ist
  const connectStrava = async () => {
    const status = await api.get('strava/status/')

    if (status.data.connected) {
      // Bereits verbunden: kein erneuter Umweg über Strava, direkt Aktivitäten auswählen
      showStravaImport.value = true
      emit('close')
    } else {
      const response = await api.get('strava/connect/')
      window.location.href = response.data.auth_url
    }
  }
</script>

<template>
  <BaseModal @close="$emit('close')">
    <h2>Fahrt hochladen</h2>
    <p>.gpx Datei auswählen</p>

    <div v-if="errorMessage" class="error-message">
      {{ errorMessage }}
    </div>

    <div v-if="erfolgsMessage" class="erfolgs-message">
      {{ erfolgsMessage }}
    </div>

    <div>
      <a @click="connectStrava">
        <img src="@/assets/btn_strava_connect_with_orange.png" alt="Connect with Strava" />
      </a>
    </div>

    <GroupSelectionUploadModal @update:selectedGroup="selectedGroupIds = $event" />

    <div
      class="dropzone-box"
      :class="{ 'active': isDragging }"
      @dragover.prevent
      @dragenter.prevent="isDragging = true"
      @dragleave.prevent="isDragging = false"
      @drop.prevent="onFileDrop"
      @click="openFileChooser"
    >
      <div class="dz-message">
        <span>Zieh deine GPX-Fahrt hier rein oder klicke, um eine Datei auszuwählen</span>
      </div>
      <input
        type="file"
        ref="fileInput"
        style="display: none"
        accept=".gpx"
        @change="handleFileChange"
      />
    </div>
  </BaseModal>
</template>

<style scoped>
  /* Overlay, Box und Schließen-Button kommen aus BaseModal */
  .error-message {
    background-color: #fee2e2;
    color: #e53e3e;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 15px;
    font-size: 14px;
  }

  .erfolgs-message{
    background-color: #c6f6d5;
    color: #385e38;
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 15px;
    font-size: 14px;
  }

  .dropzone-box {
    margin: 20px 0;
    padding: 40px 20px;
    border: 2px dashed #b3b3b3; 
    border-radius: 8px;
    background-color: #f9f9f9;
    cursor: pointer;
    transition: all 0.2s ease-in-out; 
  }

  .dropzone-box .dz-message {
    color: #666;
    font-size: 14px;
  }

  /* Färbt die dropzone Box im Velotag Farbcode😎 */
  .dropzone-box.active {
    border-color: var(--color-primary); 
    background-color: rgba(var(--color-primary-rgb), 0.05); 
    transform: scale(1.02); 
  }
</style>