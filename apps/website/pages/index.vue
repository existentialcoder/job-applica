<script setup lang="ts">
useSeoMeta({
  title: 'JobApplica — Job Application Tracker with Kanban Boards & Analytics',
  description: 'Track every job application with visual Kanban boards, a browser extension that auto-saves jobs from LinkedIn & Indeed, and an analytics dashboard showing your interview rate, ghosted applications, and offer pipeline.',
  keywords: 'job application tracker, job search organizer, kanban job tracker, job hunt spreadsheet alternative, job application dashboard, browser extension job saver, interview tracker, job search analytics',
  robots: 'index, follow',
  author: 'JobApplica',
  ogType: 'website',
  ogUrl: 'https://jobapplica.io/',
  ogTitle: 'JobApplica — Job Application Tracker',
  ogDescription: 'Stop losing track of jobs. Visual boards, browser extension auto-save, and analytics that answer: how many applied, how many ghosted, and where your pipeline stands.',
  ogImage: 'https://jobapplica.io/og-image.png',
  ogSiteName: 'JobApplica',
  ogLocale: 'en_US',
  twitterCard: 'summary_large_image',
  twitterSite: '@jobapplica',
  twitterTitle: 'JobApplica — Job Application Tracker',
  twitterDescription: 'Visual Kanban boards + browser extension + analytics dashboard. Never lose track of a job application again.',
  twitterImage: 'https://jobapplica.io/og-image.png',
})

useHead({
  link: [
    { rel: 'canonical', href: 'https://jobapplica.io/' },
  ],
  script: [
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'SoftwareApplication',
        name: 'JobApplica',
        url: 'https://jobapplica.io',
        description: 'Job application tracker with visual Kanban boards, browser extension auto-save, and an analytics dashboard.',
        applicationCategory: 'BusinessApplication',
        applicationSubCategory: 'Productivity',
        operatingSystem: 'Web, Chrome, Firefox',
        offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
        featureList: [
          'Visual Kanban job application boards',
          'Browser extension for LinkedIn, Indeed, Glassdoor, ZipRecruiter',
          'Analytics dashboard with interview rate and ghosting detection',
          'Custom stages and pipeline configuration',
          'Notes, salary range, and job description capture',
          'Application funnel and weekly activity tracking',
        ],
        screenshot: 'https://jobapplica.io/screenshot.png',
      }),
    },
    {
      type: 'application/ld+json',
      innerHTML: JSON.stringify({
        '@context': 'https://schema.org',
        '@type': 'FAQPage',
        mainEntity: [
          {
            '@type': 'Question',
            name: 'Is JobApplica free?',
            acceptedAnswer: { '@type': 'Answer', text: 'Yes. JobApplica is completely free to use, including the browser extension.' },
          },
          {
            '@type': 'Question',
            name: 'Which job sites does the browser extension support?',
            acceptedAnswer: { '@type': 'Answer', text: 'The extension works on LinkedIn, Indeed, Glassdoor, ZipRecruiter, Monster, and Jobscan. Jobs are captured with one click while you browse.' },
          },
          {
            '@type': 'Question',
            name: "What is 'ghosted' in the analytics?",
            acceptedAnswer: { '@type': 'Answer', text: 'A job is marked ghosted when it has been in the Applied stage for 14 or more days with no status update — a strong signal the employer has moved on without a response.' },
          },
          {
            '@type': 'Question',
            name: 'Can I customise the pipeline stages?',
            acceptedAnswer: { '@type': 'Answer', text: 'Yes. Every board lets you create, rename, and reorder stages to match your personal process.' },
          },
        ],
      }),
    },
  ],
})
</script>

<template>
  <div>
    <TheNav />
    <main>
      <HeroSection />
      <PlatformsStrip />
      <ProblemSection />
      <HowItWorksSection />
      <FeaturesSection />
      <AnalyticsSection />
      <ExtensionSection />
      <FaqSection />
      <FinalCtaSection />
    </main>
    <TheFooter />
  </div>
</template>
