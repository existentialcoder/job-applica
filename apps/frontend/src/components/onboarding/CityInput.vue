<script setup lang="ts">
import { watchDebounced } from '@vueuse/core';
import { computed, ref } from 'vue';
import { Autocomplete } from '@/components/ui/autocomplete';
import type { Place } from '@/lib/dataservice';
import { useProfileStore } from '@/stores/profile';

defineProps<{ modelValue: string; id?: string; placeholder?: string }>();
const emit = defineEmits<{ (e: 'update:modelValue', city: string): void; (e: 'select', place: Place): void }>();

const profileStore = useProfileStore();
// Only what the user types is searched; filling the field from a picked city must not search again.
const typed = ref('');
const places = ref<Place[]>([]);

const label = (p: Place) => [p.city, p.country].filter(Boolean).join(', ');
const suggestions = computed(() => places.value.map((p) => ({ label: label(p), value: label(p) })));

watchDebounced(
  typed,
  async (q) => {
    places.value = q.trim().length < 2 ? [] : await profileStore.searchCities(q);
  },
  { debounce: 200 }
);

function onInput(value: string) {
  typed.value = value;
  emit('update:modelValue', value);
}

function pick(value: string) {
  const place = places.value.find((p) => label(p) === value);
  if (!place) return;
  emit('update:modelValue', place.city ?? '');
  emit('select', place);
}
</script>

<template>
  <Autocomplete
    :id="id"
    :model-value="modelValue"
    :suggestions="suggestions"
    :placeholder="placeholder ?? 'e.g. Berlin'"
    @update:model-value="onInput"
    @select="pick"
  />
</template>
