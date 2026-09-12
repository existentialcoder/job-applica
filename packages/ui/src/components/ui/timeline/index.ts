import { type VariantProps, cva } from 'class-variance-authority'

export { default as Timeline } from './Timeline.vue'
export { default as TimelineItem } from './TimelineItem.vue'
export { default as TimelineDot } from './TimelineDot.vue'
export { default as TimelineContent } from './TimelineContent.vue'
export { default as TimelineHeader } from './TimelineHeader.vue'
export { default as TimelineTitle } from './TimelineTitle.vue'
export { default as TimelineDescription } from './TimelineDescription.vue'
export { default as TimelineTime } from './TimelineTime.vue'

export const timelineDotVariants = cva(
  'relative z-10 flex shrink-0 items-center justify-center rounded-full ring-4 ring-background',
  {
    variants: {
      variant: {
        default: 'bg-primary text-primary-foreground',
        secondary: 'bg-secondary text-secondary-foreground',
        muted: 'bg-muted text-muted-foreground',
        success: 'dark:bg-emerald-600 bg-emerald-500 text-white',
        warning: 'dark:bg-amber-500 bg-amber-500 text-white',
        destructive: 'bg-destructive text-destructive-foreground',
      },
      size: {
        sm: 'h-2.5 w-2.5',
        md: 'h-3.5 w-3.5',
        lg: 'h-7 w-7',
      },
    },
    defaultVariants: {
      variant: 'default',
      size: 'md',
    },
  },
)

export type TimelineDotVariants = VariantProps<typeof timelineDotVariants>
