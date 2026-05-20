import './/assets/main.css'

import { createApp } from 'vue'
import App from './App.vue'

import router from './router'

//CSS global importieren, damit die Leaflet-Karte korrekt angezeigt wird (siehe Karte.vue)
import 'leaflet/dist/leaflet.css' 

//createApp(App).mount('#app')

createApp(App).use(router).mount('#app')