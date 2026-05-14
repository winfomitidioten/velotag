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
  <div id="test-area">
    <h1>Verbindungstest: Django + Vue</h1>
    <div class="card">
      <p><strong>Status:</strong> {{ status }}</p>
      <p><strong>Server-Nachricht:</strong> {{ message }}</p>
    </div>
  </div>
</template>

<style>
/* Einfaches CSS, damit man etwas sieht */
#test-area {
  max-width: 600px;
  margin: 50px auto;
  text-align: center;
  font-family: Arial, sans-serif;
  border: 2px solid #42b883;
  border-radius: 10px;
  padding: 20px;
}
.card {
  background: #050505;
  padding: 10px;
  border-radius: 5px;
}
</style>