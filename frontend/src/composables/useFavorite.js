import { ref } from 'vue'

// Wird außerhalb der Funktion definiert, damit alle Komponenten denselben Ref teilen
const favoriteGroupId = ref(null)

export function useFavorite() {
    return {
        favoriteGroupId
    }
}