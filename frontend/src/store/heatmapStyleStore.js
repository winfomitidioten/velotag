import { defineStore } from 'pinia';
import { ref, watch } from 'vue';

const COLOR_KEY = 'velotag_heatmap_color';
const GLOW_KEY = 'velotag_heatmap_glow';
const HEX_COLOR_REGEX = /^#[0-9a-fA-F]{6}$/;

// heatmapColor === null bedeutet "kein Nutzer-Override" - drawUserMap.js fällt dann auf die
// bisherige Auto-Farbe (Blau auf Hybrid, sonst Rot) zurück, damit sich am bewährten Default
// nichts ändert, solange der Nutzer nichts personalisiert hat.
export const useHeatmapStyleStore = defineStore('heatmapStyle', () => {
    const storedColor = localStorage.getItem(COLOR_KEY);
    const heatmapColor = ref(HEX_COLOR_REGEX.test(storedColor) ? storedColor : null);

    const heatmapGlowEnabled = ref(JSON.parse(localStorage.getItem(GLOW_KEY) ?? 'false'));

    watch(heatmapColor, (value) => {
        if (value === null) {
            localStorage.removeItem(COLOR_KEY);
        } else {
            localStorage.setItem(COLOR_KEY, value);
        }
    });

    watch(heatmapGlowEnabled, (value) => localStorage.setItem(GLOW_KEY, JSON.stringify(value)));

    return { heatmapColor, heatmapGlowEnabled };
});
