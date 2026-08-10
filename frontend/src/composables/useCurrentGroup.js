import { ref } from 'vue';

// Die Gruppe, die gerade in der Mitglieder- oder Bestenlisten-Ansicht offen ist.
// Beide Views teilen sich diesen Stand, damit beim Wechsel zwischen den Tabs der
// AppHeader (Gruppenname + Bearbeiten-Button) unverändert stehen bleibt, statt
// leer zu werden, bis die neue View ihre Daten nachgeladen hat.
// Modul-scoped ref nach demselben Muster wie useFavorite.js und usePageTitle.js.
const currentGroup = ref(null);

export function useCurrentGroup() {
    // Beim Öffnen einer ANDEREN Gruppe den alten Stand verwerfen - sonst stünde
    // kurz der Name der zuvor geöffneten Gruppe im Header.
    const enterGroup = (groupId) => {
        if (currentGroup.value && String(currentGroup.value.id) !== String(groupId)) {
            currentGroup.value = null;
        }
    };

    return { currentGroup, enterGroup };
}
