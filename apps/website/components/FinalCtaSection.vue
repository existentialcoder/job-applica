<script setup lang="ts">
const t = useT()
const c = t.finalCta
const { storeUrl, storeName } = useExtensionLink()
</script>

<template>
  <section class="final-cta" aria-labelledby="final-cta-heading">
    <div class="container final-cta-inner">
      <h2 id="final-cta-heading">{{ c.headline }}</h2>
      <p>{{ c.body }}</p>
      <div class="final-cta-actions">
        <a
          href="https://app.jobapplica.io/signup"
          class="btn btn-primary btn-lg"
          aria-label="Create a free JobApplica account"
        >
          {{ c.ctaPrimary }}
        </a>
        <a
          :href="storeUrl"
          class="btn btn-ghost btn-lg"
          target="_blank"
          rel="noopener"
          :aria-label="`Install the browser extension from ${storeName}`"
        >
          {{ c.ctaExtension }}
        </a>
      </div>
    </div>
  </section>
</template>
