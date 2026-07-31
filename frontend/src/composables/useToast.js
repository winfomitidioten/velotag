import { ref } from 'vue'

// Modul-Level-Refs: alle Komponenten, die useToast() aufrufen, teilen sich denselben Zustand
// (gleiches Muster wie useStravaImport.js) - so kann jede Komponente Toasts auslösen,
// ohne dass <AppToast /> in jeder View einzeln eingebunden werden muss.
const message = ref('')
const type = ref('success') // 'success' | 'error'
const visible = ref(false)

let hideTimer = null

const showToast = (text, toastType = 'success', duration = 3500) => {
    message.value = text
    type.value = toastType
    visible.value = true

    clearTimeout(hideTimer)
    hideTimer = setTimeout(() => {
        visible.value = false
    }, duration)
}

export function useToast() {
    return { message, type, visible, showToast }
}
