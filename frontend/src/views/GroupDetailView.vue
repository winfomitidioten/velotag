<script setup>
import { useRoute, useRouter } from 'vue-router'
import { ref, onMounted, watch, computed } from 'vue'
import api from '@/api/api';
import PageHeader from '@/components/PageHeader.vue';
import HeaderButton from '@/components/HeaderButton.vue';
import CameraGalleryPicker from '@/components/CameraGalleryPicker.vue';
import { useUserStore } from '@/store/userStore'
import ConfirmDialog from '@/components/ConfirmDialog.vue';
import { useToast } from '@/composables/useToast';
import QRCode from 'qrcode';

const route = useRoute()
const router = useRouter()
const { showToast } = useToast()

const groupId = computed(() => route.params.id)
const group = ref(null)
const loading = ref(false)
const showPopup = ref(false)
const newMemberMail = ref("")

// Bearbeiten der Gruppe (Name/Beschreibung/Bild) - eigener Popup-Zustand,
// getrennt vom Einladen-Popup oben.
const showEditPopup = ref(false)
const editName = ref("")
const editDescription = ref("")
const editSelectedFile = ref(null)
const editPreviewImage = ref(null)
const editRemoveProfilbild = ref(false)

const userStore = useUserStore()

const goToProfile = (member) => {
    router.push({ name: 'user-profile', params: { id: member.id } })
}

const fetchGroup = async () => {
    try {
        loading.value = true;
        const response = await api.get(`groups/${groupId.value}/`);
        group.value = response.data;
    } catch(err) {
        console.error('Fehler beim Laden der Gruppe: ', err)
    } finally {
        loading.value = false;
    }
}

// Öffnet den Bearbeiten-Popup und füllt ihn mit den aktuellen Gruppendaten vor.
const openEditPopup = () => {
    editName.value = group.value.name;
    editDescription.value = group.value.description || "";
    editSelectedFile.value = null;
    editPreviewImage.value = null;
    editRemoveProfilbild.value = false;
    showEditPopup.value = true;
}

const onEditPhotoAdded = (photos) => {
    const photo = photos[0];
    if (!photo) return;
    editSelectedFile.value = photo.file;
    editPreviewImage.value = photo.previewUrl;
    editRemoveProfilbild.value = false;
}

// Entfernt das Bild ohne ein neues auszuwählen (Akzeptanzkriterium: löschen ohne Ersatz).
const removeEditPicture = () => {
    editSelectedFile.value = null;
    editPreviewImage.value = null;
    editRemoveProfilbild.value = true;
}

const updateGroup = async () => {
    if (!editName.value.trim()) return;
    try {
        const formData = new FormData();
        formData.append('name', editName.value);
        formData.append('description', editDescription.value); // leerer String entfernt die Beschreibung

        if (editSelectedFile.value) {
            formData.append('profilbild', editSelectedFile.value);
        } else if (editRemoveProfilbild.value) {
            formData.append('remove_profilbild', 'true');
        }

        const response = await api.patch(`groups/${groupId.value}/`, formData);
        group.value = response.data;
        showEditPopup.value = false;
    } catch (error) {
        console.error("Fehler beim Bearbeiten der Gruppe:", error);
        alert(error.response?.data?.error || "Es gab ein Problem beim Speichern der Änderungen.");
    }
}

const inviteMember = async () => {
    if (!newMemberMail.value.trim()) return;
    try {
        const response = await api.post(`groups/${groupId.value}/invite/`, {
            email: newMemberMail.value
        });

        group.value = response.data;
        showPopup.value = false;
        newMemberMail.value = ""
    } catch(error) {
        console.error("Fehler beim Einladen:", error.response?.data || error.message);
        showToast(error.response?.data?.error || "Es gab ein Problem beim Hinzufügen.", 'error');
    }
}

// Alternative zur direkten E-Mail-Einladung oben: ein Einladungslink + QR-Code,
// falls man die E-Mail-Adresse der einzuladenden Person nicht kennt (VEL-74).
const inviteLink = ref(null);
const inviteQrDataUrl = ref(null);
const inviteLinkLoading = ref(false);

