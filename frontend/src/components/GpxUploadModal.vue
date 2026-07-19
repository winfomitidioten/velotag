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
  <div class="popup">
    <div class="popup-content">
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

      <button @click="$emit('close')" class="popup-close-button" aria-label="Schließen">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
          <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/>
        </svg>
      </button>
    </div>
  </BaseModal>
</template>

<style scoped>
  /* PopUp Content*/
  .popup-content {
    background-color: white;
    padding: 20px;
    border-radius: 8px;
    text-align: center;
    position: relative;
  }

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

  .popup-close-button {
    position: absolute;
    top: 16px;
    right: 16px;
    background-color: var(--color-primary, #3db897);
    border: none;
    width: 32px;
    height: 32px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    color: white; /* Weiß für guten Kontrast zum grünen Hintergrund */
    border-radius: 50%;
    transition: background-color 0.15s;
    z-index: 3000;
  }

  /* Hover-Effekt in einem dunkleren Grün */
  .popup-close-button:hover {
    background-color: var(--color-primary-dark, #35a684);
    color: white;
  }

  .popup-close-button svg {
    width: 24px;
    height: 24px;
  }

  /* Upload PopUp*/
  .popup {
    position: fixed;
    bottom: 20px;
    right: 10px;
    width: 100%;
    height: 100%;
    background-color: rgba(0, 0, 0, 0.5); 
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