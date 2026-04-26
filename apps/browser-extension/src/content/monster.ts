import { sendMessage, first, inferWorkModel } from './common';

try {
  const titleEl = first([
    'h1[class*="job-title"]',
    'h1.title',
    '[class*="JobViewTitle"]',
    'h1',
  ]);
  const jobTitle = titleEl ? titleEl.textContent!.trim() : null;

  const companyEl = first([
    '[class*="company-name"] a',
    '[class*="company-name"]',
    '[itemprop="hiringOrganization"] [itemprop="name"]',
    '[itemprop="hiringOrganization"]',
    '.company',
  ]);
  const company = companyEl ? companyEl.textContent!.trim() : null;

  const locationEl = first([
    '[class*="job-location"]',
    '[itemprop="jobLocation"] [itemprop="name"]',
    '[itemprop="jobLocation"]',
    '.location',
  ]);
  const location = locationEl ? locationEl.textContent!.trim() : null;

  const descEl = first([
    '#JobDescription',
    '[id*="job-description"]',
    '[class*="job-description"]',
    '[itemprop="description"]',
  ]);
  const jobDescription = descEl ? ((descEl as HTMLElement).innerText || descEl.textContent || '').trim() : null;

  const workModel = inferWorkModel(location, jobDescription);

  sendMessage({ platform: 'Monster', jobTitle, company, location, jobDescription, workModel });
} catch (err) {
  console.error('[JobApplica] Monster script error:', err);
  sendMessage({ platform: 'Monster', jobTitle: null, company: null });
}