const generateInviteLink = async () => {
    try {
        inviteLinkLoading.value = true;
        const response = await api.get(`groups/${groupId.value}/invite-link/`);
        inviteLink.value = `${window.location.origin}/join/${response.data.token}`;
        inviteQrDataUrl.value = await QRCode.toDataURL(inviteLink.value);
    } catch (error) {
        console.error("Fehler beim Erzeugen des Einladungslinks:", error);
        showToast(error.response?.data?.error || "Es gab ein Problem beim Erzeugen des Einladungslinks.", 'error');
    } finally {
        inviteLinkLoading.value = false;
    }
}

// Kopiert den erzeugten Einladungslink in die Zwischenablage.
const copyInviteLink = async () => {
    try {
        await navigator.clipboard.writeText(inviteLink.value);
        showToast('Link in die Zwischenablage kopiert.');
    } catch (error) {
        console.error("Fehler beim Kopieren des Links:", error);
    }
}

// Bestätigungs-Dialoge
const confirmAction = ref(null);
const memberToDelete = ref(null);
const memberToTransfer = ref(null);
const actionBusy = ref(false);

const askDeleteMember = (email) => {
    memberToDelete.value = email;
    confirmAction.value = 'deleteMember';
};

const askDeleteGroup = () => { confirmAction.value = 'deleteGroup' };
const askLeaveGroup = () => { confirmAction.value = 'leaveGroup' };
const askTransferAdmin = (email) => {
    memberToTransfer.value = email;
    confirmAction.value = 'transferAdmin';
};

const cancleConfirm = () => {
    confirmAction.value = null;
    memberToDelete.value = null;
    memberToTransfer.value = null;
};

const confirmConfig = computed(() => {
    switch (confirmAction.value) {
        case 'deleteMember':
            return {
                title: 'Mitglied entfernen?',
                message: `Möchtest du ${memberToDelete.value} wirklich aus der Gruppe entfernen?`,
                confirmLabel: 'Entfernen'
            };
        case 'deleteGroup':
            return {
                title: 'Gruppe löschen?',
                message: 'Die Gruppe wird dauerhaft gelöscht. Diese Aktion kann nicht rückgängig gemacht werden.',
                confirmLabel: 'Löschen'
            };
        case 'leaveGroup':
            return {
                title: 'Gruppe verlassen?',
                message: 'Möchtest du diese Gruppe wirklich verlassen?',
                confirmLabel: 'Verlassen'
            };
        case 'transferAdmin':
            return {
                title: 'Adminrolle übergeben?',
                message: `Möchtest du die Adminrolle wirklich an ${memberToTransfer.value} übergeben?`,
                confirmLabel: 'Übergeben'
            };
        default:
            return {};
    }
});

const handleConfirm = () => {
    if (confirmAction.value === 'deleteMember') return deleteMember();
    if (confirmAction.value === 'deleteGroup') return deleteGroup();
    if (confirmAction.value === 'leaveGroup') return leaveGroup();
    if (confirmAction.value === 'transferAdmin') return transferAdmin();
};


const deleteMember = async () => {
    try{
        actionBusy.value = true;
        const response = await api.delete(`groups/${groupId.value}/kick/`, {
            data: { email: memberToDelete.value }
        });

        group.value = response.data;
        cancleConfirm();
    } catch (error) {
        console.error("Fehler beim Löschen des Mitglieds:", error);
        alert(error.response?.data?.error || "Es gab ein Problem beim Entfernen des Mitglieds.");
    } finally {
        actionBusy.value = false;
    }
};

// Übergibt die Adminrolle an ein anderes Mitglied. Der Server berechnet `is_admin`
// bei jeder Anfrage neu aus `group.admin`, daher reicht das Neuladen der Gruppendaten
// aus der Response, damit die Rechte hier sofort (bei mir deaktiviert, beim Ziel aktiviert) stimmen.
const transferAdmin = async () => {
    try {
        actionBusy.value = true;
        const response = await api.post(`groups/${groupId.value}/transfer-admin/`, {
            email: memberToTransfer.value
        });
        group.value = response.data;
        cancleConfirm();
    } catch (error) {
        console.error("Fehler beim Übertragen der Adminrolle:", error);
        alert(error.response?.data?.error || "Es gab ein Problem beim Übertragen der Adminrolle.");
    } finally {
        actionBusy.value = false;
    }
};

