import axios from 'axios';

const api = axios.create({
    // VITE_API_BASE_URL hat Vorrang (z.B. für den Android-Emulator auf 10.0.2.2),
    // sonst der Vite-Proxy im Dev-Server, sonst die feste Produktions-IP.
    baseURL: import.meta.env.VITE_API_BASE_URL
        ?? (import.meta.env.DEV ? '/api/' : 'http://167.233.33.166/api/'),
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('auth_token');
    
    // NEU: Wir prüfen, ob Axios hier überhaupt vorbeikommt!
    console.log("AXIOS INTERCEPTOR LÄUFT! Gefundener Token:", token);
    
    // Schützt vor dem String "undefined" (z.B. wenn beim Login response.data.token fehlte
    // und trotzdem in localStorage geschrieben wurde).
    if (token && token !== 'undefined') {
        config.headers.set('Authorization', `Token ${token}`);
    }
    return config;
});

api.interceptors.response.use(
    response => response,
    error => {
        if (error.response?.status === 401) {
            // Token ungültig/abgelaufen: löschen, damit der Router-Guard (router/index.js)
            // bei der nächsten Navigation automatisch zum Login umleitet.
            localStorage.removeItem('auth_token');
        }
        return Promise.reject(error);
    }
);

export default api; // Konfiguration wird in deinem gesamten Projekt verfügbar gemacht

/**
 * In Kombination mit dem Proxy in vite.config.js, weiß das Frontend nun, alle Anfragen die mit /api beginnen, werden an den Django-Server auf den Port 8000 weitergeleitet
 */