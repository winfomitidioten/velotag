import { ref } from 'vue'

// Wird außerhalb der Funktion definiert, damit alle Komponenten denselben Ref teilen
// Werte: null (Standard) | 'puls' | 'tempo' | 'watt'
const performanceMetric = ref(null)

// Min/Max der zuletzt geladenen Leistungs-Ansicht, für die Legende im Ebenen-Modal
const performanceRange = ref({ minValue: null, maxValue: null, hasData: true })

export function usePerformanceView() {
    return {
        performanceMetric,
        performanceRange
    }
}
