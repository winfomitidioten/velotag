
<script setup>
</script>

<template>
  <RouterView />
</template>

<style>
html, body {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
  background-color: #f5f7f8; /* Der sanfte Grauton für die ECHTE gesamte Seite */
  font-family: sans-serif;
  box-sizing: border-box;
}

#app {
  width: 100%;
  min-height: 100%;
  display: flex;
  flex-direction: column;
}
</style>