const deleteGroup = async () =>{
    try{
        actionBusy.value = true;
        await api.delete(`groups/${groupId.value}/`);
        router.push("/group");
    } catch (error) {
        console.error("Fehler beim Löschen der Gruppe:", error);
        alert(error.response?.data?.error || "Es gab ein Problem beim Löschen der Gruppe.");
        actionBusy.value = false;
    }
};

const confirmDeleteGroup = () => {
    askConfirm({
        title: 'Gruppe löschen?',
        message: 'Möchtest du diese Gruppe wirklich dauerhaft löschen?',
        confirmLabel: 'Löschen',
        danger: true,
        action: deleteGroup,
    });
}

const leaveGroup = async () =>{
    try{
        actionBusy.value = true;
        await api.post(`groups/${groupId.value}/leave`);
        router.push("/group");
    } catch (error) {
        console.error("Fehler beim Verlassen der Gruppe:", error);
        alert(error.response?.data?.error || "Es gab ein Problem beim Verlassen der Gruppe.");
        actionBusy.value = false;
    }
};

const confirmLeaveGroup = () => {
    askConfirm({
        title: 'Gruppe verlassen?',
        message: 'Möchtest du diese Gruppe wirklich verlassen?',
        confirmLabel: 'Verlassen',
        danger: true,
        action: leaveGroup,
    });
}

watch(() => route.params.id, (newId) => {
    if (newId) fetchGroup();
})

onMounted(() => {
    fetchGroup();
})
</script>

