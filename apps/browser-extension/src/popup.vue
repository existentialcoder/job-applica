<script setup lang='ts'>
import { ref, onMounted } from 'vue';

import dataservice from './lib/dataservice';

import { Button } from './components/ui/button';
import { Input } from './components/ui/input';
import { Checkbox } from './components/ui/checkbox';
import { Label } from './components/ui/label';
import { FormControl, FormField, FormLabel, FormItem } from './components/ui/form';

const isLinkedInJob = ref(false);

const userName = ref('');

const appSettings = ref({});

onMounted(() => {
  const location = window.location.href;
  isLinkedInJob.value = location.includes('linkedin.com') && location.includes('currentJobId');

  userName.value = dataservice.getUserName();
  appSettings.value = dataservice.getAppSettings();
});

const addJob = () => {
  console.log('Add Job button clicked')
  // You can later open a form or send data to your API
  alert('Add Job clicked!')
}
</script>

<template>
  <div class='popup-container'>
    <h2>Job Applica</h2>
    <div v-if='isLinkedInJob' class='job-container'>
      <form @submit="onSubmit">
        <FormField v-slot="{ componentField }" name="email">
          <FormItem class="mb-4">
            <FormLabel>Email</FormLabel>
            <FormControl>
              <Input type="text" placeholder="example@mail.com" v-bind="componentField" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <FormField v-slot="{ componentField }" name="password">
          <FormItem>
            <FormLabel>Password</FormLabel>
            <FormControl>
              <Input type="password" v-bind="componentField" />
            </FormControl>
            <FormMessage />
          </FormItem>
        </FormField>
        <div class="flex items-center space-x-2 mt-4">
          <Checkbox id="terms" />
          <Label for="terms">Remember Me</Label>
        </div>
      </form>
    </div>

    <div v-else class="mb-4 text-sm text-muted-foreground">
        No active jobs found on this page.
    </div>

    <div class="mb-4">
      <Button v-show="isLinkedInJob" @click="addJob" variant="secondary" size="sm">
        Add Job
      </Button>
      <Button variant="primary" size="sm" @click="window.open('http://localhost:5173', '_blank')">
        Go to Dashboard
      </Button>
    </div>
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
  background-color: #4f46e5;
  /* Tailwind indigo-600 */
  color: white;
  border: none;
  border-radius: 5px;
  cursor: pointer;
}

button:hover {
  background-color: #4338ca;
  /* Darker indigo */
}
</style>
