<template>
  <footer class="site-footer" role="contentinfo">
    <div class="container footer-inner">
      <NuxtLink to="/" class="nav-logo" aria-label="JobApplica">
        <DewLogo :size="24" uid="ft-dew" />
        <span style="font-size:15px;font-weight:700">Job<span style="color:#818cf8">Applica</span></span>
      </NuxtLink>

      <nav class="footer-links" aria-label="Footer navigation">
        <a href="#how-it-works">How it works</a>
        <a href="#features">Features</a>
        <a href="#analytics">Analytics</a>
        <a href="#extension">Extension</a>
        <a href="#faq">FAQ</a>
        <NuxtLink to="/privacy">Privacy</NuxtLink>
        <NuxtLink to="/terms">Terms</NuxtLink>
      </nav>

      <p class="footer-copy">© 2025 JobApplica. All rights reserved.</p>
    </div>
  </footer>
</template>
