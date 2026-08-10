// Merkt sich eine Zielroute, wenn ein nicht eingeloggter/onboardeter Nutzer eine
// requiresAuth-Route ansteuert (z.B. Einladungslink /join/:token), damit sie nach
// Login/Registrierung + ggf. Onboarding nicht verloren geht (siehe router/index.js,
// Login.vue, OnboardingView.vue).
const KEY = 'pending_redirect';

export function setPendingRedirect(path) {
    localStorage.setItem(KEY, path);
}

export function consumePendingRedirect() {
    const path = localStorage.getItem(KEY);
    localStorage.removeItem(KEY);
    return path && path.startsWith('/') ? path : null;
}
