(() => {
  try {
    // Select the main job container
    const parentDoc = document.querySelector('.job-view-layout');

    if (!parentDoc) {
      console.warn('Job view layout not found');
      chrome.runtime.sendMessage({ jobTitle: null, company: null });
      return;
    }

    // Find all <a> links inside the job container
    const jobLinks = Array.from(parentDoc.querySelectorAll('a'));

    // Filter links that include '/jobs/view' and take the first one as job title
    const jobTitleLink = jobLinks.filter(link => link.href.includes('/jobs/view'))[0];
    const jobTitle = jobTitleLink ? jobTitleLink.textContent.trim() : null;

    // Find company name
    const companyElem = parentDoc.querySelector(
      '.job-details-jobs-unified-top-card__company-name'
    );
    const company = companyElem ? companyElem.textContent.trim() : null;

    const metaData = parentDoc
      .querySelector('.job-details-jobs-unified-top-card__primary-description-container')
      .children[0].textContent.trim().split('·')

    const location = metaData[0].trim();

    const jobDescription = parentDoc.querySelector('article.jobs-description__container ')
      .querySelector('#job-details')
      .textContent.trim();

    // Send data to extension
    const sendMessage = (msg) => {
      if (typeof chrome !== 'undefined' && chrome.runtime?.sendMessage) {
        chrome.runtime.sendMessage(msg);
      } else if (typeof browser !== 'undefined' && browser.runtime?.sendMessage) {
        browser.runtime.sendMessage(msg);
      }
    };

    sendMessage({ jobTitle, company, location, jobDescription });
  } catch (error) {
    console.error('Error extracting LinkedIn job data:', error);
    const sendMessage = (msg) => {
      if (typeof chrome !== 'undefined' && chrome.runtime?.sendMessage) {
        chrome.runtime.sendMessage(msg);
      } else if (typeof browser !== 'undefined' && browser.runtime?.sendMessage) {
        browser.runtime.sendMessage(msg);
      }
    };
    sendMessage({ jobTitle: null, company: null });
  }
})();
