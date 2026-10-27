"""Prompt text for every LLM call; services/llm.py fills the templates and sends them."""

ATS_SYSTEM = (
    'You are an expert ATS (Applicant Tracking System) analyser. '
    'The job description or resume may be in any language — understand them regardless of language. '
    'ALL JSON values — every string in every array — MUST be written in English. '
    'Return only valid JSON — no markdown fences, no explanation.'
)

ATS_USER = """\
Follow these steps in order, then return a single JSON object.

STEP 1 — Extract resume skills:
  List every technical skill, programming language, framework, tool, methodology, and technology
  EXPLICITLY named in the resume. Use the canonical common name (e.g. "Vue.js" not "Vue 3 framework",
  "GitHub Actions" not "GH Actions"). Do NOT infer — literal match only.
  Also extract explicitly stated human languages with proficiency (e.g. "German C1", "English Native").

STEP 2 — Extract JD requirements from the <job_description> block ONLY:
  ⚠ STRICT RULE: Every item must be a direct quote or clear paraphrase of words that appear in the
  <job_description> block. NEVER infer from the resume or from general industry assumptions.

  2a. Technical skills: every programming language, framework, tool, or platform the JD explicitly
      requires or strongly prefers. List each separately ("Go or Java" → "Go", "Java").
  2b. Human languages: ONLY if the JD text explicitly requires them ("fluent German required").
      If the JD is silent on spoken/written language, leave this empty.
  2c. Experience & domain: years of experience, seniority level, domain knowledge, or specific
      platform familiarity the JD calls out (e.g. "2–4 years experience", "Workday or HR platform
      familiarity", "enterprise SDLC/ITGC exposure").

STEP 3 — Match and gap analysis. Populate four arrays:

  matched_skills:
    Skill/tool names from Step 1 that satisfy a Step 2a or 2b requirement.
    ⚠ Rules:
    • Skill names ONLY — no experience phrases (wrong: "API development experience", right: "FastAPI").
    • One entry per distinct skill — no duplicates even if the JD names the same skill twice.
    • Equivalents count if the JD explicitly accepts them (e.g. "Vue.js" covers "React/Vue").
    • Partial coverage counts ("GitHub Actions" covers "CI/CD pipelines").
    • Language only if explicitly required in Step 2b AND resume proficiency meets or exceeds it.

  matched_experience:
    Step 2c requirements the resume satisfies. Short descriptive phrases, not skill names.
    (e.g. "5+ years full-stack experience", "API integration delivery", "cloud deployment experience")

  missing_skills:
    Step 2a/2b requirements NOT covered by the resume. Use the exact name from the JD.
    Skill and tool names ONLY — no experience phrases. Do NOT include domain or seniority gaps here.
    (e.g. "Workday", "Azure Pipelines", "PHP")

  experience_gaps:
    Step 2c requirements the resume does NOT satisfy. Include seniority mismatches in both directions
    (overqualified or underqualified), missing domain knowledge, and platform-specific experience.
    (e.g. "HR/workforce platform experience", "candidate has ~6 years vs JD's 2–4 year target")

STEP 4 — Score 0–100:
  Weight all Step 2 requirements: technical (2a), language (2b), and experience/domain (2c).
  Penalise hard mandatory gaps heavily. Reward strong seniority and domain alignment.
  Seniority mismatch in either direction should moderately reduce the score.

STEP 5 — Write 3–8 specific, actionable suggestions in English:
  • Reference specific resume items by name — actual project names, companies, metrics, technologies.
  • Focus on repositioning existing experience, rewording bullets, adding quantified outcomes.
  • Do NOT restate missing_skills or experience_gaps verbatim — suggest how to address them.
  • If the candidate appears overqualified, advise how to frame the application for this role.

Return a JSON object with EXACTLY these fields:
{{
  "resume_skills": [...],
  "score": <integer>,
  "matched_skills": [...],
  "matched_experience": [...],
  "missing_skills": [...],
  "experience_gaps": [...],
  "suggestions": [...]
}}

{skills_hint}<job_description>
{jd}
</job_description>

<resume>
{cv}
</resume>"""

JOB_EXTRACT_SYSTEM = (
    'You are a job-posting data extraction engine. '
    'Given raw text scraped from a web page, determine if it is a single job posting and extract structured data. '
    'ALL output values MUST be written in English. '
    'Return only valid JSON — no markdown fences, no explanation.'
)

