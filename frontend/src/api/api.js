import axios from 'axios';

const api = axios.create({
    baseURL: import.meta.env.DEV
        ? '/api/'
        : 'http://167.233.33.166/api/',
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('auth_token');
    
    // NEU: Wir prüfen, ob Axios hier überhaupt vorbeikommt!
    console.log("AXIOS INTERCEPTOR LÄUFT! Gefundener Token:", token);
    
    if (token && token !== 'undefined') {
        config.headers.set('Authorization', `Token ${token}`);
    }
    return config;
});

export default api; // Konfiguration wird in deinem gesamten Projekt verfügbar gemacht

/**
 * In Kombination mit dem Proxy in vite.config.js, weiß das Frontend nun, alle Anfragen die mit /api beginnen, werden an den Django-Server auf den Port 8000 weitergeleitet
 */