<script setup lang="ts">
const t = useT()
const p = t.problem
</script>

<template>
  <section class="problem-section" aria-labelledby="problem-heading">
    <div class="container">
      <div class="problem-text-block">
        <div class="section-eyebrow">{{ p.eyebrow }}</div>
        <h2
          id="problem-heading"
          style="font-family:var(--font-display);font-size:clamp(28px,3.5vw,42px);font-weight:800;letter-spacing:-.03em;line-height:1.1;margin-bottom:0"
        >
          {{ p.headline }}
        </h2>
        <p>{{ p.body }}</p>
      </div>

      <div class="problem-grid" role="list">
        <div
          v-for="card in p.cards"
          :key="card.label"
          class="problem-cell"
          role="listitem"
        >
          <div class="problem-label" aria-hidden="true">{{ card.label }}</div>
          <div class="problem-title">{{ card.title }}</div>
          <p class="problem-desc">{{ card.desc }}</p>
        </div>
      </div>
    </div>
  </section>
</template>
