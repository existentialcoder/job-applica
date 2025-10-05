<script setup lang="ts">
import { ref, onMounted } from 'vue';
import dataservice from './lib/dataservice';

const isLinkedInJob = ref(false);
const jobId = ref<string | null>(null);
const jobLink = ref<string | null>(null);
const jobDescription = ref<string | null>(null);
const jobLocation = ref<string | null>(null); // New field for job location
const jobTitle = ref(''); // placeholder, could be fetched
const company = ref(''); // placeholder, could be fetched
const jobStatus = ref('Saved');
const alreadyExists = ref(false);
const isSaveBtnLoading = ref(false);

const addMessageListener = (callback: any) => {
  if (typeof chrome !== 'undefined' && chrome.runtime?.onMessage?.addListener) {
    chrome.runtime.onMessage.addListener(callback);
  } else if (typeof browser !== 'undefined' && browser.runtime?.onMessage?.addListener) {
    browser.runtime.onMessage.addListener(callback);
  }
};


async function setupData() {
  const currentLocation = await dataservice.getCurrentTabUrl();
  if (!currentLocation) return;
  isLinkedInJob.value = currentLocation.includes('linkedin.com') && currentLocation.includes('currentJobId');

  if (isLinkedInJob.value) {
    jobId.value = new URL(currentLocation).searchParams.get('currentJobId');
    alreadyExists.value = await dataservice.checkJobExists(jobId.value || '');
    jobLink.value = currentLocation;

    addMessageListener((msg: any) => {
      if (msg.jobTitle) jobTitle.value = msg.jobTitle;
      if (msg.company) company.value = msg.company;
      if (msg.location) jobLocation.value = msg.location;
      if (msg.jobDescription) jobDescription.value = msg.jobDescription;
    });
    await dataservice.fetchJobDataFromContentScript();
  }
}

onMounted(async () => {
  await setupData();
});

const addOrUpdateJob = async () => {
  isSaveBtnLoading.value = true;
  const success = await dataservice.createJob({
    job_title: `${jobId.value}:${jobTitle.value}`,
    company: company.value || '',
    location: jobLocation.value || '',
    status: jobStatus.value,
    // each job board is a category
    category: 'default',
    required_skills: [],
    job_description: jobDescription.value?.trim() || ''
  });

  isSaveBtnLoading.value = false;
  if (success) {
    console.log('Job added successfully!');
  } else {
    console.error('Failed to add job. Please try again.');
  }
};
</script>

<template>
  <div class="popup-container w-full p-4 bg-white dark:bg-gray-800 rounded-lg shadow-md flex flex-col gap-4">
    <h2 class="text-xl font-semibold text-gray-900 dark:text-gray-100 text-center">Job Applica</h2>

    <div v-if="isLinkedInJob">
      <form @submit.prevent="addOrUpdateJob" class="flex flex-col gap-3 w-full">
        <!-- Job Title -->
        <div class="flex flex-col w-full">
          <label for="jobTitle" class="text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Job Title</label>
          <input id="jobTitle" type="text" v-model="jobTitle" disabled :title="jobTitle"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 cursor-not-allowed" />
        </div>

        <!-- Company -->
        <div class="flex flex-col w-full">
          <label for="company" class="text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Company</label>
          <input id="company" type="text" v-model="company" disabled :title="company"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 cursor-not-allowed" />
        </div>

        <!-- Location -->
        <div class="flex flex-col w-full">
          <label for="location" class="text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Location</label>
          <input id="location" type="text" v-model="jobLocation" disabled :title="jobLocation"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-200 cursor-not-allowed" />
        </div>

        <!-- Job Status -->
        <div class="flex flex-col w-full">
          <label for="jobStatus" class="text-sm font-medium text-gray-700 dark:text-gray-200 mb-1">Job Status</label>
          <select id="jobStatus" v-model="jobStatus"
            class="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md bg-white dark:bg-gray-700 text-gray-700 dark:text-gray-200 focus:outline-none focus:ring-2 focus:ring-blue-500">
            <option>Saved</option>
            <option>Applied</option>
          </select>
        </div>

        <!-- Add Job Button -->
        <button type="submit" :disabled="isSaveBtnLoading"
          class="w-full px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700 dark:bg-blue-500 dark:hover:bg-blue-600 transition flex items-center justify-center gap-2 disabled:opacity-50 disabled:cursor-not-allowed">
          <svg v-if="isSaveBtnLoading" class="w-4 h-4 animate-spin text-white" xmlns="http://www.w3.org/2000/svg"
            fill="none" viewBox="0 0 24 24">
            <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
            <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v4a4 4 0 00-4 4H4z"></path>
          </svg>
          <span>{{ isSaveBtnLoading ? 'Saving...' : alreadyExists ? 'Update Job' : 'Add Job' }}</span>
        </button>
      </form>
    </div>

    <div v-else class="text-sm text-gray-500 dark:text-gray-400 text-center">
      No active jobs found on this page.
    </div>

    <!-- Dashboard Button -->
    <a href="http://localhost:5173/applications" target="_blank"
      class="w-full block text-center px-4 py-2 bg-gray-200 text-gray-800 rounded hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-100 dark:hover:bg-gray-600 transition mt-2">
      Go to Dashboard
    </a>
  </div>
</template>

<style scoped>
/* Optional: force popup width for browser extension */
.popup-container {
  min-width: 320px;
  max-width: 360px;
}
</style>