<template>
    <div class="page-container">
        <div v-if="loading" class="loading-state">
            <p>Gruppe wird geladen...</p>
        </div>

        <template v-else-if="group">
            <PageHeader>
                <HeaderButton v-if="group.is_admin" class="desktop-edit-btn" @click="openEditPopup">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                        <path d="M200-200h57l391-391-57-57-391 391v57Zm-80 80v-170l528-527q12-11 26.5-17t30.5-6q16 0 31 6t26 18l55 56q12 11 17.5 26t5.5 30q0 16-5.5 30.5T817-647L290-120H120Zm640-584-56-56 56 56Zm-141 85-28-29 57 57-29-28Z"/>
                    </svg>
                    <span>Bearbeiten</span>
                </HeaderButton>
                <HeaderButton v-if="group.is_admin" class="desktop-create-btn" @click="askDeleteGroup">
                    <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                        <path d="m376-300 104-104 104 104 56-56-104-104 104-104-56-56-104 104-104-104-56 56 104 104-104 104 56 56Zm-96 180q-33 0-56.5-23.5T200-200v-520h-40v-80h200v-40h240v40h200v80h-40v520q0 33-23.5 56.5T680-120H280Zm400-600H280v520h400v-520Zm-400 0v520-520Z"/>
                    </svg>
                    <span>Gruppe Löschen</span>
                </HeaderButton>
            </PageHeader>

            <button v-if="group.is_admin" @click="showPopup = true" class="mobile-fab-btn">
                <svg xmlns="http://www.w3.org/2000/svg" height="24px" viewBox="0 -960 960 960" width="24px" fill="currentColor">
                    <path d="M720-400v-120H600v-80h120v-120h80v120h120v80H800v120h-80ZM247-527q-47-47-47-113t47-113q47-47 113-47t113 47q47 47 47 113t-47 113q-47 47-113 47t-113-47ZM40-160v-112q0-34 17.5-62.5T104-378q62-31 126-46.5T360-440q66 0 130 15.5T616-378q29 15 46.5 43.5T680-272v112H40Zm80-80h480v-32q0-11-5.5-20T580-306q-54-27-109-40.5T360-360q-56 0-111 13.5T140-306q-9 5-14.5 14t-5.5 20v32Zm296.5-343.5Q440-607 440-640t-23.5-56.5Q393-720 360-720t-56.5 23.5Q280-673 280-640t23.5 56.5Q327-560 360-560t56.5-23.5ZM360-640Zm0 400Z"/>
                </svg>
            </button>

            <main class="page-content">
                <div class="group-card">
                    <div class="card-main-content">
                        <img v-if="group.profilbild" :src="group.profilbild" alt="Gruppenbild" class="group-icon-box group-icon-img">
                        <div v-else class="group-icon-box">
                            <svg xmlns="http://www.w3.org/2000/svg" height="22px" viewBox="0 -960 960 960" width="22px">
                                <path d="M40-160v-112q0-34 17.5-62.5T104-378q62-31 126-46.5T360-440q66 0 130 15.5T616-378q29 15 46.5 43.5T680-272v112H40Zm720 0v-120q0-44-24.5-84.5T666-434q51 6 96 20.5t84 35.5q36 20 55 44.5t19 53.5v120H760ZM247-527q-47-47-47-113t47-113q47-47 113-47t113 47q47 47 47 113t-47 113q-47 47-113 47t-113-47Zm466 0q-47 47-113 47-11 0-28-2.5t-28-5.5q27-32 41.5-71t14.5-81q0-42-14.5-81T544-792q14-5 28-6.5t28-1.5q66 0 113 47t47 113q0 66-47 113ZM120-240h480v-32q0-11-5.5-20T580-306q-54-27-109-40.5T360-360q-56 0-111 13.5T140-306q-9 5-14.5 14t-5.5 20v32Zm296.5-343.5Q440-607 440-640t-23.5-56.5Q393-720 360-720t-56.5 23.5Q280-673 280-640t23.5 56.5Q327-560 360-560t56.5-23.5ZM360-240Zm0-400Z"/>
                            </svg>
                        </div>
                        <div class="group-info">
                            <h3>{{ group.name }}</h3>
                            <span>{{ group.member_count }} Mitglieder</span>
                        </div>

                        <div class="button-group">
                            <button v-if="group.is_admin" @click="showPopup = true" class="action-btn desktop-invite-btn">
                                <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="currentColor">
                                    <path d="M720-400v-120H600v-80h120v-120h80v120h120v80H800v120h-80ZM247-527q-47-47-47-113t47-113q47-47 113-47t113 47q47 47 47 113t-47 113q-47 47-113 47t-113-47ZM40-160v-112q0-34 17.5-62.5T104-378q62-31 126-46.5T360-440q66 0 130 15.5T616-378q29 15 46.5 43.5T680-272v112H40Zm80-80h480v-32q0-11-5.5-20T580-306q-54-27-109-40.5T360-360q-56 0-111 13.5T140-306q-9 5-14.5 14t-5.5 20v32Zm296.5-343.5Q440-607 440-640t-23.5-56.5Q393-720 360-720t-56.5 23.5Q280-673 280-640t23.5 56.5Q327-560 360-560t56.5-23.5ZM360-640Zm0 400Z"/>
                                </svg>
                                <span>Einladen</span>
                            </button>

                            <button @click="askLeaveGroup" class="leave-btn">
                                <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px" fill="currentColor">
                                    <path d="M200-120q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h280v80H200v560h280v80H200Zm440-160-55-58 102-102H360v-80h327L585-622l55-58 200 200-200 200Z"/>
                                </svg>
                                <span>Verlassen</span>
                            </button>
                        </div>
                    </div>

                    <p v-if="group.description" class="group-description">{{ group.description }}</p>

                    <div class="card-stats-area">
                        <h4>Mitglieder</h4>
                        <ul class="member-list">
                            <li v-for="member in group.members" :key="member.id" class="member-item">
                                <img v-if="member.profilbild" :src="member.profilbild" alt="Profilbild" 
                                    class="member-avatar-img" @click="goToProfile(member)"/>
                                <div v-else class="member-avatar" @click="goToProfile(member)">
                                    {{ (member.first_name || member.email).charAt(0).toUpperCase() }}
                                </div>
                                
                                <div class="member-info-text">
                                    <span class="member-name">
                                        <template v-if="member.first_name || member.last_name">
                                            {{ member.first_name }} {{ member.last_name }}
                                        </template>
                                        <template v-else>
                                            {{ member.username }}
                                        </template>
                                        <span v-if="member.email === group.admin_email" class="admin-badge">Admin</span>
                                    </span>
                                    <span class="member-email">{{ member.email }}</span>
                                </div>

                                <!-- Adminrolle übergeben: nur für den aktuellen Admin sichtbar, nicht bei sich selbst -->
                                <div v-if="group.is_admin && member.email !== group.admin_email" class="make-admin" @click="askTransferAdmin(member.email)" title="Adminrolle übergeben">
                                    <svg xmlns="http://www.w3.org/2000/svg" height="20px" viewBox="0 -960 960 960" width="20px">
                                        <path d="M240-200 40-400l200-200 56 56-104 104h480v80H192l104 104-56 56Zm480-360-56-56 104-104H288v-80h480L664-704l56-56 200 200-200 200Z"/>
                                    </svg>
                                </div>

                                <div v-if="group.is_admin && member.email !== group.admin_email" class="delete-member" @click="askDeleteMember(member.email)">
                                    <svg xmlns="http://www.w3.org/2000/svg" height="22px" viewBox="0 -960 960 960" width="22px">
                                        <path d="m256-200-56-56 224-224-224-224 56-56 224 224 224-224 56 56-224 224 224 224-56 56-224-224-224 224Z"/>
                                    </svg>
                                </div>
                            </li>
                        </ul>
                    </div>
                </div>
            </main>

            <div v-if="showPopup" @click.self="showPopup = false" id="popup-overlay">
                <div id="popup-content">
                    <h3>Mitglieder einladen</h3>
                    <input v-model="newMemberMail" type="email" placeholder="max@mail.de" @keyup.enter="inviteMember">
                    <div id="popup-actions">
                        <button @click="showPopup = false" id="cancel-btn">Abbrechen</button>
                        <button @click="inviteMember" id="create-btn">Einladen</button>
                    </div>

                    <!-- Alternative: Einladung per Link/QR-Code, falls die E-Mail-Adresse
                         der einzuladenden Person nicht bekannt ist. -->
                    <div class="invite-link-section">
                        <button
                            type="button"
                            @click="generateInviteLink"
                            id="invite-link-btn"
                            :disabled="inviteLinkLoading"
                        >
                            {{ inviteLinkLoading ? 'Lädt...' : 'Einladungslink / QR-Code erzeugen' }}
                        </button>

                        <div v-if="inviteLink" class="invite-link-result">
                            <img v-if="inviteQrDataUrl" :src="inviteQrDataUrl" alt="QR-Code zum Beitreten" class="invite-qr-code">
                            <div class="invite-link-row">
                                <input type="text" :value="inviteLink" readonly>
                                <button type="button" @click="copyInviteLink" id="copy-link-btn">Kopieren</button>
                            </div>
                        </div>
                    </div>
                </div>
            </div>

            <div v-if="showEditPopup" @click.self="showEditPopup = false" id="popup-overlay">
                <div id="popup-content">
                    <h3>Gruppe bearbeiten</h3>
                    <input v-model="editName" type="text" placeholder="Gruppenname">
                    <textarea v-model="editDescription" placeholder="Beschreibung (optional)" rows="3"></textarea>

                    <img v-if="editPreviewImage" :src="editPreviewImage" alt="Gruppenbild" class="group-photo-preview">
                    <img v-else-if="group.profilbild && !editRemoveProfilbild" :src="group.profilbild" alt="Gruppenbild" class="group-photo-preview">

                    <CameraGalleryPicker :multiple="false" :has-photos="!!editPreviewImage" @photos-added="onEditPhotoAdded" />
                    <button
                        v-if="(group.profilbild && !editRemoveProfilbild) || editPreviewImage"
                        type="button"
                        @click="removeEditPicture"
                        id="remove-picture-btn"
                    >
                        Bild entfernen
                    </button>

                    <div id="popup-actions">
                        <button @click="showEditPopup = false" id="cancel-btn">Abbrechen</button>
                        <button @click="updateGroup" id="create-btn">Speichern</button>
                    </div>
                </div>
            </div>
            <ConfirmDialog
                v-if="confirmAction"
                :title="confirmConfig.title"
                :message="confirmConfig.message"
                :confirm-label="confirmConfig.confirmLabel"
                danger
                :busy="actionBusy"
                @confirm="handleConfirm"
                @cancel="cancleConfirm"
            />
        </template>
    </div>
