<template>
  <button class="header-btn" v-bind="$attrs">
    <slot />
  </button>
</template>

<style scoped>
.header-btn {
    display: none;
    background-color: var(--color-primary);
    color: var(--color-on-primary);
    border: none;
    cursor: pointer;
    border-radius: var(--radius-md);
    padding: 0.55rem 1.2rem;
    font-size: 0.9rem;
    font-weight: 600;
    white-space: nowrap;
    transition: background-color 0.2s;
}
.header-btn:hover { background-color: var(--color-primary-dark); }

@media (min-width: 480px) {
    .header-btn { display: inline-flex; align-items: center; }
}
</style>