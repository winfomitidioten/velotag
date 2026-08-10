<script setup>
import { ref, computed } from 'vue';
import { useRouter } from 'vue-router';
import { Geolocation } from '@capacitor/geolocation';
import api from '@/api/api';
import { useUserStore } from '@/store/userStore';
import CameraGalleryPicker from '@/components/CameraGalleryPicker.vue';

const router = useRouter();
const userStore = useUserStore();

const currentStep = ref(1);

// --- Schritt 1: Name & Foto ---
const firstName = ref('');
const lastName = ref('');
const photoFile = ref(null);
const photoPreviewUrl = ref('');

const step1Valid = computed(() => !!firstName.value.trim() && !!lastName.value.trim());

const onPhotoAdded = (added) => {
    const photo = added[0];
    if (!photo) return;
    photoFile.value = photo.file;
    photoPreviewUrl.value = photo.previewUrl;
};

// --- Schritt 2: Standort ---
const latitude = ref(null);
const longitude = ref(null);
const locationName = ref('');
const manualQuery = ref('');
const locationLoading = ref(false);
const locationError = ref('');
const sensorHint = ref('');

const step2Valid = computed(() => (latitude.value !== null && longitude.value !== null) || !!locationName.value);

const detectLocation = async () => {
    locationError.value = '';
    sensorHint.value = '';
    locationLoading.value = true;
    try {
        const position = await Geolocation.getCurrentPosition();
        latitude.value = position.coords.latitude;
        longitude.value = position.coords.longitude;
        try {
            const response = await api.get('geocode/reverse/', {
                params: { lat: latitude.value, lon: longitude.value }
            });
            locationName.value = response.data.display_name || '';
            // Freitextfeld mitbefüllen, damit der User nicht denkt, er müsse
            // den Ort zusätzlich manuell eingeben
            manualQuery.value = locationName.value;
        } catch {
            // Reverse-Geocoding ist rein kosmetisch, Fehler hier blockieren nicht
        }
    } catch {
        sensorHint.value = 'Standort konnte nicht ermittelt werden. Bitte gib deinen Ort manuell ein.';
    } finally {
        locationLoading.value = false;
    }
};

const searchLocation = async () => {
    if (!manualQuery.value.trim()) return;
    locationError.value = '';
    locationLoading.value = true;
    try {
        const response = await api.get('geocode/', { params: { query: manualQuery.value } });
        latitude.value = response.data.latitude;
        longitude.value = response.data.longitude;
        locationName.value = response.data.display_name;
    } catch {
        locationError.value = 'Ort nicht gefunden, bitte anders formulieren.';
    } finally {
        locationLoading.value = false;
    }
};

// --- Schritt 3: Abschluss ---
const submitting = ref(false);
const submitError = ref('');

const goToStep2 = () => { if (step1Valid.value) currentStep.value = 2; };
const goToStep3 = () => { if (step2Valid.value) currentStep.value = 3; };
const backTo = (step) => { currentStep.value = step; };

const completeOnboarding = async () => {
    submitting.value = true;
    submitError.value = '';
    try {
        const formData = new FormData();
        formData.append('first_name', firstName.value);
        formData.append('last_name', lastName.value);
        if (photoFile.value) formData.append('profilbild', photoFile.value);
        if (latitude.value !== null && longitude.value !== null) {
            formData.append('latitude', latitude.value);
            formData.append('longitude', longitude.value);
        }
        if (locationName.value) formData.append('location_name', locationName.value);

        await api.post('onboarding/', formData);
        // Muss vor dem Push abgeschlossen sein: sonst sieht der Router-Guard noch
        // onboardingCompleted=false und schickt sofort zurück zu /onboarding.
        await userStore.fetchProfile();
        router.push('/map');
    } catch {
        submitError.value = 'Das hat leider nicht geklappt. Bitte versuche es noch einmal.';
    } finally {
        submitting.value = false;
    }
};
</script>

