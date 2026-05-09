<script setup lang="ts">
const t = useT()
const p = t.terms

useSeoMeta({
  title: p.seoTitle,
  description: p.seoDesc,
  robots: 'index, follow',
})
useHead({
  link: [{ rel: 'canonical', href: 'https://jobapplica.io/terms' }],
})
</script>

<template>
  <div>
    <TheNav />
    <main class="legal-page">
      <div class="container">
        <div class="legal-header">
          <NuxtLink
            to="/"
            style="display:inline-flex;align-items:center;gap:6px;font-size:13px;color:var(--text-3);margin-bottom:24px;transition:color .12s"
          >
            {{ p.backToHome }}
          </NuxtLink>
          <h1>{{ p.title }}</h1>
          <p class="legal-date">{{ p.lastUpdated }}</p>
        </div>

        <div class="legal-body">
          <div class="legal-highlight">{{ p.tldr }}</div>

          <h2>1. Acceptance of Terms</h2>
          <p>
            By accessing or using JobApplica (the "Service"), you agree to be bound by these Terms of Service ("Terms"). If you don't agree with any part of these Terms, do not use the Service.
          </p>
          <p>
            These Terms apply to all users, including visitors, registered users, and anyone who accesses any part of the Service.
          </p>

          <h2>2. Description of the Service</h2>
          <p>JobApplica is a web-based job search management platform that includes:</p>
          <ul>
            <li>A web application at app.jobapplica.io for managing job applications on Kanban boards</li>
            <li>A browser extension for saving job listings from supported job boards</li>
            <li>An analytics dashboard for tracking application activity and pipeline health</li>
          </ul>
          <p>The Service is currently provided free of charge. We reserve the right to introduce paid plans in the future, with adequate notice to existing users.</p>

          <h2>3. Your Account</h2>
          <p>To use the Service, you must create an account. You are responsible for:</p>
          <ul>
            <li>Providing accurate and complete account information</li>
            <li>Maintaining the security of your password</li>
            <li>All activity that occurs under your account</li>
            <li>Notifying us immediately of any unauthorised use of your account</li>
          </ul>
          <p>
            You must be at least 16 years old to use the Service. By creating an account, you confirm you meet this requirement.
          </p>

          <h2>4. Acceptable Use</h2>
          <p>You agree to use the Service only for lawful purposes and in a way that does not infringe the rights of others. You must not:</p>
          <ul>
            <li>Use the Service to collect or store personal data about other people without their consent</li>
            <li>Attempt to gain unauthorised access to any part of the Service or its infrastructure</li>
            <li>Use automated tools or scripts to scrape, crawl, or excessively load the Service</li>
            <li>Upload malicious code, viruses, or any software intended to harm the Service or its users</li>
            <li>Impersonate another person or entity</li>
            <li>Use the Service for any commercial purpose without our prior written consent</li>
          </ul>

          <h2>5. Your Content</h2>
          <p>
            You retain ownership of all content you create and upload to the Service ("Your Content"), including job application data, notes, and board configurations.
          </p>
          <p>
            By using the Service, you grant us a limited, non-exclusive licence to store, process, and display Your Content solely to provide the Service to you. We do not claim any ownership rights over your job search data.
          </p>
          <p>
            You are responsible for ensuring Your Content does not violate any third-party rights or applicable laws.
          </p>

          <h2>6. Browser Extension</h2>
          <p>
            The browser extension is a tool that reads job listing pages at your explicit request. By using the extension, you acknowledge that:
          </p>
          <ul>
            <li>You are using it to capture publicly visible job listing information for your personal job search</li>
            <li>You will not use the extension to scrape job boards in bulk or in a way that violates those platforms' terms of service</li>
            <li>The extension operates under the same terms as the rest of the Service</li>
          </ul>

          <h2>7. Intellectual Property</h2>
          <p>
            The Service, including its design, code, logos, and content created by us, is the intellectual property of JobApplica and is protected by applicable copyright and trademark laws. You may not reproduce, distribute, or create derivative works without our explicit written permission.
          </p>

          <h2>8. Privacy</h2>
          <p>
            Your use of the Service is also governed by our <NuxtLink to="/privacy">Privacy Policy</NuxtLink>, which is incorporated into these Terms by reference.
          </p>

          <h2>9. Disclaimers</h2>
          <p>
            The Service is provided "as is" and "as available" without warranties of any kind, either express or implied. We do not guarantee that:
          </p>
          <ul>
            <li>The Service will be uninterrupted or error-free</li>
            <li>Any data stored will be retained indefinitely</li>
            <li>The Service will meet your specific requirements</li>
          </ul>
          <p>
            We are not responsible for your job search outcomes. JobApplica is a tool. Landing a job depends on many factors beyond any software.
          </p>

          <h2>10. Limitation of Liability</h2>
          <p>
            To the maximum extent permitted by law, JobApplica and its team members shall not be liable for any indirect, incidental, special, consequential, or punitive damages arising from your use of the Service, including loss of data, lost profits, or business interruption.
          </p>
          <p>
            Our total liability for any claim related to the Service shall not exceed $100 USD or the amount you paid us in the past 12 months, whichever is greater.
          </p>

          <h2>11. Termination</h2>
          <p>
            You may stop using the Service and delete your account at any time. We reserve the right to suspend or terminate accounts that violate these Terms, with or without notice, at our sole discretion.
          </p>
          <p>
            Upon termination, your right to use the Service ceases immediately. We will delete your data in accordance with our Privacy Policy.
          </p>

          <h2>12. Changes to Terms</h2>
          <p>
            We may update these Terms from time to time. When we make material changes, we'll notify you via email or a prominent in-app notice at least 14 days before the changes take effect. Continued use of the Service after that date constitutes acceptance of the updated Terms.
          </p>

          <h2>13. Governing Law</h2>
          <p>
            These Terms are governed by and construed in accordance with the laws of the jurisdiction where JobApplica operates, without regard to conflict of law principles. Any disputes shall be resolved in the courts of that jurisdiction.
          </p>

          <div class="legal-contact">
            <h3>Questions about these Terms?</h3>
            <p>
              Reach us at <a :href="`mailto:${p.contactEmail}`">{{ p.contactEmail }}</a>.
              We're a small team and we'll get back to you within a few business days.
            </p>
          </div>
        </div>
      </div>
    </main>
    <TheFooter />
  </div>
</template>
