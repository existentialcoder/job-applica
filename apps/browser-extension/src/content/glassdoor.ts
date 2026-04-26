import { sendMessage, first, inferWorkModel } from './common';

try {
  const titleEl = first([
    '[data-test="job-title"]',
    'h1[class*="JobDetails_jobTitle"]',
    'h1[class*="jobTitle"]',
    '.JobDetails_jobTitle__Rw_gn',
    'h1',
  ]);
  const jobTitle = titleEl ? titleEl.textContent!.trim() : null;

  const companyEl = first([
    '[data-test="employer-name"]',
    '.EmployerProfile_employerName__Xemli',
    '[class*="employerName"]',
    '[class*="EmployerProfile_name"]',
    '[class*="employer-name"]',
    'a[href*="/Overview/"]',
  ]);
  const company = companyEl ? companyEl.textContent!.trim() : null;

  const locationEl = first([
    '[data-test="location"]',
    '.JobDetails_location__HrGEz',
    '[class*="JobDetails_location"]',
    '[class*="location"]',
  ]);
  const location = locationEl ? locationEl.textContent!.trim() : null;

  const descEl = first([
    '[class*="JobDetails_jobDescription"]',
    '[data-test="jobDescriptionContent"]',
    '#JobDescriptionContainer',
    '[class*="jobDescription"]',
    '[class*="desc__text"]',
  ]);
  const jobDescription = descEl ? ((descEl as HTMLElement).innerText || descEl.textContent || '').trim() : null;

  const salaryEl = first([
    '[data-test="detailSalary"]',
    '[class*="SalaryEstimate"]',
    '[class*="salary"]',
  ]);
  const salaryRange = salaryEl ? salaryEl.textContent!.trim() : null;

  const workModel = inferWorkModel(location, jobDescription);

  sendMessage({ platform: 'Glassdoor', jobTitle, company, location, jobDescription, salaryRange, workModel });
} catch (err) {
  console.error('[JobApplica] Glassdoor script error:', err);
  sendMessage({ platform: 'Glassdoor', jobTitle: null, company: null });
}