<template>
    <div class="onboarding-page">
        <div class="onboarding-box">
            <div class="onboarding-logo">
                <img src="@/assets/logo-light.png" alt="velotag" class="logo logo--light" />
                <img src="@/assets/logo-dark.png" alt="velotag" class="logo logo--dark" />
            </div>

            <div class="progress-dots">
                <span class="dot" :class="{ active: currentStep >= 1 }"></span>
                <span class="dot" :class="{ active: currentStep >= 2 }"></span>
                <span class="dot" :class="{ active: currentStep >= 3 }"></span>
            </div>

            <!-- Schritt 1: Name & Foto -->
            <section v-if="currentStep === 1" class="step">
                <h1>Wer bist du?</h1>
                <p class="step-hint">Damit dich deine Freunde in velotag erkennen.</p>

                <div class="field field--photo">
                    <label>Profilbild (optional)</label>
                    <img v-if="photoPreviewUrl" :src="photoPreviewUrl" alt="Profilbild-Vorschau" class="photo-preview" />
                    <CameraGalleryPicker :multiple="false" singular :has-photos="!!photoPreviewUrl" @photos-added="onPhotoAdded" />
                </div>

                <div class="field">
                    <label>Vorname</label>
                    <div class="input-wrapper">
                        <span class="input-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                                <path d="M367-527q-47-47-47-113t47-113q47-47 113-47t113 47q47 47 47 113t-47 113q-47 47-113 47t-113-47ZM160-160v-112q0-34 17.5-62.5T224-378q62-31 126-46.5T480-440q66 0 130 15.5T736-378q29 15 46.5 43.5T800-272v112H160Zm80-80h480v-32q0-11-5.5-20T700-306q-54-27-109-40.5T480-360q-56 0-111 13.5T260-306q-9 5-14.5 14t-5.5 20v32Zm296.5-343.5Q560-607 560-640t-23.5-56.5Q513-720 480-720t-56.5 23.5Q400-673 400-640t23.5 56.5Q447-560 480-560t56.5-23.5ZM480-640Zm0 400Z"/>
                            </svg>
                        </span>
                        <input type="text" v-model="firstName" required placeholder="Max" />
                    </div>
                </div>
                <div class="field">
                    <label>Nachname</label>
                    <div class="input-wrapper">
                        <span class="input-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                                <path d="M367-527q-47-47-47-113t47-113q47-47 113-47t113 47q47 47 47 113t-47 113q-47 47-113 47t-113-47ZM160-160v-112q0-34 17.5-62.5T224-378q62-31 126-46.5T480-440q66 0 130 15.5T736-378q29 15 46.5 43.5T800-272v112H160Zm80-80h480v-32q0-11-5.5-20T700-306q-54-27-109-40.5T480-360q-56 0-111 13.5T260-306q-9 5-14.5 14t-5.5 20v32Zm296.5-343.5Q560-607 560-640t-23.5-56.5Q513-720 480-720t-56.5 23.5Q400-673 400-640t23.5 56.5Q447-560 480-560t56.5-23.5ZM480-640Zm0 400Z"/>
                            </svg>
                        </span>
                        <input type="text" v-model="lastName" required placeholder="Mustermann" />
                    </div>
                </div>

                <button type="button" class="btn-primary" :disabled="!step1Valid" @click="goToStep2">Weiter</button>
            </section>

            <!-- Schritt 2: Standort -->
            <section v-else-if="currentStep === 2" class="step">
                <h1>Wo bist du unterwegs?</h1>
                <p class="step-hint">Damit die Karte direkt an der richtigen Stelle startet.</p>

                <button type="button" class="btn-secondary" :disabled="locationLoading" @click="detectLocation">
                    <svg xmlns="http://www.w3.org/2000/svg" height="18px" viewBox="0 -960 960 960" width="18px" fill="currentColor">
                        <path d="M480-480q33 0 56.5-23.5T560-560q0-33-23.5-56.5T480-640q-33 0-56.5 23.5T400-560q0 33 23.5 56.5T480-480Zm0 400Q319-217 239.5-334.5T160-552q0-150 96.5-239T480-880q127 0 223.5 89T800-552q0 100-79.5 217.5T480-80Z"/>
                    </svg>
                    <span>{{ locationLoading ? 'Ermittle Standort...' : 'Standort automatisch ermitteln' }}</span>
                </button>
                <p v-if="sensorHint" class="hint">{{ sensorHint }}</p>

                <div class="divider"><span>oder</span></div>

                <div class="field">
                    <label>Ort manuell eingeben</label>
                    <div class="input-wrapper">
                        <span class="input-icon">
                            <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                                <path d="M480-480q33 0 56.5-23.5T560-560q0-33-23.5-56.5T480-640q-33 0-56.5 23.5T400-560q0 33 23.5 56.5T480-480Zm0 400Q319-217 239.5-334.5T160-552q0-150 96.5-239T480-880q127 0 223.5 89T800-552q0 100-79.5 217.5T480-80Z"/>
                            </svg>
                        </span>
                        <input
                            type="text"
                            v-model="manualQuery"
                            placeholder="z.B. Wiesbaden"
                            @keyup.enter="searchLocation"
                        />
                        <button type="button" class="btn-inline" :disabled="locationLoading" @click="searchLocation">Suchen</button>
                    </div>
                    <p v-if="locationError" class="error">{{ locationError }}</p>
                </div>

                <p v-if="locationName" class="location-confirmed">Standort: {{ locationName }}</p>

                <button type="button" class="btn-primary" :disabled="!step2Valid" @click="goToStep3">Weiter</button>
            </section>

            <!-- Schritt 3: Was ist velotag? -->
            <section v-else class="step">
                <h1>Was ist velotag?</h1>
                <div class="bike-animation" aria-hidden="true">
                    <svg viewBox="0 0 200 100" class="bike-svg">
                        <g class="speed-lines">
                            <line x1="4" y1="58" x2="24" y2="58" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
                            <line x1="0" y1="68" x2="26" y2="68" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
                            <line x1="8" y1="78" x2="22" y2="78" stroke="currentColor" stroke-width="3" stroke-linecap="round" />
                        </g>
                        <g class="bike-body">
                            <!-- Räder (dünn = Rennrad-Reifen) -->
                            <circle class="wheel" cx="48" cy="74" r="19" fill="none" stroke="currentColor" stroke-width="2.5" />
                            <circle class="wheel" cx="152" cy="74" r="19" fill="none" stroke="currentColor" stroke-width="2.5" />
                            <circle cx="48" cy="74" r="2.5" fill="currentColor" />
                            <circle cx="152" cy="74" r="2.5" fill="currentColor" />

                            <!-- Diamant-Rahmen -->
                            <path d="M48 74 L96 74 L80 36 L48 74 Z"
                                  fill="none" stroke="currentColor" stroke-width="3.5" stroke-linejoin="round" />
                            <path d="M96 74 L140 50 L80 36"
                                  fill="none" stroke="currentColor" stroke-width="3.5" stroke-linejoin="round" stroke-linecap="round" />

                            <!-- Sattel -->
                            <path d="M72 34 L88 32" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" />

                            <!-- Gabel -->
                            <path d="M140 50 L152 74" fill="none" stroke="currentColor" stroke-width="3.5" stroke-linecap="round" />

                            <!-- Rennlenker (Drop-Bar) -->
                            <path d="M140 50 L145 41 C150 39 153 43 150 47 C148 50 151 53 155 51"
                                  fill="none" stroke="currentColor" stroke-width="2.75" stroke-linecap="round" />

                            <!-- Pedal-Kurbel -->
                            <g class="crank">
                                <circle cx="96" cy="74" r="5.5" fill="none" stroke="currentColor" stroke-width="2.5" />
                                <line x1="96" y1="74" x2="103" y2="81" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" />
                                <line x1="96" y1="74" x2="89" y2="67" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" />
                            </g>
                        </g>
                    </svg>
                </div>
                <p class="step-hint">
                    velotag zeigt Dir wo du am häufigsten fährst - alleine oder mit Freunden
                </p>
                <p class="motto-badge">GIG – Geradelt ist geil.</p>

                <p v-if="submitError" class="error">{{ submitError }}</p>
                <button type="button" class="btn-primary" :disabled="submitting" @click="completeOnboarding">
                    {{ submitting ? 'Wird gespeichert...' : "Los geht's" }}
                </button>
            </section>

            <button v-if="currentStep > 1" type="button" class="btn-back" @click="backTo(currentStep - 1)">Zurück</button>
        </div>
    </div>
