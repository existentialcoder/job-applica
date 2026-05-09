<script setup lang="ts">
import { sections } from '~/config/sections'

const t = useT()
const isLoggedIn = ref(false)

const navLinks = computed(() =>
  [
    { key: 'features'   as const, href: '#features',     label: t.nav.links.features },
    { key: 'howItWorks' as const, href: '#how-it-works', label: t.nav.links.howItWorks },
    { key: 'pricing'    as const, href: '#pricing',      label: t.nav.links.pricing },
    { key: 'extension'  as const, href: '#extension',    label: t.nav.links.extension },
  ].filter(link => sections[link.key])
)

onMounted(async () => {
  try {
    const res = await fetch('https://app.jobapplica.io/api/v1/auth/me', {
      credentials: 'include',
      signal: AbortSignal.timeout(3000),
    })
    isLoggedIn.value = res.ok
  } catch {
    // silently fail — show login/signup buttons
  }
})
</script>

<template>
  <nav class="site-nav" role="navigation" aria-label="Main navigation">
    <div class="container nav-inner">
      <NuxtLink to="/" class="nav-logo" aria-label="JobApplica home">
        <DewLogo :size="28" uid="nav-dew" />
        <span class="nav-logo-text">Job<span>Applica</span></span>
      </NuxtLink>

      <nav v-if="navLinks.length" class="nav-links" aria-label="Page sections">
        <a v-for="link in navLinks" :key="link.key" :href="link.href">
          {{ link.label }}
        </a>
      </nav>

      <div class="nav-actions">
        <template v-if="isLoggedIn">
          <a
            href="https://app.jobapplica.io"
            class="btn btn-primary btn-sm"
            aria-label="Go to your dashboard"
          >
            {{ t.nav.dashboard }}
          </a>
        </template>
        <template v-else>
          <a
            href="https://app.jobapplica.io/login"
            class="nav-link-login"
            aria-label="Log in to your account"
          >
            {{ t.nav.login }}
          </a>
          <a
            href="https://app.jobapplica.io/signup"
            class="btn btn-primary btn-sm"
            aria-label="Create a free account"
          >
            {{ t.nav.signupFree }}
          </a>
        </template>
      </div>
    </div>
  </nav>
</template>
