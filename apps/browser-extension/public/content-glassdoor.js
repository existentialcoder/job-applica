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
      '[data-test="job-title"]',
      'h1[class*="JobDetails_jobTitle"]',
      'h1[class*="jobTitle"]',
      '.JobDetails_jobTitle__Rw_gn',
      'h1',
    ]);
    const jobTitle = titleEl ? titleEl.textContent.trim() : null;

    // ── Company ──────────────────────────────────────────────────────────────
    const companyEl = first([
      '[data-test="employer-name"]',
      '.EmployerProfile_employerName__Xemli',
      '[class*="employerName"]',
      '[class*="EmployerProfile_name"]',
      '[class*="employer-name"]',
      'a[href*="/Overview/"]',
    ]);
    const company = companyEl ? companyEl.textContent.trim() : null;

    // ── Location ─────────────────────────────────────────────────────────────
    const locationEl = first([
      '[data-test="location"]',
      '.JobDetails_location__HrGEz',
      '[class*="JobDetails_location"]',
      '[class*="location"]',
    ]);
    const location = locationEl ? locationEl.textContent.trim() : null;

    // ── Job Description ──────────────────────────────────────────────────────
    const descEl = first([
      '[class*="JobDetails_jobDescription"]',
      '[data-test="jobDescriptionContent"]',
      '#JobDescriptionContainer',
      '[class*="jobDescription"]',
      '[class*="desc__text"]',
    ]);
    const jobDescription = descEl ? (descEl.innerText || descEl.textContent || '').trim() : null;

    // ── Salary ───────────────────────────────────────────────────────────────
    const salaryEl = first([
      '[data-test="detailSalary"]',
      '[class*="SalaryEstimate"]',
      '[class*="salary"]',
    ]);
    const salaryRange = salaryEl ? salaryEl.textContent.trim() : null;

    // ── Work Model ───────────────────────────────────────────────────────────
    let workModel = 'On-site';
    const locationLower = (location || '').toLowerCase();
    const descLower = (jobDescription || '').toLowerCase();
    if (locationLower.includes('remote') || descLower.includes('fully remote')) workModel = 'Remote';
    else if (locationLower.includes('hybrid') || descLower.includes('hybrid')) workModel = 'Hybrid';

    sendMessage({ platform: 'Glassdoor', jobTitle, company, location, jobDescription, salaryRange, workModel });
  } catch (err) {
    console.error('[JobApplica] Glassdoor script error:', err);
    sendMessage({ platform: 'Glassdoor', jobTitle: null, company: null });
  }
})();
