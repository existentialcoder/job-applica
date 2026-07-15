"""
All LLM calls centralised here.

New providers: subclass LLMProvider, implement complete(), add to _REGISTRY.
Provider selection per-operation is driven entirely by config — no code changes needed.

Config keys (all optional, fall back to LLM_PROVIDER / LLM_MODEL):
  LLM_PROVIDER          — global default provider
  LLM_ATS_PROVIDER      — override for ATS scoring
  LLM_SKILLS_PROVIDER   — override for skill extraction
  LLM_MODEL             — global default model (empty = provider default)
  LLM_ATS_MODEL         — override model for ATS scoring
  LLM_SKILLS_MODEL      — override model for skill extraction
"""

from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod

from ..schemas.ats import ATSReport

logger = logging.getLogger(__name__)


def _parse_json(text: str):
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text.strip())
    return json.loads(text.strip())


# ── Shared prompt templates ────────────────────────────────────────────────────

_ATS_SYSTEM = (
    'You are an expert ATS (Applicant Tracking System) analyser. '
    'The job description or resume may be in any language — understand them regardless of language. '
    'ALL JSON values — every string in every array — MUST be written in English. '
    'Return only valid JSON — no markdown fences, no explanation.'
)

_ATS_USER = """\
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

_JOB_EXTRACT_SYSTEM = (
    'You are a job-posting data extraction engine. '
    'Given raw text scraped from a web page, determine if it is a single job posting and extract structured data. '
    'ALL output values MUST be written in English. '
    'Return only valid JSON — no markdown fences, no explanation.'
)

_JOB_EXTRACT_USER = """\
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

  For the extracted company make sure to extract these details as well - [name, website, email, size, industry, description, logo_url].
  If any of these details are not present in the job posting, return them as null.
  If on job portal like Linkedin or Indeed use the company name to fetch the details from the company page and return them in the response.
  If not do a web search to extract the same. Return it as json in the company key itself

  Example - {{
    "name": "Acme Corp",
    "website": "https://www.acme.com",
    "email": "careers@acme.com",
    "size": 100,
    "industry": "Information Technology",
    "description": "Acme Corp is a leading provider of innovative solutions in the tech industry.",
    "logo_url": "https://www.acme.com/logo.png"
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

_TRANSLATE_SYSTEM = (
    'Translate the provided text to English. '
    'If the text is already in English, return it verbatim. '
    'Output only the translated text — no preamble, no explanation.'
)

_SKILL_SYSTEM = (
    'You extract technical skills from resumes. '
    'Return only a JSON array of strings — no explanation, no markdown.'
)

_SKILL_USER = """\
Extract all technical skills mentioned in this resume.

Include: programming languages, frameworks, libraries, databases, cloud platforms,
DevOps tools, messaging systems, methodologies (REST, OAuth, etc.).
Exclude: soft skills, education institutions, company names, job titles, years of experience.

<resume>
{cv}
</resume>

Return only a JSON array, e.g. ["Python", "FastAPI", "PostgreSQL"]."""


# ── Abstract base ──────────────────────────────────────────────────────────────

class LLMProvider(ABC):
    """
    Subclasses implement complete() only.
    All prompt logic and response parsing lives here in the base class.
    """

    @abstractmethod
    async def complete(self, system: str, user: str, max_tokens: int = 1024) -> str:
        """Call the model and return raw text."""
        ...

    async def translate_to_english(self, text: str) -> str:
        """Translate text to English; returns it unchanged if already English."""
        if not text or not text.strip():
            return text
        # Token budget: ~1.5× word count to handle expansions, cap at 8192
        max_tokens = min(max(len(text.split()) * 2, 512), 8192)
        return await self.complete(system=_TRANSLATE_SYSTEM, user=text, max_tokens=max_tokens)

    async def ats_score_report(
        self,
        resume_text: str,
        job_description: str,
        required_skills: list[str],
    ) -> ATSReport:
        skills_hint = (
            f'The role explicitly requires: {", ".join(required_skills)}.\n\n'
            if required_skills else ''
        )
        text = await self.complete(
            system=_ATS_SYSTEM,
            user=_ATS_USER.format(jd=job_description, cv=resume_text, skills_hint=skills_hint),
            max_tokens=2048,
        )
        data = _parse_json(text)

        return ATSReport(
            score=float(data['score']),
            matched_skills=data.get('matched_skills', []),
            matched_experience=data.get('matched_experience', []),
            missing_skills=data.get('missing_skills', []),
            experience_gaps=data.get('experience_gaps', []),
            suggestions=data.get('suggestions', []),
        )

    async def extract_job_from_page(self, page_text: str, url: str) -> dict:
        """Extract structured job data from raw page text. Returns is_job_page + fields."""
        text = await self.complete(
            system=_JOB_EXTRACT_SYSTEM,
            user=_JOB_EXTRACT_USER.format(url=url, page=page_text[:14000]),
            max_tokens=2048,
        )
        return _parse_json(text)

    async def extract_skills_from_resume(self, resume_text: str) -> list[str]:
        try:
            text = await self.complete(
                system=_SKILL_SYSTEM,
                user=_SKILL_USER.format(cv=resume_text),
                max_tokens=512,
            )
            return _parse_json(text)
        except Exception:
            logger.exception('Skill extraction failed — skipping')
            return []


# ── Anthropic ─────────────────────────────────────────────────────────────────

class AnthropicProvider(LLMProvider):
    DEFAULT_MODEL = 'claude-haiku-4-5-20251001'

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model

    async def complete(self, system: str, user: str, max_tokens: int = 1024) -> str:
        import anthropic
        client = anthropic.AsyncAnthropic()
        msg = await client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{'role': 'user', 'content': user}],
        )
        return msg.content[0].text


