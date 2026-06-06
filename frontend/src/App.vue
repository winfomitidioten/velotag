<script setup>
import { RouterView, useRoute } from 'vue-router'
import { onMounted } from 'vue'
import MenuBar from '@/components/MenuBar.vue'
import { useUserStore } from '@/store/userStore'

const route = useRoute();
const userStore = useUserStore();

onMounted(async () => {
  if (localStorage.getItem('auth_token')) {
    await userStore.fetchProfile();
  }
});

</script>

<template>
  <MenuBar v-if="!route.meta.hideMenu" />
  <RouterView />
</template>

<style>
/* html und body funktionieren in <style scoped> nicht! 
   Daher bleibt das hier ohne 'scoped', damit der graue Hintergrund überall gilt. */
html, body, #app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  background-color: #f5f7f8;
  font-family: sans-serif;
  box-sizing: border-box;
}

#app {
  display: flex;
  flex-direction: column;
}
</style>