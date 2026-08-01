<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Combobox, type ComboboxOption } from '@/components/ui/combobox'
import dataservice from '@/lib/dataservice'

defineProps<{
  modelValue: string
  placeholder?: string
  class?: string
}>()

defineEmits<{
  (e: 'update:modelValue', val: string): void
}>()

const cities = ref<ComboboxOption[]>([])

onMounted(async () => {
  const results = await dataservice.getCities()
  cities.value = results.map((city) => ({ label: city, value: city }))
})
</script>

<template>
  <Combobox
    :options="cities"
    :model-value="modelValue"
    :placeholder="placeholder ?? 'Select city'"
    creatable
    :class="$props.class"
    @update:model-value="$emit('update:modelValue', $event)"
  />
</template>
