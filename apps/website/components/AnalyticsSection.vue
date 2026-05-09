<script setup lang="ts">
const t = useT()
const a = t.analytics
</script>

<template>
  <section id="analytics" class="analytics-section" aria-labelledby="analytics-heading">
    <div class="container">
      <div class="analytics-inner">

        <div class="analytics-text">
          <div class="section-eyebrow">{{ a.eyebrow }}</div>
          <h2 id="analytics-heading">{{ a.headline }}</h2>
          <p>{{ a.body }}</p>
          <div class="analytics-bullets" aria-label="Analytics capabilities">
            <div
              v-for="bullet in a.bullets"
              :key="bullet"
              class="analytics-bullet"
            >
              {{ bullet }}
            </div>
          </div>
        </div>

        <div class="analytics-visual" role="img" aria-label="Example analytics preview">
          <div class="stat-row">
            <div
              v-for="stat in a.preview.stats"
              :key="stat.label"
              class="stat-card"
            >
              <div class="stat-num" :style="`color:${stat.color}`">{{ stat.value }}</div>
              <div class="stat-label">{{ stat.label }}</div>
            </div>
          </div>

          <div class="funnel-title">{{ a.preview.funnelTitle }}</div>
          <div
            v-for="stage in a.preview.funnelStages"
            :key="stage.label"
            class="funnel-row"
          >
            <span class="funnel-label">{{ stage.label }}</span>
            <div class="funnel-bar-bg">
              <div class="funnel-bar" :style="`width:${stage.width};background:${stage.color}`" />
            </div>
            <span class="funnel-count">{{ stage.count }}</span>
          </div>

          <p class="analytics-note">{{ a.preview.note }}</p>
        </div>

      </div>
    </div>
  </section>
</template>
