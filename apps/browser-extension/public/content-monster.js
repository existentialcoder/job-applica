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
      'h1[class*="job-title"]',
      'h1.title',
      '[class*="JobViewTitle"]',
      'h1',
    ]);
    const jobTitle = titleEl ? titleEl.textContent.trim() : null;

    // ── Company ──────────────────────────────────────────────────────────────
    const companyEl = first([
      '[class*="company-name"] a',
      '[class*="company-name"]',
      '[itemprop="hiringOrganization"] [itemprop="name"]',
      '[itemprop="hiringOrganization"]',
      '.company',
    ]);
    const company = companyEl ? companyEl.textContent.trim() : null;

    // ── Location ─────────────────────────────────────────────────────────────
    const locationEl = first([
      '[class*="job-location"]',
      '[itemprop="jobLocation"] [itemprop="name"]',
      '[itemprop="jobLocation"]',
      '.location',
    ]);
    const location = locationEl ? locationEl.textContent.trim() : null;

    // ── Job Description ──────────────────────────────────────────────────────
    const descEl = first([
      '#JobDescription',
      '[id*="job-description"]',
      '[class*="job-description"]',
      '[itemprop="description"]',
    ]);
    const jobDescription = descEl ? (descEl.innerText || descEl.textContent || '').trim() : null;

    // ── Work Model ───────────────────────────────────────────────────────────
    let workModel = 'On-site';
    const combined = `${location || ''} ${jobDescription || ''}`.toLowerCase();
    if (combined.includes('remote')) workModel = 'Remote';
    else if (combined.includes('hybrid')) workModel = 'Hybrid';

    sendMessage({ platform: 'Monster', jobTitle, company, location, jobDescription, workModel });
  } catch (err) {
    console.error('[JobApplica] Monster script error:', err);
    sendMessage({ platform: 'Monster', jobTitle: null, company: null });
  }
})();
