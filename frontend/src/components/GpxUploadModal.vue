<script setup>
  import api from '@/api/api'
  // NEU: Wir importieren unsere ausgelagerte Logik
  import { useGPXVerarbeitung } from '@/composables/useGPXVerarbeitung'

  defineEmits(['close']) 

  // NEU: Wir entpacken exakt die zwei Dinge, die unser HTML für die Box braucht
  const { isDragging, onFileDrop, errorMessage } = useGPXVerarbeitung()

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

      <div> 
        <a @click="connectStrava"> 
          <img src="@/assets/btn_strava_connect_with_orange.png" alt="Connect with Strava" />
        </a>
      </div>
      
      <div 
        class="dropzone-box"
        :class="{ 'active': isDragging }"
        @dragover.prevent
        @dragenter.prevent="isDragging = true" 
        @dragleave.prevent="isDragging = false"
        @drop.prevent="onFileDrop"
      >
        <div class="dz-message">
          <span>Zieh deine GPX-Fahrt hier rein</span>
        </div>
      </div>

      <button class="btn_close_popup" @click="$emit('close')">x</button> 
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

  .btn_close_popup {
    position: absolute; 
    top: -15px;   
    right: -15px; 
    z-index: 3000;
    color: white;
    font-size: 24px;
    background-color: var(--color-primary); 
    height: 40px;
    width: 40px;
    border-radius: 50%;
    border: none;
    cursor: pointer;
    display: flex;
    justify-content: center;
    align-items: center;
    box-shadow: 0 2px 5px rgba(0,0,0,0.2);
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