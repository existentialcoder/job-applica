<script setup lang="ts">
const addJob = () => {
  console.log("Add Job button clicked")
  // You can later open a form or send data to your API
  alert("Add Job clicked!")
}
</script>

<template>
  <div class="popup">
    <h2>Job Applica</h2>
    <button @click="addJob">Add Job</button>
  </div>
</template>

<style scoped>
.popup {
  width: 220px;
  padding: 15px;
  font-family: sans-serif;
  text-align: center;
}

h2 {
  margin-bottom: 15px;
}

button {
  padding: 8px 15px;
  background-color: #4f46e5; /* Tailwind indigo-600 */
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #4338ca; /* Darker indigo */
}
</style>
