import { sendMessage, first, inferWorkModel } from './common';

try {
  const titleEl = first([
    '[data-testid="jobsearch-JobInfoHeader-title"]',
    'h1.jobsearch-JobInfoHeader-title',
    'h1[class*="JobTitle"]',
    'h1[class*="job-title"]',
    'h1',
  ]);
  const jobTitle = titleEl
    ? titleEl.textContent!.trim().replace(/\s*-\s*job post\s*$/i, '')
    : null;

  const companyEl = first([
    '[data-testid="inlineHeader-companyName"] a',
    '[data-testid="inlineHeader-companyName"]',
    '[data-testid="companyInfo-name"]',
    '[data-company-name]',
    '.jobsearch-InlineCompanyRating a',
    '[class*="companyName"]',
    '[class*="company-name"]',
  ]);
  const company = companyEl ? companyEl.textContent!.trim() : null;

  const locationEl = first([
    '[data-testid="job-location"]',
    '[data-testid="companyInfo-location"]',
    '[class*="jobLocation"]',
    '[class*="job-location"]',
    '.jobsearch-JobInfoHeader-subtitle [class*="location"]',
  ]);
  const location = locationEl ? locationEl.textContent!.trim() : null;

  const descEl = first([
    '#jobDescriptionText',
    '[id*="jobDescription"]',
    '[data-testid="jobDescriptionText"]',
    '[class*="jobDescriptionText"]',
    '[class*="job-description"]',
  ]);
  const jobDescription = descEl ? ((descEl as HTMLElement).innerText || descEl.textContent || '').trim() : null;

  const salaryEl = first([
    '[data-testid="attribute_snippet_testid"]',
    '[id*="salaryInfoAndJobType"]',
    '[class*="salary"]',
    '[class*="Salary"]',
  ]);
  const salaryRange = salaryEl ? salaryEl.textContent!.trim() : null;

  const workModel = inferWorkModel(location, jobDescription);

  sendMessage({ platform: 'Indeed', jobTitle, company, location, jobDescription, salaryRange, workModel });
} catch (err) {
  console.error('[JobApplica] Indeed script error:', err);
  sendMessage({ platform: 'Indeed', jobTitle: null, company: null });
}
