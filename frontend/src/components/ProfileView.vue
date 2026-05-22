<script setup>
    import { ref, onMounted } from 'vue'
    import axios from 'axios'

    const profile = ref({
        firstname: '',
        lastname: '',
        mail: '',
        profilbild: null
    })
    const newPassword = ref('')
    const confirmPassword = ref('')
    const loading = ref(false)
    const selectedFile = ref(null)
    const previewImage = ref(null)
    const onFileChange = (event) => {
        const file = event.target.files[0]
        if(!file) return
        selectedFile.value = file
        previewImage.value = URL.createObjectURL(file)
    }
    const fetchProfile = async () => {
        try{
            loading.value = true
            const response = await axios.get('http://127.0.0.1:8000/api/profil/')
            profile.value = response.data
        } catch(err) {
            console.error('Fehler: ', err)
        } finally{
            loading.value = false
        }
    }

    const updateProfile = async () => {
        if(newPassword.value || confirmPassword.value) {
            if(newPassword.value !== confirmPassword.value) {
                alert("Die passwörter stimmen nicht über ein")
                return
            }
        

            const passwordRegex = /^(?=.*[A-Z])(?=.*\d)(?=.*[a-z])[A-Za-z\d@$!%*?&]{8,20}$/
            if(!passwordRegex.test(newPassword.value)){
                alert("Das Passwort erfüllt die Anforderungen nicht!\n\n" +
                    "- Mindestens 8 Zeichen lang\n" +
                    "- Mindestens ein Großbuchstabe\n" +
                    "- Mindestens eine Zahl\n" +
                    "- Mindestens ein Kleinbuchstaben");
                return;
            }
        }
        try{
            const formData = new FormData()

            formData.append('firstname', profile.value.firstname)
            formData.append('lastname', profile.value.lastname)
            formData.append('mail', profile.value.mail)

            if(newPassword.value){
                formData.append('password', newPassword.value)
            }
            if(selectedFile.value){
                formData.append('profilbild', selectedFile.value)
            }
            const response = await axios.patch('http://127.0.0.1:8000/api/profil/', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data'
                }
            })

            profile.value = response.data

            newPassword.value = ""
            confirmPassword.value = ""
            selectedFile.value = null
        } catch(err){
            console.error('Fehler: ', err)
        }
    }

    onMounted(() => {
        fetchProfile()
    })
</script>
<template>
    <div id="outer-box">
        <form id="formular" @submit.prevent="updateProfile">
            <div id="profile-selector" class="input-group">
                <div id="profile-picture">
                    <img :src="previewImage || (profile.profilbild ? 'http://127.0.0.1:8000' + profile.profilbild : '/profile_pic.jpg')" id="picture">
                    <input type="file" accept="image/*" id="img-upload" @change="onFileChange">
                    <label for="img-upload" id="img-upload-button">
                        <svg xmlns="http://www.w3.org/2000/svg" 
                        viewBox="0 -960 960 960" 
                        fill="currentColor"
                        id="camera-icon">
                        <path d="M480-260q75 0 127.5-52.5T660-440q0-75-52.5-127.5T480-620q-75 0-127.5 52.5T300-440q0 75 52.5 127.5T480-260Zm0-80q-42 0-71-29t-29-71q0-42 29-71t71-29q42 0 71 29t29 71q0 42-29 71t-71 29ZM160-120q-33 0-56.5-23.5T80-200v-480q0-33 23.5-56.5T160-760h126l74-80h240l74 80h126q33 0 56.5 23.5T880-680v480q0 33-23.5 56.5T800-120H160Zm0-80h640v-480H638l-73-80H395l-73 80H160v480Zm320-240Z"/></svg>
                    </label>
                </div>
                <div id="profile-text">
                    <h3>Profilbild</h3>
                    <p>Klicken Sie auf das Kamera-Symbol, um ein neues Bild hochzuladen</p>
                </div>
            </div>
            <div id="personal-info" class="input-group">
                <h3><svg xmlns="http://www.w3.org/2000/svg" 
                    height="24px" 
                    viewBox="0 -960 960 960" 
                    width="24px" 
                    fill="#0A8B7B">
                    <path d="M367-527q-47-47-47-113t47-113q47-47 113-47t113 47q47 47 47 113t-47 113q-47 47-113 47t-113-47ZM160-160v-112q0-34 17.5-62.5T224-378q62-31 126-46.5T480-440q66 0 130 15.5T736-378q29 15 46.5 43.5T800-272v112H160Zm80-80h480v-32q0-11-5.5-20T700-306q-54-27-109-40.5T480-360q-56 0-111 13.5T260-306q-9 5-14.5 14t-5.5 20v32Zm296.5-343.5Q560-607 560-640t-23.5-56.5Q513-720 480-720t-56.5 23.5Q400-673 400-640t23.5 56.5Q447-560 480-560t56.5-23.5ZM480-640Zm0 400Z"/></svg>
                    Persönliche Informationen</h3>
                <div id="names">
                    <div class="name-field">
                        <label for="vorname">Vorname</label>
                        <input type="text" placeholder="Vorname" id="vorname" v-model="profile.firstname">
                    </div>
                    <div class="name-field">
                        <label for="nachname">Nachname</label>
                        <input type="text" placeholder="Nachname" id="nachname" v-model="profile.lastname">
                    </div>
                </div>
                <div class="email-field">
                    <label for="mail"><svg xmlns="http://www.w3.org/2000/svg" 
                        height="24px" 
                        viewBox="0 -960 960 960" 
                        width="24px" 
                        fill="currentColor">
                        <path d="M160-160q-33 0-56.5-23.5T80-240v-480q0-33 23.5-56.5T160-800h640q33 0 56.5 23.5T880-720v480q0 33-23.5 56.5T800-160H160Zm320-280L160-640v400h640v-400L480-440Zm0-80 320-200H160l320 200ZM160-640v-80 480-400Z"/></svg>
                        Email</label>
                    <input type="email" placeholder="julius@mail.de" id="mail" v-model="profile.mail">
                </div>
            </div>
            <div id="password" class="input-group">
                <h3><svg xmlns="http://www.w3.org/2000/svg" 
                    height="24px" 
                    viewBox="0 -960 960 960" 
                    width="24px" 
                    fill="#0A8B7B">
                    <path d="M240-80q-33 0-56.5-23.5T160-160v-400q0-33 23.5-56.5T240-640h40v-80q0-83 58.5-141.5T480-920q83 0 141.5 58.5T680-720v80h40q33 0 56.5 23.5T800-560v400q0 33-23.5 56.5T720-80H240Zm0-80h480v-400H240v400Zm296.5-143.5Q560-327 560-360t-23.5-56.5Q513-440 480-440t-56.5 23.5Q400-393 400-360t23.5 56.5Q447-280 480-280t56.5-23.5ZM360-640h240v-80q0-50-35-85t-85-35q-50 0-85 35t-35 85v80ZM240-160v-400 400Z"/>
                </svg>Passwort ändern</h3>
                <div id="password-change">
                    <div class="name-field">
                        <label>Neues Passwort</label>
                        <input type="password" v-model="newPassword">
                    </div>
                    <div class="name-field">
                        <label>Passwort bestätigen</label>
                        <input type="password" v-model="confirmPassword">
                    </div>
                </div>

            </div>
            <button type="submit" id="save"><svg xmlns="http://www.w3.org/2000/svg" 
                height="24px" 
                viewBox="0 -960 960 960" 
                width="24px" 
                fill="#FFFFFF">
                <path d="M840-680v480q0 33-23.5 56.5T760-120H200q-33 0-56.5-23.5T120-200v-560q0-33 23.5-56.5T200-840h480l160 160Zm-80 34L646-760H200v560h560v-446ZM565-275q35-35 35-85t-35-85q-35-35-85-35t-85 35q-35 35-35 85t35 85q35 35 85 35t85-35ZM240-560h360v-160H240v160Zm-40-86v446-560 114Z"/>
            </svg>Änderungen speichern</button>
        </form>
    </div>
