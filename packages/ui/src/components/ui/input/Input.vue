<script setup lang="ts">
import { computed, ref, type HTMLAttributes } from 'vue'
import { useVModel } from '@vueuse/core'
import { cn } from '@/lib/utils'

defineOptions({ inheritAttrs: false })

const props = defineProps<{
  defaultValue?: string | number
  modelValue?: string | number
  prependIcon?: string
  placeholder?: string
  type?: string
  class?: HTMLAttributes['class'],
}>()

const emits = defineEmits<{
  (e: 'update:modelValue', payload: string | number): void
  (e: 'focus', payload: FocusEvent & { isFocused: boolean }): void
  (e: 'blur', payload: FocusEvent & { isFocused: boolean }): void
  (e: 'keydown', payload: KeyboardEvent): void
}>()

const modelValue = useVModel(props, 'modelValue', emits, {
  passive: true,
  defaultValue: props.defaultValue,
})
const isFocused = ref<boolean>(false);
const onFocus = (e: FocusEvent) => {
  isFocused.value = true;
  emits('focus', { ...e, isFocused: isFocused.value })
};
const onBlur = (e: FocusEvent) => {
  isFocused.value = false;
  emits('blur', { ...e, isFocused: isFocused.value })
};
const onKeydown = (e: KeyboardEvent) => {
  emits('keydown', e);
};

const isPassword = computed(() => props.type === 'password');
const showPassword = ref(false);
const resolvedType = computed(() => (isPassword.value && showPassword.value) ? 'text' : (props.type ?? 'text'));
</script>

<template>
  <div class="relative">
    <Icon v-if="prependIcon" :name="prependIcon" class="text-slate-500 absolute h-4 top-1/2 -translate-y-1/2 left-4"></Icon>
    <input
      v-bind="$attrs"
      :type="resolvedType"
      :class="[
        cn('flex h-10 w-full rounded-md border border-input bg-background px-3 py-2 text-sm ring-offset-background file:border-0 file:bg-transparent file:text-sm file:font-medium placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50', props.class),
        prependIcon ? 'pl-12 left-placeholder' : '',
        isPassword ? 'pr-10' : ''
      ]"
      v-model="modelValue"
      :placeholder="placeholder"
      @focus="onFocus"
      @blur="onBlur"
      @keydown="onKeydown"
    >
    <button
      v-if="isPassword"
      type="button"
      tabindex="-1"
      class="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
      @click="showPassword = !showPassword"
    >
      <Icon :name="showPassword ? 'EyeOff' : 'Eye'" class="h-4 w-4"></Icon>
    </button>
  </div>
</template>
