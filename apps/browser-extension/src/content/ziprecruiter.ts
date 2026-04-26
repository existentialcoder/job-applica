import { sendMessage, first, inferWorkModel } from './common';

try {
  const titleEl = first([
    'h1.job_title',
    'h1[class*="job-title"]',
    'h1[class*="jobTitle"]',
    '[data-testid="job-title"]',
    'h1',
  ]);
  const jobTitle = titleEl ? titleEl.textContent!.trim() : null;

  const companyEl = first([
    'a.hiring_company_text',
    '[class*="hiring_company"]',
    '[data-testid="job-company"]',
    '[class*="company"]',
  ]);
  const company = companyEl ? companyEl.textContent!.trim() : null;

  const locationEl = first([
    'a.location_text',
    '[class*="location_text"]',
    '[data-testid="job-location"]',
    '[class*="location"]',
  ]);
  const location = locationEl ? locationEl.textContent!.trim() : null;

  const descEl = first([
    '.jobDescriptionSection',
    '[class*="job_description"]',
    '[data-testid="job-description"]',
    '[class*="jobDescription"]',
  ]);
  const jobDescription = descEl ? ((descEl as HTMLElement).innerText || descEl.textContent || '').trim() : null;

  const salaryEl = first([
    '[data-testid="job-salary"]',
    '[class*="salary"]',
    '[class*="compensation"]',
  ]);
  const salaryRange = salaryEl ? salaryEl.textContent!.trim() : null;

  const workModel = inferWorkModel(location, jobDescription);

  sendMessage({ platform: 'ZipRecruiter', jobTitle, company, location, jobDescription, salaryRange, workModel });
} catch (err) {
  console.error('[JobApplica] ZipRecruiter script error:', err);
  sendMessage({ platform: 'ZipRecruiter', jobTitle: null, company: null });
}
