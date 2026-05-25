<script setup lang="ts">
import { featureCards } from '~/config/sections'

const t = useT()
const f = t.features

const visibleItems = computed(() =>
  f.items.filter(item => featureCards[item.label.toLowerCase() as keyof typeof featureCards] ?? true)
)
</script>

<template>
  <section id="features" class="features-section" aria-labelledby="features-heading">
    <div class="container">
      <div class="features-header">
        <div class="features-header-text">
          <div class="section-eyebrow">{{ f.eyebrow }}</div>
          <h2 id="features-heading">{{ f.headline }}</h2>
        </div>
        <p class="features-header-sub">{{ f.subtext }}</p>
      </div>

      <div class="features-grid" role="list">
        <article
          v-for="(item, i) in visibleItems"
          :key="i"
          class="feature-cell"
          role="listitem"
          :aria-labelledby="`feat-${i}`"
        >
          <div class="feature-cell-tag" aria-hidden="true">{{ item.label }}</div>
          <h3 :id="`feat-${i}`">{{ item.title }}</h3>
          <p>{{ item.desc }}</p>
          <ul :aria-label="`${item.title} features`">
            <li v-for="bullet in item.bullets" :key="bullet">{{ bullet }}</li>
          </ul>
        </article>
      </div>
    </div>
  </section>
</template>
