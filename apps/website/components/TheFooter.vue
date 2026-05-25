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

        <span class="footer-sep" aria-hidden="true">·</span>

        <a
          href="https://github.com/existentialcoder/job-applica"
          target="_blank"
          rel="noopener noreferrer"
          class="footer-github"
          aria-label="JobApplica on GitHub"
        >
          <svg width="14" height="14" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
            <path d="M12 0C5.374 0 0 5.373 0 12c0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23A11.509 11.509 0 0 1 12 5.803c1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576C20.566 21.797 24 17.3 24 12c0-6.627-5.373-12-12-12z"/>
          </svg>
          GitHub
        </a>
      </nav>

      <p class="footer-copy">{{ f.copyright }}</p>
    </div>
  </footer>
</template>
