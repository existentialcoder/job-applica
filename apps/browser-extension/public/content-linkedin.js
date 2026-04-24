(() => {
  const sendMessage = (msg) => {
    const rt = (typeof chrome !== 'undefined' && chrome.runtime) ? chrome.runtime
             : (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime : null;
    if (rt) rt.sendMessage(msg);
  };

  const first = (selectors, root) => {
    for (const sel of selectors) {
      const el = (root || document).querySelector(sel);
      if (el?.textContent?.trim()) return el;
    }
    return null;
  };

  // On the dedicated job view page the document title reliably contains both
  // title and company in "Job Title - Company | LinkedIn" format.
  function parseDocTitle() {
    const title = document.title;
    if (!title.includes('LinkedIn')) return {};
    const raw = title
      .replace(/\s*\|\s*LinkedIn\s*$/, '')
      .replace(/\s*\(\d+[^)]*\)\s*/g, ' ')
      .trim();
    const dashIdx = raw.lastIndexOf(' - ');
    if (dashIdx > 0) {
      return {
        jobTitle: raw.substring(0, dashIdx).trim() || null,
        company:  raw.substring(dashIdx + 3).trim() || null,
      };
    }
    const dotParts = raw.split(/\s*[·•]\s*/);
    return { jobTitle: dotParts[0]?.trim() || null, company: null };
  }

  // Returns the best container for the job detail panel.
  function findPanel() {
    const candidates = [
      '.job-details-jobs-unified-top-card__content-container',
      '.jobs-unified-top-card',
      // search / collections side-panel
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

  function extract() {
    const panel = findPanel();
    const isDirectView = /\/jobs\/view\/\d+/.test(window.location.pathname);

    // ── Job Title ────────────────────────────────────────────────────────────
    let jobTitle = null;

    // On the direct view page the doc title is the most reliable source
    if (isDirectView) {
      jobTitle = parseDocTitle().jobTitle;
    }

    if (!jobTitle) {
      const titleEl = first([
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
        // broad fallback scoped to the panel so we don't grab page navigation
        'h1',
        'h2',
      ], panel);
      if (titleEl) jobTitle = titleEl.textContent.trim();
    }

    // Last resort for collections page: parse the document title if non-generic
    if (!jobTitle && !document.title.toLowerCase().includes('recommended')
        && !document.title.toLowerCase().includes('collection')
        && !document.title.toLowerCase().includes('jobs | linkedin')) {
      jobTitle = parseDocTitle().jobTitle;
    }

    // ── Company ──────────────────────────────────────────────────────────────
    let company = null;

    if (isDirectView) {
      company = parseDocTitle().company;
    }

    if (!company) {
      const companyEl = first([
        '.job-details-jobs-unified-top-card__company-name a',
        '.job-details-jobs-unified-top-card__company-name',
        '.jobs-unified-top-card__company-name a',
        '.jobs-unified-top-card__company-name',
        '[class*="company-name"] a',
        '[class*="company-name"]',
        '[class*="companyName"] a',
        '[class*="companyName"]',
        // any visible company link inside the panel
        'a[href*="/company/"]',
      ], panel);
      if (companyEl) company = companyEl.textContent.trim();
    }

    if (!company && isDirectView) {
      // Title already came from doc title; company is the part after " - "
      const doc = parseDocTitle();
      company = doc.company;
    }

    // ── Location & Work Model ────────────────────────────────────────────────
    let location = null;
    let workModel = null;

    const metaEl = first([
      '.job-details-jobs-unified-top-card__primary-description-container',
      '.job-details-jobs-unified-top-card__primary-description-without-modal',
      '[class*="primary-description-container"]',
      '[class*="top-card-layout__first-subline"]',
      '.jobs-unified-top-card__subtitle-primary-grouping',
      '.jobs-unified-top-card__metadata-container',
    ], panel);

    if (metaEl) {
      const parts = metaEl.textContent.trim().split(/[·•·]/).map(p => p.trim()).filter(Boolean);
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
        const t = el.textContent.trim().toLowerCase();
        if (t === 'remote') { workModel = 'Remote'; break; }
        if (t === 'hybrid') { workModel = 'Hybrid'; break; }
        if (t === 'on-site' || t === 'onsite') { workModel = 'On-site'; break; }
      }
    }

    // ── Job Description ──────────────────────────────────────────────────────
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
    const jobDescription = descEl ? (descEl.innerText || descEl.textContent || '').trim() : null;

    // ── Salary ───────────────────────────────────────────────────────────────
    const salaryEl = first([
      '.job-details-jobs-unified-top-card__job-insight--highlight',
      '[class*="compensation"]',
      '[class*="salary"]',
      '[aria-label*="alary"]',
    ]);
    const salaryRange = salaryEl ? salaryEl.textContent.trim() : null;

    return { jobTitle, company, location, jobDescription, salaryRange, workModel };
  }

  try {
    const result = extract();
    if (result.jobTitle) {
      sendMessage({ platform: 'LinkedIn', ...result });
      return;
    }

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
  } catch (err) {
    console.error('[JobApplica] LinkedIn script error:', err);
    sendMessage({ platform: 'LinkedIn', jobTitle: null, company: null });
  }
})();
