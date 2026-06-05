<script>
//hier die Logik zur Gruppenabfrage an die DB für den eingelogten User, damit die Gruppen in der Dropdown-Liste angezeigt werden können

</script>

<template>

    <div class="group-selection-info">
        <img src="@/assets/infoButton.png" alt="Info" width="20" height="20" title="Bitte wähle optional eine Gruppe aus, der du die Strecke zuordnen möchtest."/>
        <p>Optional - Gruppenauswahl: </p>
      </div>

      <form>
        <select v-model="selectedGroup" class="group-dropdown">
          <option value="">Keine Gruppe</option>
          <option v-for="group in groups" :key="group.id" :value="group.id">  <!--v-for statt normaler schleife, damit Vue die Optionen automatisch aktualisieren kann, wenn sich die Gruppenliste ändert-->
            {{ group.name }}
          </option>
        </select>
      </form>

</template>

<style scoped>

.group-selection-info {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 8px; /* Abstand zwischen Bild und Text */
    margin-top: 15px; 
  }

  .group-selection-info p {
    margin: 0; /* Verhindert, dass das p-Tag durch Standard-Abstände das Layout verzerrt */
  }

</style>