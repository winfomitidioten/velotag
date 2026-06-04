<script setup>
import { useRoute } from 'vue-router'
import { ref, onMounted } from 'vue'


const route = useRoute()
const groupId = route.params.id
const group = ref(null)
const loading = ref(false)

const fetchGroup = async () => {
    try{
        loading.value = true;
        const response = api.await('groups/${groupID}/');
        group.value = reponse.data;
    } catch(err) {
        console.error('Fehler: ', err)
    } finally {
        loading.value = false;
    }
}

onMounted(() => {
    fetchGroup();
})
</script>
<template>
    <div class="page-container">
        <header>
            <h3>Test</h3>
        </header>
        <main class="page-contet">

        </main>
    </div>
</template>
<style scoped>
.page-container {
        min-height: 100vh;
        background-color: #f8f9fa;
        display: flex;
        flex-direction: column;
    }

    header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        width: 100%;
        background-color: #ffffff;
        box-shadow: 0 0.2rem 0.6rem rgba(0, 0, 0, 0.05);
        box-sizing: border-box;
        padding: 1.2rem 2rem;
    }
    header h3 {
        font-size: 1.25rem;
        font-weight: 500;
        margin: 0;
        color: #2c3e50;
    }
</style>