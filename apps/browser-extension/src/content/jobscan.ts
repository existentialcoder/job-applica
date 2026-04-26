import { sendMessage, first } from './common';

try {
  const titleEl = first([
    '[class*="job-title"]',
    '[class*="position"]',
    'h1',
  ]);
  const jobTitle = titleEl ? titleEl.textContent!.trim() : null;

  const companyEl = first([
    '[class*="company"]',
    '[class*="employer"]',
  ]);
  const company = companyEl ? companyEl.textContent!.trim() : null;

  // Jobscan may store the description in a textarea
  const descTextarea = document.querySelector<HTMLTextAreaElement>('textarea[name*="job"]');
  const descEl = first(['[class*="job-description"]']);
  const jobDescription = descTextarea?.value?.trim()
    || ((descEl as HTMLElement | null)?.innerText || descEl?.textContent || '').trim()
    || null;

  sendMessage({ platform: 'Jobscan', jobTitle, company, jobDescription, location: null });
} catch (err) {
  console.error('[JobApplica] Jobscan script error:', err);
  sendMessage({ platform: 'Jobscan', jobTitle: null, company: null });
}
