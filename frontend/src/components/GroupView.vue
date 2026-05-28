<script setup>
    import { ref } from 'vue'
    const groups = ref([{name: 'Gruppe1'}, {name: 'Gruppe2'}])
</script>
<template>
    <header>
        <h3>Meine Gruppen</h3>
        <button> + Neue Gruppe</button>
    </header>
    <main>
        <div id="all-groups">
            <li v-for="group in groups">
                <div id="group-card">
                    {{ group.name }}
                </div>  
            </li>
        </div>
    </main>
</template>
<style scoped>
    header{
        display: flex;
    }
</style>