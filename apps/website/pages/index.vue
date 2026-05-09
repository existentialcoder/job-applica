<script setup lang="ts">
import { sections } from '~/config/sections'

const t = useT()

useSeoMeta({
  title: 'JobApplica — AI-Powered Job Search Platform | Discover, Apply & Track',
  description: 'JobApplica is a complete AI-powered job search platform. Discover relevant jobs automatically, generate tailored CVs and cover letters, track your pipeline on visual Kanban boards, and let email intelligence handle follow-ups.',
  keywords: 'ai job search platform, job application tracker, job discovery ai, ats score match, cv generator, cover letter generator, kanban job tracker, job search automation, interview tracker, follow-up automation',
  robots: 'index, follow',
  author: 'JobApplica',
  ogType: 'website',
  ogUrl: 'https://jobapplica.io/',
  ogTitle: 'JobApplica — AI-Powered Job Search Platform',
  ogDescription: 'Not just a tracker. JobApplica discovers jobs for you, generates tailored CVs, matches ATS scores, and follows up automatically. Free to start.',
  ogImage: 'https://jobapplica.io/og-image.png',
  ogSiteName: 'JobApplica',
  ogLocale: 'en_US',
  twitterCard: 'summary_large_image',
  twitterSite: '@jobapplica',
  twitterTitle: 'JobApplica — AI-Powered Job Search Platform',
  twitterDescription: 'Discover jobs, generate CVs, track applications, automate follow-ups. Your complete AI job search system — free to start.',
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
        description: 'AI-powered complete job search platform — discover jobs, generate tailored CVs, track applications on Kanban boards, and automate follow-ups.',
        applicationCategory: 'BusinessApplication',
        applicationSubCategory: 'Productivity',
        operatingSystem: 'Web, Chrome',
        offers: { '@type': 'Offer', price: '0', priceCurrency: 'USD' },
        featureList: [
          'AI-powered job discovery based on your profile',
          'Smart import from LinkedIn and Gmail',
          'AI CV and cover letter generator',
          'ATS score match and gap analysis',
          'Visual Kanban job application boards',
          'Browser extension for one-click job saving',
          'Email intelligence — auto-detect replies and rejections',
          'Automated follow-up suggestions',
          'Analytics dashboard with interview rate and ghosting detection',
        ],
        screenshot: 'https://jobapplica.io/screenshot.png',
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
      <PlatformsStrip    v-if="sections.platformsStrip" />
      <ProblemSection    v-if="sections.problem" />
      <HowItWorksSection v-if="sections.howItWorks" />
      <FeaturesSection   v-if="sections.features" />
      <AnalyticsSection  v-if="sections.analytics" />
      <ExtensionSection  v-if="sections.extension" />
      <PricingSection    v-if="sections.pricing" />
      <FinalCtaSection   v-if="sections.finalCta" />
    </main>
    <TheFooter />
  </div>
</template>