</template>

<style scoped>
    @media (max-width: 480px) {
    .field-row {
            flex-direction: column;
            gap: 0;
        }
    }
    .page-container {
        min-height: 100vh;
        background-color: var(--color-bg-page);
        display: flex;
        flex-direction: column;
    }

    header h3 {
        font-size: 1.2rem;
        font-weight: 600;
        margin: 0;
        padding-left: 130px;
        color: var(--color-text);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .desktop-create-btn {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        background-color: var(--color-danger);
        color: var(--color-on-primary);
        border: none;
        /* Auf schmalen Handys nur das Icon zeigen (padding gleich für beide Achsen),
           damit zwei Header-Buttons nebeneinander nicht überlaufen. Text kommt erst
           ab 480px zurück, siehe Media Query weiter unten. */
        padding: 0.5rem;
        border-radius: var(--radius-md);
        cursor: pointer;
        font-weight: 600;
    }

    .desktop-edit-btn {
        display: flex;
        align-items: center;
        gap: 0.3rem;
        background-color: var(--color-bg-page);
        color: var(--color-text);
        border: 1px solid var(--color-border);
        padding: 0.5rem;
        border-radius: var(--radius-md);
        cursor: pointer;
        font-weight: 600;
    }
    .desktop-edit-btn:hover {
        border-color: var(--color-primary);
        color: var(--color-primary);
    }

    /* Text-Label der beiden Header-Buttons erst ab Tablet-Breite zeigen (siehe oben) */
    .desktop-create-btn span,
    .desktop-edit-btn span {
        display: none;
    }

    .mobile-fab-btn {
        position: fixed;
        bottom: 2rem;
        right: 1.5rem;
        z-index: 90;
        background-color: var(--color-primary);
        color: var(--color-on-primary);
        border: none;
        cursor: pointer;
        width: 3.5rem;
        height: 3.5rem;
        border-radius: 50%;
        padding: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0 4px 14px rgba(var(--color-primary-rgb), 0.4);
        transition: all 0.2s ease;
    }
    .mobile-fab-btn:active {
        transform: scale(0.95);
    }

    .button-group {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }

    .desktop-invite-btn {
        display: none; 
    }

    .leave-btn {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        background-color: transparent;
        border: 1px solid var(--color-danger);
        color: var(--color-danger);
        cursor: pointer;
        border-radius: var(--radius-md);
        padding: 0.6em 1.2em;
        font-size: 0.9rem;
        font-weight: 600;
        transition: all 0.2s ease;
        white-space: nowrap;
    }
    .leave-btn:hover {
        background-color: var(--color-danger-bg);
    }

    .page-content {
        flex: 1;
        display: flex;
        justify-content: center;
        padding: 1rem;
        box-sizing: border-box;
    }

    .group-card {
        display: flex;
        flex-direction: column;    
        justify-content: flex-start;
        gap: 1.5rem;                
        background-color: var(--color-bg-card); 
        padding: 1.25rem;     
        border-radius: var(--radius-md);     
        box-shadow: 0 0.2rem 0.8rem rgba(0, 0, 0, 0.03);
        box-sizing: border-box;
        width: 100%;
        max-width: 45rem;  
        border: 2px solid transparent;
        align-self: start;
    }

    .card-main-content {
        display: flex;
        align-items: center;
        width: 100%;
        gap: 1rem;
    }

    .group-icon-box {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 3rem;          
        height: 3rem;
        background-color: var(--color-primary-soft);
        border-radius: var(--radius-md);     
        flex-shrink: 0;            
    }
    .group-icon-box svg {
        width: 1.5rem;
        height: 1.5rem;
        fill: var(--color-primary);
    }
    .group-icon-img {
        object-fit: cover;
    }

    .group-description {
        margin: 0;
        font-size: 0.9rem;
        line-height: 1.4;
        color: var(--color-text-muted);
        white-space: pre-wrap;
        word-break: break-word;
    }

    .group-info {
        display: flex;
        flex-direction: column;
        gap: 0.1rem;   
        flex-grow: 1;      
        min-width: 0;
    }
    .group-info h3 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--color-text);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }
    .group-info span {
        font-size: 0.85rem;
        color: var(--color-text-muted);           
    }

    .card-stats-area {
        display: flex;
        flex-direction: column;
        gap: 0.8rem;
    }
    .card-stats-area h4 {
        margin: 0;
        font-size: 1rem;
        font-weight: 600;
        color: var(--color-text);
        border-bottom: 2px solid var(--color-bg-page);
        padding-bottom: 0.5rem;
    }

    .member-list {
        list-style: none;
        padding: 0;
        margin: 0;
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }

    .member-item {
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 0.6rem;
        background-color: var(--color-bg-page);
        border-radius: var(--radius-md);
        border: 1px solid var(--color-border);
    }

    .member-avatar-img {
        width: 2.2rem;
        height: 2.2rem;
        border-radius: 50%;
        object-fit: cover;
        border: 2px solid var(--color-primary); 
    }

    .member-avatar {
        display: flex;
        justify-content: center;
        align-items: center;
        width: 2.2rem;
        height: 2.2rem;
        background-color: var(--color-primary-soft);
        color: var(--color-primary);
        font-weight: 600;
        font-size: 0.95rem;
        border-radius: 50%;
        flex-shrink: 0;
    }

    .member-info-text {
        display: flex;
        flex-direction: column;
        gap: 0.1rem;
        flex-grow: 1;
        min-width: 0;
    }

    .member-name {
        display: flex;
        align-items: center;
        gap: 0.4rem;
        font-size: 0.9rem;
        font-weight: 600;
        color: var(--color-text);
    }

    .member-email {
        font-size: 0.8rem;
        color: var(--color-text-muted);
        white-space: nowrap;
        overflow: hidden;
        text-overflow: ellipsis;
    }

    .admin-badge {
        font-size: 0.7rem;
        background-color: var(--color-primary-soft);
        color: var(--color-primary);
        padding: 0.1rem 0.4rem;
        border-radius: var(--radius-sm);
        font-weight: 500;
    }

    .make-admin,
    .delete-member {
        cursor: pointer;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 2rem;
        height: 2rem;
        border-radius: 50%;
        transition: background-color 0.2s ease, transform 0.1s ease;
        flex-shrink: 0;
    }

    .make-admin svg {
        fill: #94a3b8;
    }
    .make-admin:hover {
        background-color: #e8f7f3;
    }
    .make-admin:hover svg {
        fill: var(--color-primary);
    }

    .delete-member svg {
        fill: var(--color-text-muted);
    }
    .delete-member:hover {
        background-color: var(--color-danger-bg);
    }
    .delete-member:hover svg {
        fill: var(--color-danger);
    }

    #popup-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background-color: rgba(44, 62, 80, 0.4); 
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 999;
        backdrop-filter: blur(4px); 
        padding: 1rem;
        box-sizing: border-box;
    }

    #popup-content {
        background: var(--color-bg-card);
        padding: 1.5rem;
        border-radius: var(--radius-lg);
        width: 100%;
        max-width: 28rem;
        box-shadow: 0 1rem 3rem rgba(0, 0, 0, 0.1);
        display: flex;
        flex-direction: column;
        gap: 1.25rem;
        box-sizing: border-box;
    }
    #popup-content h3 {
        margin: 0;
        font-size: 1.25rem;
        font-weight: 600;
        color: var(--color-text);
    }
    #popup-content input[type="email"],
    #popup-content input[type="text"],
    #popup-content textarea {
        width: 100%;
        padding: 0.85rem 1rem;
        font-size: 1rem;
        font-family: inherit;
        border: 1px solid var(--color-border);
        border-radius: var(--radius-md);
        outline: none;
        color: var(--color-text);
        box-sizing: border-box;
        background-color: var(--color-bg-page);
        resize: vertical;
    }
    #popup-content input[type="email"]:focus,
    #popup-content input[type="text"]:focus,
    #popup-content textarea:focus {
        border-color: var(--color-primary);
    }
    .group-photo-preview {
        width: 5rem;
        height: 5rem;
        border-radius: var(--radius-md);
        object-fit: cover;
        align-self: center;
    }
    #remove-picture-btn {
        background: none;
        border: none;
        color: var(--color-text-muted);
        text-decoration: underline;
        cursor: pointer;
        font-size: 0.85rem;
        align-self: center;
    }
    #remove-picture-btn:hover {
        color: #ef4444;
    }
    #popup-actions {
        display: flex;
        justify-content: flex-end;
        gap: 1rem;
    }
    #popup-actions button {
        border: none;
        cursor: pointer;
        border-radius: var(--radius-md);
        padding: 0.85rem 1.5rem;
        font-size: 0.95rem;
        font-weight: 600;
        flex: 1;
    }
    #cancel-btn {
        background-color: var(--color-bg-hover);
        color: var(--color-text-muted);
    }
    #create-btn {
        background-color: var(--color-primary);
        color: var(--color-on-primary);
    }

    /* Einladungslink / QR-Code (VEL-74) */
    .invite-link-section {
        border-top: 1px solid var(--color-border);
        padding-top: 1.25rem;
        display: flex;
        flex-direction: column;
        gap: 1rem;
    }
    #invite-link-btn {
        border: 1px solid var(--color-border);
        background-color: var(--color-bg-page);
        color: var(--color-text);
        border-radius: var(--radius-md);
        padding: 0.75rem 1rem;
        font-size: 0.9rem;
        font-weight: 600;
        cursor: pointer;
    }
    #invite-link-btn:disabled {
        opacity: 0.6;
        cursor: not-allowed;
    }
    .invite-link-result {
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 1rem;
    }
    .invite-qr-code {
        width: 10rem;
        height: 10rem;
    }
    .invite-link-row {
        display: flex;
        gap: 0.5rem;
        width: 100%;
    }
    .invite-link-row input {
        flex: 1;
        min-width: 0;
        padding: 0.6rem 0.75rem;
        font-size: 0.85rem;
        border: 1px solid var(--color-border);
        border-radius: var(--radius-md);
        color: var(--color-text-muted);
        background-color: var(--color-bg-page);
    }
    #copy-link-btn {
        border: none;
        border-radius: var(--radius-md);
        padding: 0.6rem 1rem;
        font-size: 0.85rem;
        font-weight: 600;
        cursor: pointer;
        background-color: var(--color-primary);
        color: var(--color-on-primary);
        flex-shrink: 0;
    }

    .loading-state {
        display: flex;
        justify-content: center;
        align-items: center;
        min-height: 100vh;
        color: var(--color-text-muted);
    }

    .member-avatar-img,
    .member-avatar {
        cursor: pointer;
    }


    @media (min-width: 480px) {
        header h3 {
            padding-left: 95px; 
        }
        .page-content {
            padding: 3rem 2rem;
        }
        .group-card {
            padding: 2rem;
        }
        .mobile-fab-btn {
            display: none;
        }
        .desktop-create-btn,
        .desktop-edit-btn {
            padding: 0.5rem 1rem;
        }
        .desktop-create-btn span,
        .desktop-edit-btn span {
            display: inline;
        }
        .desktop-invite-btn {
            display: flex;
            align-items: center;
            gap: 0.5rem;
            background-color: var(--color-primary);
            color: var(--color-on-primary);
            border: none;
            cursor: pointer;
            border-radius: var(--radius-md);
            padding: 0.6em 1.4em;
            font-size: 0.9rem;
            font-weight: 600;
            white-space: nowrap;
        }
        .desktop-invite-btn:hover {
            background-color: var(--color-primary-dark);
        }
    }
</style>