</template>
<style scoped>
    
    #outer-box{
        padding: 1.5rem;
        min-height: 100vh;
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
        align-items: center;
        background-color: #f5f7f8;
    }
    #formular{
        width: 90%;
        max-width: 600px;
        display: flex;
        flex-direction: column;
        gap: 2rem;
        margin: auto 0;
    }
    img{
        border-radius: 50%;
        border: 0.3rem solid #0A8B7B;
        width: 7rem;
        height: 7rem;
        object-fit: cover;
    }
    #img-upload{
        display: none;
    }
    #img-upload-button{
        position: absolute;
        border-radius: 50%;
        background-color: #009F8C;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 2.5rem;
        height: 2.5rem;
        cursor: pointer;    
        color:black;
        font-size: 1.7em;
        bottom: 0;
        right: 0;
    }
    #camera-icon{
        width: 1em;
        height: 1em;
    }
    .input-group{
        background-color: #FAFAFA;
        padding: 2rem;
        border-radius: 1rem;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
    }
    #profile-selector{
        display: flex;
        align-items: center;
        gap: 1.5rem;
    }
    @media (max-width: 480px) {
        #profile-selector {
            flex-direction: column; /* Bild und Text UNTEREINANDER stapeln */
            text-align: center; /* Text mittig ausrichten */
            gap: 1.2rem;
        }

        #profile-text {
            width: 100%;
        }
    }
    #profile-picture{
        position: relative;
    }
    #personal-info{
        display: flex;
        flex-direction: column;
        gap: 0.5rem;
    }
    #names, #password-change{
        display: flex;
        gap: 1rem;
        width: 100%;
        align-items: flex-start;
    }
    @media (max-width: 480px) {
        #names, #password-change {
            flex-direction: column;
            gap: 1.2rem;
            align-items: stretch;
        }
    }
    .name-field, .email-field{
        display: flex;
        gap: 0.5rem;
        flex-direction: column;
        flex: 1;
    }
    .email-field{
        width: 100%;
    }
    input{
        padding: 0.75rem;
        border-radius: 0.5rem;
        border: 1px solid black;
        box-sizing: border-box;
        width: 100%;
    }
    h3, label, #save{
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    #password-change, #names, .email-field{
        margin-top: 1rem;
    }
    #save{
        background-color:#009F8C;
        border: none;
        color: white;
        border-radius: 1rem;
        display: flex;
        justify-content: center;
        padding: 1rem;
        font-size: medium;
    }
    input:focus{
        outline: none;
        border-color: #0A8B7B;
    }
</style>