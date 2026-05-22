


<!-- Code Historie - alter Beispiel-Code von Maxi, nur zum initialen Test?-->


<!-- '<script setup>
import HelloWorld from './components/HelloWorld.vue'
import TheWelcome from './components/TheWelcome.vue'
</script>
<template>
  <header>
    <img alt="Vue logo" class="logo" src="./assets/logo.svg" width="125" height="125" />
    <div class="wrapper">
      <HelloWorld msg="You did it!" />
    </div>
  </header>
  <main>
    <TheWelcome />
  </main>
</template>
<style scoped>
header {
  line-height: 1.5;
}
.logo {
  display: block;
  margin: 0 auto 2rem;
}
@media (min-width: 1024px) {
  header {
    display: flex;
    place-items: center;
    padding-right: calc(var(--section-gap) / 2);
  }
  .logo {
    margin: 0 2rem 0 0;
  }
  header .wrapper {
    display: flex;
    place-items: flex-start;
    flex-wrap: wrap;
  }
}
  
</style> -->

<!-- 
// Beispiel um die Verbindung zu testen
<script setup>
import { ref, onMounted } from 'vue'
import apiClient from '@/api/client'
const message = ref('Warte auf Antwort vom Server...')
const status = ref('Unbekannt')
onMounted(async () => {
  try {
    const response = await apiClient.get('/routes/test/')
    console.log("Daten empfangen:", response.data) // Prüfe die Browser-Konsole (F12)
    message.value = response.data.message
    status.value = response.data.status
  } catch (error) {
    message.value = 'Keine Verbindung zum Backend!'
    status.value = 'Fehler'
    console.error('API Fehler:', error)
  }
})
</script>
<template>
  <RouterView />
</template>
<style>
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  background-color: #f5f7f8; /* Der sanfte Grauton für die ECHTE gesamte Seite */
  font-family: sans-serif;
  box-sizing: border-box;
}

#app {
  width: 100%;
  min-height: 100%;
  display: flex;
  flex-direction: column;
}
</style>
-->

