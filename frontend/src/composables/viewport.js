import { ref } from 'vue';

// Ab dieser Breite gilt die Desktop-Menüleiste statt TabBar/Mobile-Header
// (muss zum @media-Breakpoint für --app-header-height/--tab-bar-height in
// main.css passen, sonst laufen Layout und Komponentenauswahl auseinander).
export const MOBILE_BREAKPOINT = 768;

// Modul-scoped ref nach demselben Muster wie useFavorite.js - ein einziger
// globaler resize-Listener (in App.vue) aktualisiert diesen Wert, alle
// Komponenten lesen ihn einfach reaktiv mit statt jeweils eigene Listener
// zu registrieren.
export const isMobile = ref(window.innerWidth < MOBILE_BREAKPOINT);

export function updateIsMobile() {
  isMobile.value = window.innerWidth < MOBILE_BREAKPOINT;
}
