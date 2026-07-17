<script setup lang="ts">
import { type HTMLAttributes, computed } from 'vue'
import { TabsContent, type TabsContentProps } from 'radix-vue'
import { cn } from '@/lib/utils'

const props = defineProps<TabsContentProps & {
  class?: HTMLAttributes['class']
  /**
   * When true the content fills its parent flex container and scrolls
   * internally. Use inside a panel/sheet where the parent is a flex column
   * with a constrained height (e.g. 100vh). Removes the default mt-2 margin.
   */
  fill?: boolean
}>()

const delegatedProps = computed(() => {
  const { class: _, fill: __, ...delegated } = props
  return delegated
})
</script>

<template>
  <TabsContent
    :class="cn(
      'ring-offset-background focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2',
      fill ? '!mt-0' : 'mt-2',
      props.class,
    )"
    :style="fill ? 'flex:1; min-height:0; overflow-y:auto;' : undefined"
    v-bind="delegatedProps"
  >
    <slot />
  </TabsContent>
</template>
