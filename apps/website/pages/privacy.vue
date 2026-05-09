<script setup lang="ts">
const t = useT()
const p = t.privacy

useSeoMeta({
  title: p.seoTitle,
  description: p.seoDesc,
  robots: 'index, follow',
})
useHead({
  link: [{ rel: 'canonical', href: 'https://jobapplica.io/privacy' }],
})
</script>

<template>
  <div>
    <TheNav />
    <main class="legal-page">
      <div class="container">
        <div class="legal-header">
          <NuxtLink to="/" class="legal-back">{{ p.backToHome }}</NuxtLink>
          <h1>{{ p.title }}</h1>
          <p class="legal-date">{{ p.lastUpdated }}</p>
        </div>

        <div class="legal-body">

          <div class="legal-highlight">
            We collect only what is needed to run JobApplica. We do not sell your data. We do not share your job search
            information with employers or recruiters. The browser extension only reads a page when you explicitly open
            the popup and click Save.
          </div>

          <!-- ── 1. Who we are ─────────────────────────────── -->
          <h2>1. Who We Are</h2>
          <p>
            JobApplica ("we", "us", "our") operates the job search management platform accessible at
            <a href="https://jobapplica.io">jobapplica.io</a>,
            <a href="https://app.jobapplica.io">app.jobapplica.io</a>, and the
            JobApplica browser extension available on the Chrome Web Store.
          </p>
          <p>
            This Privacy Policy applies to all components of the service. Questions or requests can be sent to
            <a :href="`mailto:${p.contactEmail}`">{{ p.contactEmail }}</a>.
          </p>

          <!-- ── 2. Browser Extension – detailed disclosure ── -->
          <h2>2. Browser Extension — Permissions and Data Use</h2>
          <p>
            This section is specific to the JobApplica Chrome extension and is written to meet the
            <a href="https://developer.chrome.com/docs/webstore/user_data/" target="_blank" rel="noopener">
              Chrome Web Store User Data Policy
            </a>.
          </p>

          <h3>Single Purpose</h3>
          <p>
            The extension has one purpose: to let you save a job listing from a supported job board to your
            JobApplica board in a single click. It reads job data only when you open the extension popup while
            viewing a job listing, and only sends that data to your JobApplica account when you explicitly press
            <strong>Save Job</strong>.
          </p>

          <h3>Permissions Requested and Why</h3>

          <div class="legal-permission-table">
            <div class="legal-permission-row">
              <span class="legal-permission-name">tabs</span>
              <span class="legal-permission-desc">
                Used to read the URL of your currently active tab so the extension can detect whether you are on a
                supported job board (LinkedIn, Indeed, Glassdoor, Monster, ZipRecruiter, Jobscan). The extension
                does not access tab content, history, or any other tab data.
              </span>
            </div>
            <div class="legal-permission-row">
              <span class="legal-permission-name">activeTab</span>
              <span class="legal-permission-desc">
                Grants temporary access to the current tab when you open the extension popup. This is used to
                inject the job-extraction script into the page so it can read the job listing details. Access
                expires as soon as the popup closes.
              </span>
            </div>
            <div class="legal-permission-row">
              <span class="legal-permission-name">scripting</span>
              <span class="legal-permission-desc">
                Used together with <code>activeTab</code> to run a script on the job listing page you have open.
                The script reads the job title, company, location, salary range, and description displayed on
                that page. No script runs in the background or on pages you have not opened the popup on.
              </span>
            </div>
            <div class="legal-permission-row">
              <span class="legal-permission-name">storage</span>
              <span class="legal-permission-desc">
                Used to store the following in your browser locally:
                your authentication token (so you stay signed in),
                your dark/light mode preference,
                and the last board you used (so the extension remembers it next time).
                This data never leaves your device except as described in this policy.
              </span>
            </div>
          </div>

          <h3>Host Permissions and Why</h3>
          <p>
            The extension requests access to specific job board domains so it can read job listing pages when
            you open the popup on them. It does not inject any scripts automatically — scripts only run on
            demand when you open the popup on one of these sites.
          </p>
          <ul>
            <li><strong>linkedin.com, www.linkedin.com</strong> — to read job listings on LinkedIn</li>
            <li><strong>indeed.com, www.indeed.com</strong> — to read job listings on Indeed</li>
            <li><strong>glassdoor.com, www.glassdoor.com</strong> — to read job listings on Glassdoor</li>
            <li><strong>monster.com, www.monster.com</strong> — to read job listings on Monster</li>
            <li><strong>ziprecruiter.com, www.ziprecruiter.com</strong> — to read job listings on ZipRecruiter</li>
            <li><strong>jobscan.co, www.jobscan.co</strong> — to read job listings on Jobscan</li>
            <li><strong>app.jobapplica.io</strong> — to sync your login session between the web app and the extension, so you do not need to sign in twice</li>
            <li><strong>api.jobapplica.io</strong> — to send saved job data to your JobApplica account and to retrieve your boards and settings</li>
          </ul>

          <h3>What Data the Extension Reads from Job Pages</h3>
          <p>
            When you open the popup on a job listing and click Save, the extension reads the following fields
            from the page currently visible in your browser:
          </p>
          <ul>
            <li>Job title</li>
            <li>Company name</li>
            <li>Job location</li>
            <li>Salary range (if shown on the page)</li>
            <li>Job description text</li>
            <li>Work model (remote, hybrid, on-site, if shown)</li>
            <li>The URL of the job listing page</li>
          </ul>
          <p>
            This data is sent to <strong>api.jobapplica.io</strong> and stored in your JobApplica account.
            It is only accessible to you. It is never shared with third parties, employers, or recruiters.
          </p>

          <h3>What the Extension Does Not Do</h3>
          <ul>
            <li>It does not run scripts in the background on job boards without your interaction</li>
            <li>It does not track your browsing history or the pages you visit</li>
            <li>It does not read any page you have not opened the popup on</li>
            <li>It does not collect data from pages outside the listed host permissions</li>
            <li>It does not display ads or transmit data to advertising networks</li>
            <li>It does not use remote code — all extension code is bundled in the package submitted to the Chrome Web Store</li>
          </ul>

          <h3>Local Storage and Uninstallation</h3>
          <p>
            The extension stores your authentication token, dark mode preference, and last-used board ID in
            <code>chrome.storage.local</code>. This data is stored only on your device. When you uninstall the
            extension, Chrome automatically clears this local storage. Your job application data stored in your
            JobApplica account is not affected by uninstalling the extension.
          </p>

          <!-- ── 3. Web app data ──────────────────────────── -->
          <h2>3. Web Application — Information We Collect</h2>

          <h3>Account Information</h3>
          <p>When you create an account, we collect:</p>
          <ul>
            <li>Your name and email address</li>
            <li>A hashed password (plain text passwords are never stored)</li>
            <li>Optional: a profile photo you upload</li>
            <li>If you sign in with Google or LinkedIn OAuth, we receive your name and email from that provider. We do not receive your passwords or private messages from those services.</li>
          </ul>

          <h3>Job Application Data</h3>
          <p>The job and application data you create in JobApplica, including job titles, companies, salaries, notes, pipeline stages, and board configurations, is stored securely and accessible only to you.</p>

          <h3>Usage Information</h3>
          <p>We collect basic usage data to improve the product:</p>
          <ul>
            <li>Browser type and operating system</li>
            <li>Pages visited within the application</li>
            <li>Feature interactions</li>
            <li>Error logs and performance data</li>
          </ul>

          <h3>Cookies</h3>
          <p>
            We use essential cookies to keep you signed in across sessions. We do not use advertising cookies
            or third-party tracking cookies.
          </p>

          <!-- ── 4. How we use data ──────────────────────── -->
          <h2>4. How We Use Your Information</h2>
          <p>We use your information to:</p>
          <ul>
            <li>Provide and operate the JobApplica service</li>
            <li>Authenticate you and secure your account</li>
            <li>Generate the analytics shown in your dashboard</li>
            <li>Send transactional emails (password reset, account notifications)</li>
            <li>Improve the product using aggregate, anonymised usage patterns</li>
            <li>Respond to support requests</li>
          </ul>
          <p>We do <strong>not</strong> use your data to serve ads, build marketing profiles, or share it with employers or recruiters.</p>

          <!-- ── 5. Data sharing ─────────────────────────── -->
          <h2>5. Data Sharing</h2>
          <p>We do not sell or share your personal data. The only circumstances where data may be disclosed:</p>
          <ul>
            <li><strong>Infrastructure providers:</strong> Hosting and database providers process data on our behalf under data processing agreements. They cannot use your data for their own purposes.</li>
            <li><strong>Legal requirements:</strong> If required by law or court order.</li>
            <li><strong>Business transfer:</strong> If JobApplica is acquired, users will be notified before any data transfer occurs.</li>
          </ul>

          <!-- ── 6. Security ────────────────────────────── -->
          <h2>6. Data Security</h2>
          <p>
            Data is encrypted in transit (HTTPS/TLS) and at rest. Passwords are hashed. Production database
            access is restricted. If you find a security issue, please report it to
            <a :href="`mailto:${p.securityEmail}`">{{ p.securityEmail }}</a>.
          </p>

          <!-- ── 7. Retention ──────────────────────────── -->
          <h2>7. Data Retention</h2>
          <p>
            Your account and application data is retained while your account is active. When you delete your
            account, data is deleted within 30 days except where retention is required by law.
            To request deletion, contact <a :href="`mailto:${p.contactEmail}`">{{ p.contactEmail }}</a>.
          </p>

          <!-- ── 8. Your rights ────────────────────────── -->
          <h2>8. Your Rights</h2>
          <p>You have the right to access, correct, export, or delete your personal data at any time. Contact us at <a :href="`mailto:${p.contactEmail}`">{{ p.contactEmail }}</a> to exercise any of these rights.</p>

          <!-- ── 9. Children ───────────────────────────── -->
          <h2>9. Children</h2>
          <p>JobApplica is not directed at anyone under 16. We do not knowingly collect data from minors.</p>

          <!-- ── 10. Changes ──────────────────────────── -->
          <h2>10. Changes to This Policy</h2>
          <p>
            Material changes will be communicated via email or an in-app notice before they take effect.
            The date at the top of this page reflects the latest revision.
          </p>

          <div class="legal-contact">
            <h3>Contact</h3>
            <p>
              Privacy questions: <a :href="`mailto:${p.contactEmail}`">{{ p.contactEmail }}</a><br>
              Security disclosures: <a :href="`mailto:${p.securityEmail}`">{{ p.securityEmail }}</a>
            </p>
          </div>

        </div>
      </div>
    </main>
    <TheFooter />
  </div>
</template>
