<template>
  <nav class="site-nav" role="navigation" aria-label="Main navigation">
    <div class="container nav-inner">
      <NuxtLink to="/" class="nav-logo" aria-label="JobApplica home">
        <DewLogo :size="32" uid="nav-dew" />
        <span class="nav-logo-text">Job<span style="color:#818cf8">Applica</span></span>
      </NuxtLink>

      <nav class="nav-links" aria-label="Page sections">
        <a href="#how-it-works">How it works</a>
        <a href="#features">Features</a>
        <a href="#analytics">Analytics</a>
        <a href="#extension">Extension</a>
        <a href="#faq">FAQ</a>
      </nav>

      <div class="nav-cta">
        <a href="#extension" class="btn btn-primary" style="padding:9px 18px;font-size:14px;">
          Install Extension
        </a>
      </div>
    </div>
  </nav>
</template>
