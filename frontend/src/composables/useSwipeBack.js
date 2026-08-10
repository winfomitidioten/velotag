import { useRouter, useRoute } from 'vue-router';
import { goBack } from './useBackNavigation';

const EDGE_ZONE_PX = 24; // Geste muss nahe am linken Bildschirmrand starten
const SWIPE_THRESHOLD_PX = 80; // Mindest-Wegstrecke nach rechts, um als "Zurück" zu gelten
const MAX_VERTICAL_DRIFT_PX = 60; // Zu viel vertikale Bewegung = Scrollen, kein Swipe

// Ahmt die iOS-Edge-Swipe-Geste nach (Kein natives Hook verfügbar, da die
// App eine Single-WebView-Capacitor-SPA ohne UINavigationController ist -
// muss daher auf iOS wie Android gleichermaßen selbst nachgebaut werden).
export function useSwipeBack() {
  const router = useRouter();
  const route = useRoute();

  let startX = 0;
  let startY = 0;
  let tracking = false;

  const onTouchStart = (event) => {
    const touch = event.touches[0];
    tracking = route.meta.showBack === true && touch.clientX <= EDGE_ZONE_PX;
    startX = touch.clientX;
    startY = touch.clientY;
  };

  const onTouchMove = (event) => {
    if (!tracking) return;
    const touch = event.touches[0];
    if (Math.abs(touch.clientY - startY) > MAX_VERTICAL_DRIFT_PX) {
      tracking = false; // überwiegend vertikale Bewegung -> Scroll, kein Swipe
    }
  };

  const onTouchEnd = (event) => {
    if (!tracking) return;
    tracking = false;
    const touch = event.changedTouches[0];
    const deltaX = touch.clientX - startX;
    const deltaY = Math.abs(touch.clientY - startY);
    if (deltaX > SWIPE_THRESHOLD_PX && deltaY < MAX_VERTICAL_DRIFT_PX) {
      goBack(router, route);
    }
  };

  const start = () => {
    window.addEventListener('touchstart', onTouchStart, { passive: true });
    window.addEventListener('touchmove', onTouchMove, { passive: true });
    window.addEventListener('touchend', onTouchEnd, { passive: true });
  };

  const stop = () => {
    window.removeEventListener('touchstart', onTouchStart);
    window.removeEventListener('touchmove', onTouchMove);
    window.removeEventListener('touchend', onTouchEnd);
  };

  return { start, stop };
}
