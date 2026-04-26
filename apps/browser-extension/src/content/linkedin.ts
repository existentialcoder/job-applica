import { sendMessage, first, inferWorkModel } from './common';

// ── Helpers ───────────────────────────────────────────────────────────────────

/** Parses "Job Title - Company | LinkedIn" from document.title. */
function parseDocTitle(): { jobTitle: string | null; company: string | null } {
  const title = document.title;
  if (!title.includes('LinkedIn')) return { jobTitle: null, company: null };
  const raw = title
    .replace(/\s*\|\s*LinkedIn\s*$/, '')
    .replace(/\s*\(\d+[^)]*\)\s*/g, ' ')
    .trim();
  const dashIdx = raw.lastIndexOf(' - ');
  if (dashIdx > 0) {
    return {
      jobTitle: raw.substring(0, dashIdx).trim() || null,
      company: raw.substring(dashIdx + 3).trim() || null,
    };
  }
  const dotParts = raw.split(/\s*[·•]\s*/);
  return { jobTitle: dotParts[0]?.trim() || null, company: null };
}

/** Returns the best container for the job detail panel. */
function findPanel(): Element | Document {
  const candidates = [
    '.job-details-jobs-unified-top-card__content-container',
    '.jobs-unified-top-card',
    '.scaffold-layout__detail',
    '.jobs-search__job-details',
    '.jobs-details',
    '[class*="job-details"][class*="container"]',
    '[class*="job-details"]',
  ];
  for (const sel of candidates) {
    const el = document.querySelector(sel);
    if (el) return el;
  }
  return document;
}

// ── Extraction ────────────────────────────────────────────────────────────────

function extract() {
  const panel = findPanel();
  const isDirectView = /\/jobs\/view\/\d+/.test(window.location.pathname);

  // Job Title
  let jobTitle: string | null = null;
  if (isDirectView) jobTitle = parseDocTitle().jobTitle;
  if (!jobTitle) {
    const el = first([
      'h1.job-details-jobs-unified-top-card__job-title',
      'h1.job-details-jobs-unified-top-card__job-title-link',
      'h1[class*="job-title"]',
      'h2[class*="job-title"]',
      'h1[class*="jobTitle"]',
      'h2[class*="jobTitle"]',
      '.jobs-unified-top-card__job-title h1',
      '.jobs-unified-top-card__job-title h2',
      '.jobs-unified-top-card__job-title a',
      '.jobs-unified-top-card__job-title',
      'h1',
      'h2',
    ], panel);
    if (el) jobTitle = el.textContent!.trim();
  }
  if (
    !jobTitle &&
    !document.title.toLowerCase().includes('recommended') &&
    !document.title.toLowerCase().includes('collection') &&
    !document.title.toLowerCase().includes('jobs | linkedin')
  ) {
    jobTitle = parseDocTitle().jobTitle;
  }

  // Company
  let company: string | null = null;
  if (isDirectView) company = parseDocTitle().company;
  if (!company) {
    const el = first([
      '.job-details-jobs-unified-top-card__company-name a',
      '.job-details-jobs-unified-top-card__company-name',
      '.jobs-unified-top-card__company-name a',
      '.jobs-unified-top-card__company-name',
      '[class*="company-name"] a',
      '[class*="company-name"]',
      '[class*="companyName"] a',
      '[class*="companyName"]',
      'a[href*="/company/"]',
    ], panel);
    if (el) company = el.textContent!.trim();
  }
  if (!company && isDirectView) company = parseDocTitle().company;

  // Location + Work Model
  let location: string | null = null;
  let workModel: string | null = null;

  const metaEl = first([
    '.job-details-jobs-unified-top-card__primary-description-container',
    '.job-details-jobs-unified-top-card__primary-description-without-modal',
    '[class*="primary-description-container"]',
    '[class*="top-card-layout__first-subline"]',
    '.jobs-unified-top-card__subtitle-primary-grouping',
    '.jobs-unified-top-card__metadata-container',
  ], panel);

  if (metaEl) {
    const parts = metaEl.textContent!.trim().split(/[·•·]/).map(p => p.trim()).filter(Boolean);
    const workTerms = ['remote', 'hybrid', 'on-site', 'onsite', 'in-person'];
    for (const part of parts) {
      const lower = part.toLowerCase();
      if (!workTerms.some(t => lower === t || lower.startsWith(t))) {
        if (!location) location = part;
      }
      if (lower === 'remote' || lower.startsWith('remote')) workModel = 'Remote';
      else if (lower === 'hybrid' || lower.startsWith('hybrid')) workModel = 'Hybrid';
      else if (lower.includes('on-site') || lower.includes('onsite') || lower.includes('in-person')) workModel = 'On-site';
    }
  }

  if (!workModel) {
    const badges = document.querySelectorAll('[class*="workplace"], [class*="workplaceType"], [class*="work-type"]');
    for (const el of badges) {
      const t = el.textContent!.trim().toLowerCase();
      if (t === 'remote') { workModel = 'Remote'; break; }
      if (t === 'hybrid') { workModel = 'Hybrid'; break; }
      if (t === 'on-site' || t === 'onsite') { workModel = 'On-site'; break; }
    }
  }

  // Job Description
  const descEl = first([
    '#job-details',
    '[id*="job-details"]',
    '.jobs-description__content',
    '.jobs-description-content__text',
    'article.jobs-description__container',
    '[class*="description__text"]',
    '[class*="jobDescription"]',
    '[class*="job-description"]',
  ]);
  const jobDescription = descEl ? ((descEl as HTMLElement).innerText || descEl.textContent || '').trim() : null;

  // Salary
  const salaryEl = first([
    '.job-details-jobs-unified-top-card__job-insight--highlight',
    '[class*="compensation"]',
    '[class*="salary"]',
    '[aria-label*="alary"]',
  ]);
  const salaryRange = salaryEl ? salaryEl.textContent!.trim() : null;

  return { jobTitle, company, location, jobDescription, salaryRange, workModel: workModel ?? inferWorkModel(location, jobDescription) };
}

// ── Run ───────────────────────────────────────────────────────────────────────

try {
  const result = extract();
  if (result.jobTitle) {
    sendMessage({ platform: 'LinkedIn', ...result });
  } else {
    // Side-panel may still be rendering — poll for up to 2 s
    let attempts = 0;
    const interval = setInterval(() => {
      attempts++;
      const r = extract();
      if (r.jobTitle || attempts >= 8) {
        clearInterval(interval);
        sendMessage({ platform: 'LinkedIn', ...r });
      }
    }, 250);
  }
} catch (err) {
  console.error('[JobApplica] LinkedIn script error:', err);
  sendMessage({ platform: 'LinkedIn', jobTitle: null, company: null });
}
