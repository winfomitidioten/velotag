import axios from 'axios';

const api = axios.create({
    //baseURL: 'http://127.0.0.1:8000/api/', Maxis vorheriger Code
    baseURL: '/api/', // Dank Proxy in vite.config.js, wird das automatisch an den Django-Server weitergeleitet
});

api.interceptors.request.use((config) => {
    const token = localStorage.getItem('auth_token');
    
    // NEU: Wir prüfen, ob Axios hier überhaupt vorbeikommt!
    console.log("AXIOS INTERCEPTOR LÄUFT! Gefundener Token:", token);
    
    if (token) {
        // Moderne, bombensichere Schreibweise für Axios-Header
        config.headers.set('Authorization', `Token ${token}`);
    }
    return config;
});

export default api; // Konfiguration wird in deinem gesamten Projekt verfügbar gemacht

/**
 * In Kombination mit dem Proxy in vite.config.js, weiß das Frontend nun, alle Anfragen die mit /api beginnen, werden an den Django-Server auf den Port 8000 weitergeleitet
 */