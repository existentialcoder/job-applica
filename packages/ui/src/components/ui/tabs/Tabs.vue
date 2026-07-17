<script setup lang="ts">
import { TabsRoot, useForwardPropsEmits } from 'radix-vue'
import type { TabsRootEmits, TabsRootProps } from 'radix-vue'

defineOptions({ inheritAttrs: false })

const props = defineProps<TabsRootProps>()
const emits = defineEmits<TabsRootEmits>()

const forwarded = useForwardPropsEmits(props, emits)
</script>

<template>
  <TabsRoot v-bind="{ ...forwarded, ...$attrs }">
    <slot />
  </TabsRoot>
</template>
