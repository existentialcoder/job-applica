(() => {
  const sendMessage = (msg) => {
    const rt = (typeof chrome !== 'undefined' && chrome.runtime) ? chrome.runtime
             : (typeof browser !== 'undefined' && browser.runtime) ? browser.runtime : null;
    if (rt) rt.sendMessage(msg);
  };

  const first = (selectors) => {
    for (const sel of selectors) {
      const el = document.querySelector(sel);
      if (el) return el;
    }
    return null;
  };

  try {
    // ── Job Title ────────────────────────────────────────────────────────────
    const titleEl = first([
      '[data-testid="jobsearch-JobInfoHeader-title"]',
      'h1.jobsearch-JobInfoHeader-title',
      'h1[class*="JobTitle"]',
      'h1[class*="job-title"]',
      'h1',
    ]);
    const jobTitle = titleEl ? titleEl.textContent.trim().replace(/\s*-\s*job post\s*$/i, '') : null;

    // ── Company ──────────────────────────────────────────────────────────────
    const companyEl = first([
      '[data-testid="inlineHeader-companyName"] a',
      '[data-testid="inlineHeader-companyName"]',
      '[data-testid="companyInfo-name"]',
      '[data-company-name]',
      '.jobsearch-InlineCompanyRating a',
      '[class*="companyName"]',
      '[class*="company-name"]',
    ]);
    const company = companyEl ? companyEl.textContent.trim() : null;

    // ── Location ─────────────────────────────────────────────────────────────
    const locationEl = first([
      '[data-testid="job-location"]',
      '[data-testid="companyInfo-location"]',
      '[class*="jobLocation"]',
      '[class*="job-location"]',
      '.jobsearch-JobInfoHeader-subtitle [class*="location"]',
    ]);
    const location = locationEl ? locationEl.textContent.trim() : null;

    // ── Job Description ──────────────────────────────────────────────────────
    const descEl = first([
      '#jobDescriptionText',
      '[id*="jobDescription"]',
      '[data-testid="jobDescriptionText"]',
      '[class*="jobDescriptionText"]',
      '[class*="job-description"]',
    ]);
    const jobDescription = descEl ? (descEl.innerText || descEl.textContent || '').trim() : null;

    // ── Salary ───────────────────────────────────────────────────────────────
    const salaryEl = first([
      '[data-testid="attribute_snippet_testid"]',
      '[id*="salaryInfoAndJobType"]',
      '[class*="salary"]',
      '[class*="Salary"]',
    ]);
    const salaryRange = salaryEl ? salaryEl.textContent.trim() : null;

    // ── Work Model ───────────────────────────────────────────────────────────
    let workModel = 'On-site';
    const combined = `${location || ''} ${jobDescription || ''}`.toLowerCase();
    if (combined.includes('fully remote') || location?.toLowerCase() === 'remote') workModel = 'Remote';
    else if (combined.includes('remote')) workModel = 'Remote';
    else if (combined.includes('hybrid')) workModel = 'Hybrid';

    sendMessage({ platform: 'Indeed', jobTitle, company, location, jobDescription, salaryRange, workModel });
  } catch (err) {
    console.error('[JobApplica] Indeed script error:', err);
    sendMessage({ platform: 'Indeed', jobTitle: null, company: null });
  }
})();