</template>

<style scoped>
.onboarding-page {
    display: flex;
    justify-content: center;
    align-items: center;
    min-height: 100vh;
    background-color: var(--color-bg-page);
    padding: 1rem;
}

.onboarding-box {
    background: var(--color-bg-card);
    border-radius: var(--radius-lg);
    box-shadow: 0 4px 24px rgba(0, 0, 0, 0.08);
    padding: 2.5rem 2rem;
    width: 100%;
    max-width: 440px;
}

@media (max-width: 480px) {
    .onboarding-box {
        padding: 1.5rem 1rem;
        border-radius: 12px;
        box-shadow: none;
    }
}

.onboarding-logo {
    text-align: center;
    margin-bottom: 1rem;
}
.onboarding-logo .logo {
    height: 28px;
    opacity: 0.85;
}
.logo--dark { display: none; }
:root[data-theme='dark'] .logo--light { display: none; }
:root[data-theme='dark'] .logo--dark { display: inline; }
@media (prefers-color-scheme: dark) {
    :root:not([data-theme]) .logo--light { display: none; }
    :root:not([data-theme]) .logo--dark { display: inline; }
}

.progress-dots {
    display: flex;
    justify-content: center;
    gap: 8px;
    margin-bottom: 1.75rem;
}
.dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--color-border);
    transition: background 0.2s;
}
.dot.active {
    background: var(--color-primary);
}

