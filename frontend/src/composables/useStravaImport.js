import { ref } from 'vue'

// Modul-Level-Ref: alle Komponenten, die useStravaImport() aufrufen, teilen sich denselben Zustand
const showStravaImport = ref(false)

export function useStravaImport() {
  return { showStravaImport }
}
