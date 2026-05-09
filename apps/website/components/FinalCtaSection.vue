<script setup lang="ts">
const t = useT()
const c = t.finalCta
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
          href="https://chrome.google.com/webstore"
          class="btn btn-ghost btn-lg"
          target="_blank"
          rel="noopener"
          aria-label="Install the browser extension"
        >
          {{ c.ctaExtension }}
        </a>
      </div>
    </div>
  </section>
</template>
