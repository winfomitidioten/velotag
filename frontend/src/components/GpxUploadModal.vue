<script setup>
  defineEmits(['close']) //Emits ermöglicht es dem "Kind" Ereigniss an Eltern (Karte) zu senden, z.B. Close-Event, damit die Karte weiß, dass das Modal geschlossen werden soll

  import api from '@/api/api'
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
      <div> 
        <a @click="connectStrava"> 
          <img src="@/assets/btn_strava_connect_with_orange.png" alt="Connect with Strava" />
        </a>
      </div>
      <div>
        <button class="btn_upload_manual">Datei auswählen</button>
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
    position: relative;/* Damit der Close-Button relativ zum Popup positioniert werden kann */
  }

  .btn_close_popup {
    position: absolute; /* Positioniert den Button relativ zum Popup-Content */
    top: -15px;   /* Positioniert den Button am oberen Rand */
    right: -15px; /* Positioniert den Button am rechten Rand */
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
    background-color: rgba(0, 0, 0, 0.5); /* Halbtransparenter Hintergrund */
    display: flex;
    justify-content: center;
    align-items: center;
    z-index: 1001; /* Damit das Popup über dem Button liegt */
  }
</style>