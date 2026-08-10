import { ref } from 'vue';
import { useRouter } from 'vue-router';

// Modul-scoped ref nach demselben Muster wie useFavorite.js (gemeinsamer
// State über alle Komponenten hinweg) - überschreibt den statischen
// route.meta.title für Seiten mit dynamischem Titel (z.B. Gruppenname auf
// der Gruppendetailseite).
const titleOverride = ref(null);
let resetHookRegistered = false;

export function usePageTitle() {
  // useRouter() statt eines statischen Imports von '@/router' - mehrere
  // Views, die von router/index.js importiert werden, nutzen dieses
  // Composable. Ein direkter Modul-Import des Routers hier würde einen
  // zirkulären Import erzeugen, der im Produktions-Build (anders als im
  // Vite-Dev-Server) beim Laden crasht (router.afterEach auf "undefined").
  const router = useRouter();

  if (!resetHookRegistered) {
    resetHookRegistered = true;
    // Bei jeder Navigation zurücksetzen, sonst bliebe z.B. ein Gruppenname
    // beim Wechsel auf eine andere Seite fälschlich im Header stehen.
    router.afterEach(() => {
      titleOverride.value = null;
    });
  }

  const setPageTitle = (title) => {
    titleOverride.value = title;
  };

  return { titleOverride, setPageTitle };
}