# ── DeepSeek ──────────────────────────────────────────────────────────────────

class DeepSeekProvider(LLMProvider):
    DEFAULT_MODEL = 'deepseek-chat'  # DeepSeek-V3
    _BASE_URL = 'https://api.deepseek.com'

    def __init__(self, model: str = DEFAULT_MODEL, use_cache: bool = True):
        self.model = model
        # use_cache=True: DeepSeek automatic prefix caching applies (server-side,
        # no API flag needed — repeated system prompts are cached at $0.07/1M vs $0.27/1M).
        # Set False to skip the system message entirely (breaks caching but saves tokens
        # when you don't need it).
        self.use_cache = use_cache

    async def complete(self, system: str, user: str, max_tokens: int = 1024) -> str:
        from openai import AsyncOpenAI
        from ..core.config import settings

        client = AsyncOpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url=self._BASE_URL)
        messages: list[dict] = []
        if system and self.use_cache:
            messages.append({'role': 'system', 'content': system})
        messages.append({'role': 'user', 'content': user})

        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ''


# ── Gemini ────────────────────────────────────────────────────────────────────

class GeminiProvider(LLMProvider):
    DEFAULT_MODEL = 'gemini-2.0-flash'  # free tier: 1500 req/day, 15 req/min
    _BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/openai/'

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model

    async def complete(self, system: str, user: str, max_tokens: int = 1024) -> str:
        from openai import AsyncOpenAI
        from ..core.config import settings

        client = AsyncOpenAI(api_key=settings.GEMINI_API_KEY, base_url=self._BASE_URL)
        messages: list[dict] = []
        if system:
            messages.append({'role': 'system', 'content': system})
        messages.append({'role': 'user', 'content': user})

        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or ''


# ── Registry & factory ─────────────────────────────────────────────────────────

_REGISTRY: dict[str, type[LLMProvider]] = {
    'anthropic': AnthropicProvider,
    'deepseek': DeepSeekProvider,
    'gemini': GeminiProvider,
}


def get_provider(purpose: str = '') -> LLMProvider:
    """
    Return the LLMProvider for a given purpose ('ats' | 'skills' | '').
    Reads LLM_CONFIG from settings — purpose key falls back to 'default'.
    """
    from ..core.config import settings

    cfg: dict = settings.LLM_CONFIG
    default_cfg: dict = cfg.get('default', {})
    purpose_cfg: dict = cfg.get(purpose, {}) if purpose else {}

    provider_name = purpose_cfg.get('provider') or default_cfg.get('provider') or 'anthropic'
    model = purpose_cfg.get('model') or default_cfg.get('model') or ''
    use_cache: bool = cfg.get('deepseek_cache', True)

    cls = _REGISTRY.get(provider_name, AnthropicProvider)

    if cls is DeepSeekProvider:
        return DeepSeekProvider(model=model or DeepSeekProvider.DEFAULT_MODEL, use_cache=use_cache)
    if cls is GeminiProvider:
        return GeminiProvider(model=model or GeminiProvider.DEFAULT_MODEL)
    return AnthropicProvider(model=model or AnthropicProvider.DEFAULT_MODEL)


# ── Module-level API (callers unchanged) ──────────────────────────────────────

async def ats_score_report(
    resume_text: str,
    job_description: str,
    required_skills: list[str],
) -> ATSReport:
    return await get_provider('ats').ats_score_report(resume_text, job_description, required_skills)


async def extract_skills_from_resume(resume_text: str) -> list[str]:
    return await get_provider('skills').extract_skills_from_resume(resume_text)


async def extract_job_from_page(page_text: str, url: str) -> dict:
    return await get_provider('extract').extract_job_from_page(page_text, url)
