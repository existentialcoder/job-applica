<script setup lang="ts">
const t = useT()
const p = t.pricing
</script>

<template>
  <section id="pricing" class="pricing-section" aria-labelledby="pricing-heading">
    <div class="container">
      <div class="pricing-header">
        <div class="section-eyebrow">{{ p.eyebrow }}</div>
        <h2 id="pricing-heading">{{ p.headline }}</h2>
        <p class="pricing-sub">{{ p.subtext }}</p>
      </div>

      <div class="pricing-grid" role="list">
        <article
          v-for="plan in p.plans"
          :key="plan.name"
          class="pricing-card"
          :class="{ 'pricing-card--featured': plan.highlight }"
          role="listitem"
          :aria-labelledby="`plan-${plan.name}`"
        >
          <div v-if="plan.highlight" class="pricing-badge" aria-label="Recommended plan">
            Most popular
          </div>

          <div class="pricing-card-header">
            <h3 :id="`plan-${plan.name}`" class="plan-name">{{ plan.name }}</h3>
            <div class="plan-price">
              <span class="plan-price-num">{{ plan.price }}</span>
              <span class="plan-price-period">{{ plan.period }}</span>
            </div>
            <p class="plan-desc">{{ plan.desc }}</p>
          </div>

          <a
            :href="plan.ctaHref"
            class="btn btn-lg plan-cta"
            :class="plan.highlight ? 'btn-primary' : 'btn-ghost'"
            target="_blank"
            rel="noopener"
            :aria-label="plan.cta"
          >
            {{ plan.cta }}
          </a>

          <ul class="plan-features" aria-label="Included features">
            <li v-for="feature in plan.features" :key="feature" class="plan-feature plan-feature--yes">
              <span class="plan-feature-icon" aria-hidden="true">✓</span>
              {{ feature }}
            </li>
            <li v-for="feature in plan.notIncluded" :key="feature" class="plan-feature plan-feature--no">
              <span class="plan-feature-icon" aria-hidden="true">–</span>
              {{ feature }}
            </li>
          </ul>
        </article>
      </div>

      <p class="pricing-note">{{ p.note }}</p>
    </div>
  </section>
</template>
