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
  <BaseModal width="min(480px, 90vw)" @close="$emit('close')">
    <div class="gpx-modal-body">
      <h2>Fahrt hochladen</h2>

      <div v-if="errorMessage" class="error-message">
        {{ errorMessage }}
      </div>

      <div v-if="erfolgsMessage" class="erfolgs-message">
        {{ erfolgsMessage }}
      </div>

      <div class="strava-section">
        <a @click="connectStrava" class="strava-btn">
          <img src="@/assets/btn_strava_connect_with_orange.png" alt="Connect with Strava" />
        </a>
      </div>

      <div class="divider">
        <span>ODER</span>
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
    </div>
  </BaseModal>
</template>

<style scoped>
  /* Overlay, Box, Radius/Schatten und Schließen-Button kommen aus BaseModal */

  /* Flexbox sorgt für perfekte, gleichmäßige Abstände zwischen den Abschnitten (ohne margin-Gefummel) */
  .gpx-modal-body {
    display: flex;
    flex-direction: column;
    gap: 24px;
  }

  /* --- MESSAGES --- */
  .error-message, .erfolgs-message {
    padding: 12px 16px;
    border-radius: 12px;
    font-size: 0.9rem;
    font-weight: 500;
    margin: 0;
    text-align: center;
  }

  .error-message {
    background-color: #fef2f2;
    color: #dc2626;
    border: 1px solid #fecaca;
  }

  .erfolgs-message {
    background-color: #f0fdf4;
    color: #16a34a;
    border: 1px solid #bbf7d0;
  }

  /* --- STRAVA BUTTON --- */
  .strava-section {
    text-align: center;
  }

  .strava-btn {
    display: inline-block;
    cursor: pointer;
  }

  .strava-btn img {
    max-width: 240px; /* Verhindert, dass der Button zu riesig wird */
    width: 100%;
    height: auto;
    transition: transform 0.2s ease, filter 0.2s ease;
  }

  .strava-btn:hover img {
    transform: translateY(-2px);
    filter: brightness(1.05); /* Leichter Leuchteffekt beim Hover */
  }

  /* --- DIVIDER (ODER) --- */
  .divider {
    display: flex;
    align-items: center;
    text-align: center;
    color: #94a3b8;
    font-size: 0.85rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
  }

  .divider::before,
  .divider::after {
    content: '';
    flex: 1;
    border-bottom: 1px solid #e2e8f0; /* Zarte graue Linien links und rechts */
  }

  .divider::before { margin-right: 16px; }
  .divider::after { margin-left: 16px; }

  /* --- DROPZONE --- */
  .dropzone-box {
    padding: 32px 20px;
    border: 2px dashed #cbd5e1; 
    border-radius: 16px;
    background-color: #f8fafc;
    cursor: pointer;
    transition: all 0.2s ease; 
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
  }

  .dropzone-box:hover {
    border-color: #94a3b8;
    background-color: #f1f5f9;
  }

  .dz-message {
    color: #64748b;
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
    color: #94a3b8;
    transition: color 0.2s ease;
  }

  .dropzone-box:hover .upload-icon {
    color: var(--color-primary, #3db897);
  }

  /* Aktiver Status (Drag & Drop) */
  .dropzone-box.active {
    border-color: var(--color-primary, #3db897); 
    background-color: rgba(61, 184, 151, 0.05); /* Zarter Velotag-Grüner Hintergrund */
    transform: scale(1.02); 
  }
  
  .dropzone-box.active .upload-icon {
    color: var(--color-primary, #3db897);
  }
</style>