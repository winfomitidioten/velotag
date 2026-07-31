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
        <svg class="upload-icon" xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
          <path d="M440-320v-326L336-542l-56-58 200-200 200 200-56 58-104-104v326h-80ZM240-160q-33 0-56.5-23.5T160-240v-120h80v120h480v-120h80v120q0 33-23.5 56.5T720-160H240Z"/>
        </svg>
        <span>Zieh deine GPX-Fahrt hier rein<br>oder klicke, um eine Datei auszuwählen</span>
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
  .error-message {
    background-color: var(--color-danger-bg);
    color: var(--color-danger);
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 15px;
    font-size: 14px;
  }

  .erfolgs-message{
    background-color: var(--color-success-bg);
    color: var(--color-success-text);
    padding: 10px;
    border-radius: 8px;
    margin-bottom: 15px;
    font-size: 14px;
  }

  .divider::before,
  .divider::after {
    content: '';
    flex: 1;
    border-bottom: 1px solid var(--color-border); /* Zarte graue Linien links und rechts */
  }

  .divider::before { margin-right: 16px; }
  .divider::after { margin-left: 16px; }

  /* --- DROPZONE --- */
  .dropzone-box {
    padding: 32px 20px;
    border: 2px dashed var(--color-border);
    border-radius: 16px;
    background-color: var(--color-bg-input);
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
  }

  .dropzone-box:hover {
    border-color: var(--color-text-muted);
    background-color: var(--color-bg-hover);
  }

  .dz-message {
    color: var(--color-text-muted);
    font-size: 0.95rem;
    line-height: 1.5;
    display: flex;
    flex-direction: column;
    align-items: center;
    gap: 12px;
  }

  .upload-icon {
    width: 40px;
    height: 40px;
    color: var(--color-text-muted);
    transition: color 0.2s ease;
  }

  .dropzone-box:hover .upload-icon {
    color: var(--color-primary, #3db897);
  }

  /* Aktiver Status (Drag & Drop) */
  .dropzone-box.active {
    border-color: var(--color-primary, #3db897);
    background-color: rgba(var(--color-primary-rgb), 0.05); /* Zarter Velotag-Grüner Hintergrund */
    transform: scale(1.02);
  }
  
  .dropzone-box.active .upload-icon {
    color: var(--color-primary, #3db897);
  }
</style>