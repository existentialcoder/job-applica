<script setup lang="ts">
import { computed, onBeforeUnmount, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuthStore } from '@/stores/auth';

const STAY_MS = 2500;
const COLORS = ['bg-primary', 'bg-primary/60', 'bg-primary/30', 'bg-muted-foreground/50'];
const BITS = Array.from({ length: 16 }, (_, i) => {
  const angle = (i / 16) * Math.PI * 2 + 0.2;
  const distance = 120 + (i % 3) * 28;
  const bar = i % 2 === 0;
  return {
    class: [COLORS[i % COLORS.length], bar ? 'w-[5px] h-3.5 rounded-sm' : 'size-[9px] rounded-full'],
    style: {
      '--dx': `${Math.round(Math.cos(angle) * distance)}px`,
      '--dy': `${Math.round(Math.sin(angle) * distance)}px`,
      '--r': `${i * 47}deg`
    }
  };
});

const router = useRouter();
const authStore = useAuthStore();
const heading = computed(() =>
  authStore.user?.first_name ? `You're all set, ${authStore.user.first_name}` : "You're all set"
);

let timer: ReturnType<typeof setTimeout> | undefined;
onMounted(() => {
  timer = setTimeout(() => router.replace('/home'), STAY_MS);
});
onBeforeUnmount(() => clearTimeout(timer));
</script>

<template>
  <div class="flex flex-col items-center justify-center gap-7 pt-24 text-center">
    <div class="relative size-28" aria-hidden="true">
      <span v-for="(bit, i) in BITS" :key="i" class="bit absolute left-1/2 top-1/2 block" :class="bit.class" :style="bit.style" />
      <span class="pop absolute inset-0 rounded-full bg-primary/10 text-primary flex items-center justify-center">
        <Icon name="Check" :size="52" :stroke-width="2.5" />
      </span>
    </div>
    <h1 class="rise text-[28px] font-bold tracking-tight">{{ heading }}</h1>
  </div>
</template>

<style scoped>
.pop {
  animation: pop 0.75s ease-out both;
}

.bit {
  opacity: 0;
  animation: burst 1.3s cubic-bezier(0.2, 0.7, 0.3, 1) 0.1s both;
}

.rise {
  animation: rise 0.5s ease-out 0.45s both;
}

@keyframes pop {
  0% {
    transform: scale(0);
    opacity: 0;
  }
  50% {
    transform: scale(1.18);
    opacity: 1;
  }
  75% {
    transform: scale(0.94);
  }
  100% {
    transform: scale(1);
    opacity: 1;
  }
}

@keyframes burst {
  0% {
    transform: translate(-50%, -50%) scale(0.4);
    opacity: 0;
  }
  10% {
    opacity: 1;
  }
  55% {
    transform: translate(-50%, -50%) translate(var(--dx), var(--dy)) rotate(var(--r));
    opacity: 1;
  }
  100% {
    transform: translate(-50%, -50%) translate(var(--dx), calc(var(--dy) + 36px)) rotate(var(--r));
    opacity: 0;
  }
}

@keyframes rise {
  from {
    opacity: 0;
    transform: translateY(12px);
  }
  to {
    opacity: 1;
    transform: none;
  }
}

@media (prefers-reduced-motion: reduce) {
  .pop,
  .rise {
    animation: none;
  }

  .bit {
    display: none;
  }
}
</style>
