<script setup lang="ts">
const t = useT()
const n = t.notFound

useSeoMeta({
  title: 'Page Not Found — JobApplica',
  description: 'This page could not be found.',
  robots: 'noindex',
})
</script>

<template>
  <div class="not-found-page">
    <TheNav />
    <main class="not-found-main">
      <div class="not-found-inner">
        <div class="not-found-code" aria-hidden="true">{{ n.code }}</div>
        <h1 class="not-found-title">{{ n.title }}</h1>
        <p class="not-found-sub">{{ n.body }}</p>
        <div class="not-found-actions">
          <NuxtLink to="/" class="btn btn-primary btn-lg">
            {{ n.backHome }}
          </NuxtLink>
          <a
            href="https://app.jobapplica.io"
            class="btn btn-ghost btn-lg"
            target="_blank"
            rel="noopener"
          >
            {{ n.dashboard }}
          </a>
        </div>
      </div>
    </main>
    <TheFooter />
  </div>
</template>
