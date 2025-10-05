<script setup lang="ts">
import { ref, onMounted } from 'vue';
import type { JobData } from '@/lib/types';
import {
  Select,
  SelectContent,
  SelectGroup,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';

import { Button } from '@/components/ui/button';

import dataservice from '@/lib/dataservice';

import { TableApplications } from '@/components/applications';

import { Label } from '@/components/ui/label';

const selectedLayout = ref('table');

const allJobs = ref<JobData[]>([]);

const selectedJobs = ref<JobData[]>([]);

async function setAllJobs() {
  const res = await dataservice.getJobs();
  allJobs.value = res;
}

function onTableSelectionChange(val: any) {
  selectedJobs.value = val;
}

async function deleteSelectedJobs() {
  if (selectedJobs.value.length === 0) return;

  const idsToDelete = selectedJobs.value.map((job) => job.id);
  await Promise.all(idsToDelete.map((id) => dataservice.deleteJob(id)));
  await setAllJobs();
}

onMounted(() => {
  setAllJobs();
});

</script>

<template>
  <div class="mb-4">
    <div class="flex float-end">
      <div class="btn-container" v-if="selectedJobs.length > 0">
        <Button size="icon" class="mr-4" @click="deleteSelectedJobs">
          <Icon name="Trash" class="w-4 h-4" />
        </Button>
        <!-- <Button size="icon" class="mr-4" v-if="selectedJobs.length === 1" @click="openEditJobModal">
          <Icon name="Edit" class="w-4 h-4" />
        </Button> -->
      </div>
      <div class="flex">
        <Label class="mr-1 mt-3">Layout: </Label>
        <Select defaultValue="table">
          <SelectTrigger placeholder="Select Layout" class="w-[100px] ml-2">
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectItem value="table">
                Table
              </SelectItem>
              <SelectItem value="board">
                Board
              </SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>
    </div>

    <div class="clear-both"></div>

    <div class="mt-3">
      <TableApplications :jobs="allJobs" @selection-change="onTableSelectionChange" v-if="selectedLayout === 'table'" />
      <!-- <BoardApplications :jobs="allJobs" v-else /> -->
    </div>
  </div>
</template>