JOB_EXTRACT_USER = """\
Analyse the page text and return a single JSON object.

STEP 1 — Decide: is this a single job posting?
  Set "is_job_page" true only when the page describes ONE specific open role with a title and duties.
  Set false for job-search result pages, company overview pages, blog posts, or anything else.

STEP 2 — If is_job_page is true, extract every field below. All strings must be in English.
  title            — job title
  company          — company or organisation name
  location         — structured object with city, state (optional), country (see format below)
  description      — clean body of the job posting: responsibilities + requirements.
                     Remove navigation menus, cookie banners, "apply now" buttons, and other page chrome.
  salary_range     — if ONE salary is stated, return it as-is (e.g. "€50,000/yr").
                     If multiple location-based tiers are listed, return the tier that matches the
                     extracted location. If no location match, return the lowest–highest as a range.
                     Return null if no compensation is mentioned.
  work_model       — exactly one of: "On-site", "Remote", "Hybrid" — infer from context when not stated.
                     If the posting says "remote" anywhere in the location or role description, prefer "Remote".
  position         — infer seniority from the job title AND stated experience requirements.
                     Use these rules in order:
                     1. Title contains "Intern", "Trainee", "Apprentice" → "Intern"
                     2. Title contains "Junior", "Associate", "Entry" → "Junior"
                     3. Title contains "Senior", "Sr.", "Principal", "Staff" → "Senior"
                     4. Title contains "Lead", "Architect" → "Lead"
                     5. Title contains "Manager", "Director", "Head of", "VP" → "Manager"
                     6. No seniority prefix (e.g. "Account Executive", "Engineer", "Analyst") → "Mid";
                        bump to "Senior" if the JD requires 5+ years of experience.
                     Return null only if genuinely impossible to infer.
  years_of_experience — extract from experience phrases:
                     "3+ years" → {{"min": 3, "max": null}}
                     "2–4 years" → {{"min": 2, "max": 4}}
                     "up to 5 years" → {{"min": null, "max": 5}}
                     "at least 2 years" → {{"min": 2, "max": null}}
                     Return null if no experience requirement is mentioned.
  required_skills  — array of technical skills, tools, programming languages, and frameworks explicitly required or strongly preferred.
                     Do NOT include human/spoken languages (e.g. German, English) here — only software and technical skills.

  For the extracted company make sure to extract these details as well - [name, website, email, size, industry, description].
  If any of these details are not present in the job posting, return them as null.
  If on job portal like Linkedin or Indeed use the company name to fetch the details from the company page and return them in the response.
  If not do a web search to extract the same. Return it as json in the company key itself

  Example - {{
    "name": "Acme Corp",
    "website": "https://www.acme.com",
    "email": "[EMAIL]",
    "size": 100,
    "industry": "Information Technology",
    "description": "Acme Corp is a leading provider of innovative solutions in the tech industry."
  }}

  For the extracted location, return a JSON object with these fields:
    city    — city name, null if fully remote and not mentioned
    state   — state or province, null if not mentioned
    country — country name in English, always required (empty string if truly unknown)

  Example 1 - {{ "city": "New York", "state": "NY", "country": "USA" }}
  Example 2 - {{ "city": "Dusseldorf", "state": "North Rhine-Westphalia", "country": "Germany" }}
  Example 3 - {{ "city": null, "state": null, "country": "United Kingdom" }}
STEP 3 — If is_job_page is false, return all other fields as null / [].

<page_url>{url}</page_url>

<page_text>
{page}
</page_text>

Return exactly this shape:
{{
  "is_job_page": true,
  "title": "...",
  "company": {{}},
  "location": {{}},
  "description": "...",
  "salary_range": null,
  "work_model": "On-site",
  "position": null,
  "years_of_experience": null,
  "required_skills": []
}}"""

TRANSLATE_SYSTEM = (
    'Translate the provided text to English. '
    'If the text is already in English, return it verbatim. '
    'Output only the translated text — no preamble, no explanation.'
)

PROFILE_SYSTEM = (
    'You turn a CV into structured JSON. Contact details were replaced with placeholders such as [NAME], [EMAIL], '
    '[PHONE] or [ADDRESS]; never copy a placeholder into a value. Keep values in the language of the CV. '
    'Return only valid JSON — no markdown fences, no explanation.'
)

PROFILE_USER = """\
Read the CV and return one JSON object with exactly these keys:

{{
  "headline": "one line describing the person professionally, e.g. \"Senior backend engineer\"" or null,
  "summary": "always filled: the CV's own summary or profile section, lightly cleaned up; if it has none, write 2-3 sentences from the CV's experience and skills, e.g. \"Backend engineer with 7 years building payment systems in Python and Go.\"",
  "years_experience": whole years of professional experience, or null if unclear,
  "experience": [{{"title": "...", "company": "..." or null,
                  "company_website": "employer's main website, e.g. \"https://www.sap.com\", if the CV states it or the company is widely known, else null",
                  "start": "YYYY-MM" or null,
                  "end": "YYYY-MM" or null if ongoing, "highlights": ["achievements, as written"],
                  "work_model": "On-site", "Remote" or "Hybrid" if the CV says so, else null,
                  "job_type": "Full-time", "Part-time" or "Contract" if the CV says so, else null,
                  "seniority": "Intern", "Junior", "Mid", "Senior", "Lead" or "Manager" as the title implies, else null}}],
  "education": [{{"institution": "...", "degree": "..." or null, "field": "..." or null,
                 "start": "YYYY-MM" or null, "end": "YYYY-MM" or null}}],
  "skills": ["technical skills, tools and methods named in the CV, canonical names, no soft skills"],
  "languages": [{{"name": "spoken language in English, e.g. \"German\"", "level": "A1-C2, \"Native\", or null if not stated"}}],
  "certifications": [{{"name": "...", "issuer": "..." or null, "year": 2023 or null}}],
  "awards": [{{"title": "...", "issuer": "..." or null, "year": 2023 or null}}],
  "location": {{"city": "..." or null, "country": "country name in English, e.g. \"Germany\"" or null}} or null
}}

"location" is where the person lives, from the header or contact section; never an employer's or school's location.

List experience newest first. Apart from headline, summary and seniority, which you work out from the CV, use only what the CV states; leave a value null rather than guess.

<cv>
{cv}
</cv>"""
