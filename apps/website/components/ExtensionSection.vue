<template>
  <section id="extension" class="extension-section" aria-labelledby="ext-heading">
    <div class="container">
      <div class="extension-inner">

        <div>
          <div class="section-label" style="justify-content:flex-start;margin-bottom:14px">
            <span class="badge">Browser Extension</span>
          </div>
          <h2 id="ext-heading">Start here.<br><span class="gradient-text">Save jobs as you browse.</span></h2>
          <p>Install the extension once. From that moment, every job you find on LinkedIn, Indeed, or Glassdoor can be saved to your board in a single click — title, company, salary, description, and source URL included.</p>

          <div class="extension-steps" aria-label="Extension installation steps">
            <div class="ext-step">
              <div class="ext-step-icon" aria-hidden="true">1</div>
              <div class="ext-step-text">
                <strong>Install from the Chrome Web Store</strong>
                <span>Free. No account required to install.</span>
              </div>
            </div>
            <div class="ext-step">
              <div class="ext-step-icon" aria-hidden="true">2</div>
              <div class="ext-step-text">
                <strong>Sign in to your JobApplica account</strong>
                <span>Takes 30 seconds. Your board is ready immediately.</span>
              </div>
            </div>
            <div class="ext-step">
              <div class="ext-step-icon" aria-hidden="true">3</div>
              <div class="ext-step-text">
                <strong>Browse jobs, click Save — done</strong>
                <span>The extension reads the page so you don't have to type anything.</span>
              </div>
            </div>
          </div>

          <div style="margin-top:28px;display:flex;gap:12px;flex-wrap:wrap">
            <a
              href="https://chrome.google.com/webstore"
              class="btn btn-primary btn-lg"
              target="_blank"
              rel="noopener"
              aria-label="Install JobApplica extension from Chrome Web Store"
            >
              <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor" aria-hidden="true">
                <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 14.5v-9l6 4.5-6 4.5z"/>
              </svg>
              Install for Chrome
            </a>
          </div>
        </div>

        <!-- Extension popup mockup -->
        <div class="ext-visual" aria-label="Extension popup preview" role="img">
          <div style="display:flex;align-items:center;gap:10px;margin-bottom:16px">
            <DewLogo :size="24" uid="ext-dew" />
            <div>
              <div style="font-size:13px;font-weight:700">JobApplica</div>
              <div style="font-size:11px;color:var(--muted)">Job detected on this page</div>
            </div>
          </div>

          <div class="ext-popup-bar">
            <div>
              <div class="ext-popup-title">Senior Frontend Engineer</div>
              <div class="ext-popup-sub">Stripe · Remote · $160k–$200k</div>
            </div>
            <button class="ext-save-btn" aria-label="Save job to JobApplica board">Save Job</button>
          </div>

          <div class="ext-popup-bar">
            <div>
              <div class="ext-popup-title">Product Designer</div>
              <div class="ext-popup-sub">Figma · San Francisco · $140k–$180k</div>
            </div>
            <button class="ext-save-btn" aria-label="Save job to JobApplica board">Save Job</button>
          </div>

          <div style="margin-top:12px;padding:10px 14px;background:rgba(16,185,129,0.08);border:1px solid rgba(16,185,129,0.2);border-radius:8px;font-size:12px;color:#6ee7b7">
            ✓ 2 jobs saved to "Job Search 2025" board
          </div>
        </div>

      </div>
    </div>
  </section>
</template>
