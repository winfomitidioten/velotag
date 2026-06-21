<script setup>
  import { ref } from 'vue'
  import api from '@/api/api'
  import { useGPXVerarbeitung } from '@/composables/useGPXVerarbeitung'
  import GroupSelectionUploadModal from '@/components/GroupSelectionUploadModal.vue'

  defineEmits(['close']) 

  // NEU: Wir entpacken nun auch selectedGroupIds, um die ausgewählte Gruppe zu speichern
  const { isDragging, onFileDrop, errorMessage, erfolgsMessage, selectedGroupIds } = useGPXVerarbeitung()

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
    const response = await api.get('strava/connect/')
    window.location.href = response.data.auth_url
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

      <button @click="$emit('close')" class="popup-close-button" aria-label="Schließen">
        <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 -960 960 960" fill="currentColor">
          <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/>
        </svg>
      </button>
    </div>
  </div>
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
    justify-content: center;
    align-items: center;
    z-index: 1001; 
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