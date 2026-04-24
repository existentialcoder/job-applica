(() => {
  const sendMessage = (msg) => {
    if (typeof chrome !== 'undefined' && chrome.runtime?.sendMessage) {
      chrome.runtime.sendMessage(msg);
    } else if (typeof browser !== 'undefined' && browser.runtime?.sendMessage) {
      browser.runtime.sendMessage(msg);
    }
  };

  try {
    // Jobscan job scan results page
    const titleEl = document.querySelector('[class*="job-title"]') ||
      document.querySelector('h1') ||
      document.querySelector('[class*="position"]');
    const jobTitle = titleEl ? titleEl.textContent.trim() : null;

    const companyEl = document.querySelector('[class*="company"]') ||
      document.querySelector('[class*="employer"]');
    const company = companyEl ? companyEl.textContent.trim() : null;

    const descEl = document.querySelector('[class*="job-description"]') ||
      document.querySelector('textarea[name*="job"]');
    const jobDescription = descEl ? (descEl.value || descEl.textContent || '').trim() : null;

    sendMessage({ platform: 'Jobscan', jobTitle, company, jobDescription, location: null });
  } catch (error) {
    console.error('JobApplica Jobscan content script error:', error);
    sendMessage({ platform: 'Jobscan', jobTitle: null, company: null });
  }
})();
