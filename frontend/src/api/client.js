import axios from 'axios';

const apiClient = axios.create({
    baseURL: '/api', // beginnt jede Anfrage automatisch mit /api, statt mit der vollen Adresse 
    headers: {
        'Content-Type': 'application/json', // schickt Daten an Django in JSON und erwartet JSON zurück
    },
});

export default apiClient; // Konfiguration wird in deinem gesamten Projekt verfügbar gemacht

/**
 * In Kombination mit dem Proxy in vite.config.js, weiß das Frontend nun, alle Anfragen die mit /api beginnen, werden an den Django-Server auf den Port 8000 weitergeleitet
 */