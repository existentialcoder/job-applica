<script setup lang="ts">
import { ref } from 'vue';
import { Button } from '@/components/ui/button';
import { Combobox } from '@/components/ui/combobox';
import { Label } from '@/components/ui/label';
import { Select, SelectContent, SelectGroup, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { LANGUAGE_OPTIONS } from '@/lib/constants';
import type { Language } from '@/lib/profile';

const LEVELS = ['A1', 'A2', 'B1', 'B2', 'C1', 'C2', 'Native'];
const OPTIONS = LANGUAGE_OPTIONS.map((l) => ({ label: l, value: l }));

const props = defineProps<{ entry: Language | null }>();
const emit = defineEmits<{ (e: 'save', entry: Language): void; (e: 'cancel'): void }>();

const name = ref(props.entry?.name ?? '');
const level = ref(props.entry?.level ?? '');
</script>

<template>
  <form
    class="flex flex-col gap-4 rounded-lg border border-border p-4"
    @submit.prevent="emit('save', { name: name.trim(), level: level || null })"
  >
    <div class="grid gap-4 md:grid-cols-2">
      <div class="flex flex-col gap-1.5">
        <Label>Language</Label>
        <Combobox v-model="name" :options="OPTIONS" placeholder="Select a language" creatable />
      </div>
      <div class="flex flex-col gap-1.5">
        <Label>Level</Label>
        <Select v-model="level">
          <SelectTrigger>
            <SelectValue placeholder="Select a level" />
          </SelectTrigger>
          <SelectContent>
            <SelectGroup>
              <SelectItem v-for="l in LEVELS" :key="l" :value="l">{{ l }}</SelectItem>
            </SelectGroup>
          </SelectContent>
        </Select>
      </div>
    </div>
    <div class="flex justify-end gap-2">
      <Button type="button" variant="ghost" @click="emit('cancel')">Cancel</Button>
      <Button type="submit" :disabled="!name.trim()">Save</Button>
    </div>
  </form>
</template>
