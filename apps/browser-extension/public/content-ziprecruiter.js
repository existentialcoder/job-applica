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
      'h1.job_title',
      'h1[class*="job-title"]',
      'h1[class*="jobTitle"]',
      '[data-testid="job-title"]',
      'h1',
    ]);
    const jobTitle = titleEl ? titleEl.textContent.trim() : null;

    // ── Company ──────────────────────────────────────────────────────────────
    const companyEl = first([
      'a.hiring_company_text',
      '[class*="hiring_company"]',
      '[data-testid="job-company"]',
      '[class*="company"]',
    ]);
    const company = companyEl ? companyEl.textContent.trim() : null;

    // ── Location ─────────────────────────────────────────────────────────────
    const locationEl = first([
      'a.location_text',
      '[class*="location_text"]',
      '[data-testid="job-location"]',
      '[class*="location"]',
    ]);
    const location = locationEl ? locationEl.textContent.trim() : null;

    // ── Job Description ──────────────────────────────────────────────────────
    const descEl = first([
      '.jobDescriptionSection',
      '[class*="job_description"]',
      '[data-testid="job-description"]',
      '[class*="jobDescription"]',
    ]);
    const jobDescription = descEl ? (descEl.innerText || descEl.textContent || '').trim() : null;

    // ── Salary ───────────────────────────────────────────────────────────────
    const salaryEl = first([
      '[data-testid="job-salary"]',
      '[class*="salary"]',
      '[class*="compensation"]',
    ]);
    const salaryRange = salaryEl ? salaryEl.textContent.trim() : null;

    // ── Work Model ───────────────────────────────────────────────────────────
    let workModel = 'On-site';
    const combined = `${location || ''} ${jobDescription || ''}`.toLowerCase();
    if (combined.includes('fully remote') || location?.toLowerCase() === 'remote') workModel = 'Remote';
    else if (combined.includes('remote')) workModel = 'Remote';
    else if (combined.includes('hybrid')) workModel = 'Hybrid';

    sendMessage({ platform: 'ZipRecruiter', jobTitle, company, location, jobDescription, salaryRange, workModel });
  } catch (err) {
    console.error('[JobApplica] ZipRecruiter script error:', err);
    sendMessage({ platform: 'ZipRecruiter', jobTitle: null, company: null });
  }
})();
