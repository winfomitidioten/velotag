<script setup>
import { ref } from 'vue';
import api from '@/api/api';
import GroupSelectionUploadModal from '@/components/GroupSelectionUploadModal.vue';
import { Camera } from '@capacitor/camera';

const props = defineProbs({
    latitude: { type: Number, required: true },
    longitude: { type: Number, required: true }
});
const emit = defineEmits(['close', 'created']);

const selectedFile = ref(null);
const previewImage = ref(null);
const description = ref('');
const selectedGroups = ref([]);
const uploading = ref(false);
const error = ref('');

const setFromMediaResult = async (media) => {
    const response = await fetch(media.webPath);
    const blob = await response.blob();
    selectedFile.value = new File([blob], `pin-${Date.now()}.jpg`, { type: blob.type });
    previewImage.value = media.webPath;
};

const takePhoto = async () => {
    try {
        const media = await Camera.takePhoto({ quality: 80 });
        await setFromMediaResult(media);
    } catch (e) {
        console.log('Kamera abgebrochen', e);
    }
};

const chooseFromGallery = async () => {
    try {
        const media = await Camera.chooseFromGallery({ quality: 80 });
        const first = media.results[0];
        if (first) await setFromMediaResult(first);
    } catch (e) {
        console.log('Galeriauswahl abgebrochen', e);
    }
};

const submitPin = async () => {
    if (!selectedFile.value) {
        error.value = 'Bitte wähle zuerst ein Foto aus.';
        return;
    };
    try {
        uploading.value = true;
        error.value = '';
        const formData = new FormData();
        formData.append('latitude', props.latitude);
        formData.append('longitude', prop.longitude);
        formData.append('description', description.value);
        formData.append('image', selectedFile.value);
        selectedGroups.value.forEach(id => formData.append('groups', id));

        await api.post('photo-pins-create/', formData);
        emit('created');
    } catch (e) {
        console.error('Fehler beim Hochladen:', e);
        error.value = 'Foto konnte nicht gespeichert werden.';
    } finally {
        uploading.value = false;
    };
};

</script>