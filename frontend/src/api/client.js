import axios from 'axios';

const apiClient = axios.create({
    // Gleiches Muster wie api.js: VITE_API_BASE_URL (z.B. für den Android-Emulator
    // auf 10.0.2.2) hat Vorrang, sonst der Vite-Proxy im Dev-Server, sonst Produktion.
    baseURL: import.meta.env.VITE_API_BASE_URL
        ?? (import.meta.env.DEV ? '/api' : 'http://167.233.33.166/api'),
    headers: {
        'Content-Type': 'application/json', // schickt Daten an Django in JSON und erwartet JSON zurück
    },
});

// Ohne diesen Interceptor schickt apiClient nie einen Auth-Token mit - Endpunkte wie
// save-push-token/ verlangen aber IsAuthenticated und antworten sonst immer mit 401.
apiClient.interceptors.request.use((config) => {
    const token = localStorage.getItem('auth_token');
    // Schützt vor dem String "undefined" (z.B. wenn response.data.token beim Login fehlte).
    if (token && token !== 'undefined') {
        config.headers.set('Authorization', `Token ${token}`);
    }
    return config;
});

export default apiClient; // Konfiguration wird in deinem gesamten Projekt verfügbar gemacht

/**
 * In Kombination mit dem Proxy in vite.config.js, weiß das Frontend nun, alle Anfragen die mit /api beginnen, werden an den Django-Server auf den Port 8000 weitergeleitet
 */
