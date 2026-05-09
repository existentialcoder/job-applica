<script setup lang="ts">
const t = useT()
const h = t.howItWorks
</script>

<template>
  <section id="how-it-works" class="how-section" aria-labelledby="how-heading">
    <div class="container">
      <div class="steps-header">
        <div class="section-eyebrow">{{ h.eyebrow }}</div>
        <h2 id="how-heading">{{ h.headline }}</h2>
        <p>{{ h.subtext }}</p>
      </div>

      <div class="steps-list" role="list">
        <article
          v-for="(step, i) in h.steps"
          :key="i"
          class="step-row"
          role="listitem"
          :aria-labelledby="`step${i + 1}-h`"
        >
          <div class="step-num-wrap">
            <div class="step-num" :aria-label="`Step ${i + 1}`">{{ i + 1 }}</div>
          </div>
          <div class="step-body">
            <span class="step-tag">{{ step.tag }}</span>
            <h3 :id="`step${i + 1}-h`">{{ step.heading }}</h3>
            <p>{{ step.body }}</p>
            <div v-if="step.action" class="step-action">
              <a
                v-if="i === 0"
                href="https://chrome.google.com/webstore"
                class="btn btn-ghost btn-sm"
                target="_blank"
                rel="noopener"
                :aria-label="step.action"
              >
                {{ step.action }}
              </a>
              <a
                v-else-if="i === 2"
                href="https://app.jobapplica.io"
                class="btn btn-ghost btn-sm"
                target="_blank"
                rel="noopener"
                :aria-label="step.action"
              >
                {{ step.action }}
              </a>
            </div>
          </div>
        </article>
      </div>
    </div>
  </section>
</template>
