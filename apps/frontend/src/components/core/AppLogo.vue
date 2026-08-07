<script setup lang="ts">
withDefaults(
  defineProps<{
    collapsed?: boolean
    showIcon?: boolean
    showBrandName?: boolean
  }>(),
  {
    collapsed: false,
    showIcon: true,
    showBrandName: true
  }
)
</script>

<template>
  <div class="inline-flex items-center gap-2.5 select-none">
    <!-- Dew-drop icon mark -->
    <svg
      v-if="showIcon"
      xmlns="http://www.w3.org/2000/svg"
      viewBox="20 0 432 480"
      class="flex-shrink-0 w-8 h-8"
      aria-hidden="true"
    >
      <defs>
        <linearGradient id="logo-dew" x1="0%" y1="0%" x2="100%" y2="100%">
          <stop offset="0%" stop-color="#4F46E5" />
          <stop offset="100%" stop-color="#7C3AED" />
        </linearGradient>
      </defs>
      <path
        fill="url(#logo-dew)"
        d="M 430,112 C 452,222 362,470 230,470 A 200,200 0 0 1 30,270 C 30,78 172,8 430,112 Z"
      />
      <circle cx="248" cy="154" r="22" fill="white" />
      <path
        fill="white"
        d="M 231,194 L 265,194 L 265,360 Q 265,442 210,442 Q 172,442 172,406 L 172,388 Q 172,418 210,418 Q 248,418 248,360 L 248,194 Z"
      />
    </svg>

    <span
      v-if="showBrandName && !collapsed"
      class="text-[17px] font-semibold tracking-tight leading-none whitespace-nowrap"
    >
      <span class="text-foreground">Job</span><span class="text-[#818CF8]">Applica</span>
    </span>
  </div>
</template>
