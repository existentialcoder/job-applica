<script setup lang="ts">
import { RouterLink } from 'vue-router';
import AppLogo from '@/components/core/AppLogo.vue';
import { Button } from '@/components/ui/button';
</script>

<template>
  <div class="min-h-screen flex flex-col bg-background">
    <header class="h-16 shrink-0 flex items-center px-4 lg:px-8 border-b border-border bg-card">
      <RouterLink to="/home" aria-label="JobApplica home">
        <AppLogo />
      </RouterLink>
    </header>
    <main class="flex-1 flex flex-col items-center justify-center gap-6 px-4 pt-10 pb-[15vh] text-center">
      <svg
        class="w-full max-w-[360px]"
        viewBox="0 46 320 108"
        fill="none"
        stroke-linecap="round"
        stroke-linejoin="round"
        aria-hidden="true"
      >
        <line x1="10" y1="150" x2="310" y2="150" class="stroke-border" stroke-width="3" />
        <line x1="262" y1="150" x2="262" y2="88" class="stroke-muted-foreground" stroke-width="3" />
        <path d="M222 66 H296 V88 H222 L212 77 Z" class="fill-card stroke-primary" stroke-width="2" />
        <text x="256" y="81" text-anchor="middle" class="fill-primary text-[11px] font-semibold">Interviews</text>
        <rect x="228" y="96" width="68" height="24" rx="4" class="fill-muted stroke-border" stroke-width="2" />
        <text x="262" y="112" text-anchor="middle" class="fill-muted-foreground text-[11px] font-semibold">Dead end</text>
        <g class="walker">
          <g class="body stroke-foreground" stroke-width="3">
            <circle cx="0" cy="-64" r="9" class="fill-background" />
            <line x1="0" y1="-55" x2="0" y2="-26" />
            <line x1="0" y1="-48" x2="-9" y2="-34" />
            <line x1="0" y1="-48" x2="9" y2="-34" />
            <rect x="4" y="-34" width="15" height="11" rx="2" class="fill-primary stroke-primary" stroke-width="2" />
            <line class="leg leg-a" x1="0" y1="-26" x2="0" y2="0" />
            <line class="leg leg-b" x1="0" y1="-26" x2="0" y2="0" />
          </g>
          <text x="8" y="-80" class="huh fill-primary text-[22px] font-bold">?</text>
        </g>
      </svg>
      <div class="flex flex-col gap-2">
        <h1 class="text-2xl font-bold tracking-tight">Don't get lost in your job search</h1>
        <p class="sr-only">Page not found.</p>
      </div>
      <Button as-child>
        <RouterLink to="/home">Return home</RouterLink>
      </Button>
    </main>
  </div>
</template>

<style scoped>
/* One 9s loop drives every part: walk in, stop at the dead end, "?", turn round, walk back out. */
.walker {
  animation: walk 9s linear infinite;
}

.body,
.leg {
  transform-box: view-box;
}

.body {
  animation: turn 9s step-end infinite;
}

.leg {
  transform-origin: 0 -26px;
}

.leg-a {
  animation: stride-a 9s ease-in-out infinite;
}

.leg-b {
  animation: stride-b 9s ease-in-out infinite;
}

.huh {
  opacity: 0;
  animation: huh 9s ease-out infinite;
}

@keyframes walk {
  0% { transform: translate(30px, 150px); opacity: 0; }
  5% { transform: translate(40px, 150px); opacity: 1; }
  45%, 65% { transform: translate(196px, 150px); }
  94% { transform: translate(70px, 150px); opacity: 1; }
  100% { transform: translate(60px, 150px); opacity: 0; }
}

@keyframes turn {
  0% { transform: scaleX(1); }
  62% { transform: scaleX(-1); }
}

@keyframes stride-a {
  5% { transform: rotate(22deg); }
  10% { transform: rotate(-22deg); }
  15% { transform: rotate(22deg); }
  20% { transform: rotate(-22deg); }
  25% { transform: rotate(22deg); }
  30% { transform: rotate(-22deg); }
  35% { transform: rotate(22deg); }
  40% { transform: rotate(-22deg); }
  45% { transform: rotate(22deg); }
  46%, 65% { transform: rotate(10deg); }
  66% { transform: rotate(22deg); }
  71% { transform: rotate(-22deg); }
  76% { transform: rotate(22deg); }
  81% { transform: rotate(-22deg); }
  86% { transform: rotate(22deg); }
  91% { transform: rotate(-22deg); }
  0%, 4%, 95%, 100% { transform: rotate(10deg); }
}

@keyframes stride-b {
  5% { transform: rotate(-22deg); }
  10% { transform: rotate(22deg); }
  15% { transform: rotate(-22deg); }
  20% { transform: rotate(22deg); }
  25% { transform: rotate(-22deg); }
  30% { transform: rotate(22deg); }
  35% { transform: rotate(-22deg); }
  40% { transform: rotate(22deg); }
  45% { transform: rotate(-22deg); }
  46%, 65% { transform: rotate(-10deg); }
  66% { transform: rotate(-22deg); }
  71% { transform: rotate(22deg); }
  76% { transform: rotate(-22deg); }
  81% { transform: rotate(22deg); }
  86% { transform: rotate(-22deg); }
  91% { transform: rotate(22deg); }
  0%, 4%, 95%, 100% { transform: rotate(-10deg); }
}

@keyframes huh {
  0%, 46% { opacity: 0; transform: translateY(6px); }
  50%, 60% { opacity: 1; transform: translateY(0); }
  64%, 100% { opacity: 0; }
}

@media (prefers-reduced-motion: reduce) {
  .walker, .body, .leg, .huh {
    animation: none;
  }

  .walker {
    transform: translate(196px, 150px);
  }

  .leg-a {
    transform: rotate(10deg);
  }

  .leg-b {
    transform: rotate(-10deg);
  }

  .huh {
    opacity: 1;
  }
}
</style>
