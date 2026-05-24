<script setup>
</script>

<template>
  <RouterView />
</template>

<style>
/* WICHTIG: Kein "scoped" hier! Diese Regeln müssen für die ganze Seite gelten. */
html, body, #app {
  margin: 0;
  padding: 0;
  width: 100%;
  height: 100%;
}
</style>