h1 {
    font-size: 20px;
    margin: 0 0 6px;
    text-align: center;
    color: var(--color-text);
}
.step-hint {
    font-size: 13px;
    color: var(--color-text-muted);
    text-align: center;
    margin: 0 0 1.5rem;
}

.field { margin-bottom: 1.1rem; }
.field label { display: block; font-size: 13px; font-weight: 500; color: var(--color-text-muted); margin-bottom: 6px; }
.field--photo { text-align: center; }
.input-wrapper { display: flex; align-items: center; border: 1.5px solid var(--color-border); border-radius: 10px; padding: 0 14px; background: var(--color-bg-card); transition: border-color 0.2s; }
.input-wrapper:focus-within { border-color: var(--color-primary); }
.input-wrapper input { flex: 1; border: none; outline: none; padding: 11px 0; font-size: 14px; color: var(--color-text); background: transparent; }
.input-icon {
    display: flex;
    align-items: center;
    flex-shrink: 0;
    margin-right: 10px;
    color: var(--color-primary);
}
.input-icon svg {
    width: 16px;
    height: 16px;
}

.btn-inline {
    background: none;
    border: none;
    color: var(--color-primary);
    font-weight: 600;
    font-size: 13px;
    cursor: pointer;
    padding: 8px 0 8px 10px;
}
.btn-inline:disabled { opacity: 0.5; cursor: not-allowed; }

.photo-preview {
    display: block;
    width: 72px;
    height: 72px;
    border-radius: 50%;
    object-fit: cover;
    margin: 0 auto 10px;
}

.btn-primary {
    width: 100%;
    padding: 13px;
    background: var(--color-primary);
    color: var(--color-on-primary);
    border: none;
    border-radius: 10px;
    font-size: 15px;
    font-weight: 600;
    cursor: pointer;
    margin-top: 0.5rem;
    transition: background 0.2s, transform 0.1s;
}
.btn-primary:hover { background: var(--color-primary-dark); }
.btn-primary:active { transform: scale(0.98); }
.btn-primary:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-secondary {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px;
    width: 100%;
    padding: 13px;
    background: var(--color-bg-page);
    color: var(--color-primary);
    border: 1.5px solid var(--color-primary);
    border-radius: 10px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    transition: background 0.2s;
}
.btn-secondary:disabled { opacity: 0.6; cursor: not-allowed; }

.btn-back {
    display: block;
    margin: 1.25rem auto 0;
    background: none;
    border: none;
    color: var(--color-text-muted);
    font-size: 13px;
    cursor: pointer;
}
.btn-back:hover { color: var(--color-primary); }

.divider {
    display: flex;
    align-items: center;
    text-align: center;
    color: var(--color-text-muted);
    font-size: 12px;
    margin: 1rem 0;
}
.divider::before, .divider::after {
    content: '';
    flex: 1;
    border-bottom: 1px solid var(--color-border);
}
.divider span { padding: 0 10px; }

.hint {
    font-size: 12px;
    color: var(--color-text-muted);
    margin: 8px 0 0;
    text-align: center;
}
.error {
    color: var(--color-danger);
    font-size: 13px;
    text-align: center;
    margin-top: 0.5rem;
}
.location-confirmed {
    font-size: 13px;
    color: var(--color-primary);
    text-align: center;
    margin: 0.5rem 0 1rem;
}

.motto-badge {
    display: block;
    width: fit-content;
    margin: 0 auto 1.5rem;
    padding: 6px 16px;
    background: rgba(var(--color-primary-rgb), 0.1);
    color: var(--color-primary);
    font-weight: 700;
    font-size: 13px;
    letter-spacing: 0.01em;
    border-radius: 20px;
}

.bike-animation {
    display: flex;
    justify-content: center;
    margin-bottom: 1.5rem;
}
.bike-svg {
    width: 160px;
    height: 80px;
    color: var(--color-primary);
}
.bike-body {
    animation: bike-bob 1.6s ease-in-out infinite;
    transform-origin: 100px 60px;
}
.wheel,
.crank {
    transform-box: fill-box;
    transform-origin: center;
    animation: wheel-spin 1.2s linear infinite;
}
.speed-lines {
    color: var(--color-border);
    animation: speed-fade 1.2s ease-in-out infinite;
}
@keyframes wheel-spin {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}
@keyframes bike-bob {
    0%, 100% { transform: translateY(0); }
    50% { transform: translateY(-4px); }
}
@keyframes speed-fade {
    0%, 100% { opacity: 0.3; transform: translateX(0); }
    50% { opacity: 0.8; transform: translateX(-6px); }
}
</style>
