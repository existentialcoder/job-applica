<script setup lang="ts">
import { sections } from '~/config/sections'

const t = useT()
const f = t.footer

const footerNavLinks = computed(() =>
  [
    { key: 'features'   as const, href: '#features',     label: f.links.features },
    { key: 'howItWorks' as const, href: '#how-it-works', label: f.links.howItWorks },
    { key: 'pricing'    as const, href: '#pricing',      label: f.links.pricing },
    { key: 'extension'  as const, href: '#extension',    label: f.links.extension },
  ].filter(link => sections[link.key])
)
</script>

<template>
  <footer class="site-footer" role="contentinfo">
    <div class="container footer-inner">
      <NuxtLink to="/" class="footer-logo" aria-label="JobApplica home">
        <DewLogo :size="22" uid="ft-dew" />
        <span class="footer-logo-text">Job<span>Applica</span></span>
      </NuxtLink>

      <nav class="footer-links" aria-label="Footer navigation">
        <a
          v-for="link in footerNavLinks"
          :key="link.key"
          :href="link.href"
        >
          {{ link.label }}
        </a>

        <span v-if="footerNavLinks.length" class="footer-sep" aria-hidden="true">·</span>

        <NuxtLink to="/privacy">{{ f.links.privacy }}</NuxtLink>
        <NuxtLink to="/terms">{{ f.links.terms }}</NuxtLink>

        <span class="footer-sep" aria-hidden="true">·</span>

        <a href="https://app.jobapplica.io" target="_blank" rel="noopener">
          {{ f.links.dashboard }}
        </a>
      </nav>

      <p class="footer-copy">{{ f.copyright }}</p>
    </div>
  </footer>
</template>
