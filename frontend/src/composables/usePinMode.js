import { ref } from 'vue';

const isPinMode = ref(false);

export function usePinMode() {
    const setPinMode = (value) => {
        isPinMode.value = value;
    };
    return { isPinMode, setPinMode };
}