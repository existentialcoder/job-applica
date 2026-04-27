<script setup lang="ts">
const faqs = [
  {
    q: 'Is JobApplica free?',
    a: 'Yes. JobApplica is completely free — the web app and the browser extension. No credit card, no trial period, no hidden limits.',
  },
  {
    q: 'Which job boards does the browser extension support?',
    a: 'The extension works on LinkedIn, Indeed, Glassdoor, ZipRecruiter, Monster, and Jobscan. New platforms are added regularly. If a site you use isn\'t supported, you can still manually add jobs directly from the dashboard.',
  },
  {
    q: 'What does "ghosted" mean in the analytics?',
    a: 'A job is flagged as ghosted when it has been sitting in the "Applied" stage for 14 or more days with no status update. This is a strong signal that the employer has moved on without communicating. You can still update the status at any time.',
  },
  {
    q: 'Can I create multiple boards?',
    a: 'Yes. You can create as many boards as you like — for example, one for full-time roles, one for contract work, and one for internships. Each board has its own stages, cards, and settings.',
  },
  {
    q: 'Can I customise the pipeline stages?',
    a: 'Absolutely. You can rename any stage, add new custom stages like "Awaiting Referral" or "Take-home Test", and remove stages you don\'t use. When you rename a stage, all existing jobs are automatically migrated to the new name.',
  },
  {
    q: 'Is my data private?',
    a: 'Your application data is private to your account. We do not sell or share your personal job search data with third parties, recruiters, or employers.',
  },
  {
    q: 'Does it work on Firefox?',
    a: 'Chrome and Chromium-based browsers (Edge, Brave, Arc) are fully supported. Firefox support is planned for an upcoming release.',
  },
]
</script>

<template>
  <section id="faq" aria-labelledby="faq-heading">
    <div class="container">
      <div class="section-label"><span class="badge">FAQ</span></div>
      <h2 class="section-heading" id="faq-heading">
        Common <span class="gradient-text">questions</span>
      </h2>
      <p class="section-sub">Everything you need to know before you start.</p>

      <div class="faq-list">
        <details v-for="faq in faqs" :key="faq.q">
          <summary>{{ faq.q }}</summary>
          <div class="faq-answer">{{ faq.a }}</div>
        </details>
      </div>
    </div>
  </section>
</template>
