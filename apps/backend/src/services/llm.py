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
  List every technical skill, language, framework, tool, methodology, and technology that is \
EXPLICITLY named in the resume text. Literal word match only — do NOT infer skills from context.
  Also extract any explicitly stated human languages and proficiency levels \
(e.g. "German C1", "English Native").

STEP 2 — Extract JD requirements (translate all terms to English):
  2a. Technical: every programming language, framework, tool, platform required or strongly preferred.
      For alternatives expressed as "X or Y", list each separately.
  2b. Language: any human language requirements (e.g. "fluent German", "business English").
      Mark mandatory language requirements with "(mandatory)".
  2c. Experience: years of experience, seniority, domain knowledge requirements.

STEP 3 — Match:
  matched_skills = resume items (Step 1) that directly satisfy a JD requirement (Step 2).
    Rules:
    • A skill covers an equivalent if the JD explicitly accepts it as an alternative
      (e.g. resume has "Java" → covers JD requirement "Go or Java").
    • Partial tool coverage counts: "GitHub Actions" covers "CI/CD pipelines".
    • Language match: only count a human language as matched if the resume proficiency
      meets or exceeds what the JD requires (A2 German does NOT match "fluent German").
  missing_skills = Step 2 requirements not covered by any resume item.
    • Include unmet mandatory language requirements (e.g. "Fluent German (mandatory)").
    • Include missing technical skills even if they are "nice to have".

STEP 4 — Score 0-100:
  Weight mandatory requirements (Go/Java backend, Kubernetes/Docker, fluent language) heavily.
  A hard-requirement gap (e.g. mandatory language not met) should lower the score significantly.
  Reflect experience depth and seniority alignment, not just skill checkbox coverage.

STEP 5 — Write 3-8 specific, actionable suggestions in English:
  Do not restate the missing skills list. Focus on how to reposition existing experience,
  reword bullets, add quantified outcomes, or bridge gaps credibly.

Return a JSON object with EXACTLY these fields:
{{
  "resume_skills": [...],
  "score": <integer>,
  "matched_skills": [...],
  "missing_skills": [...],
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
  location         — city / region / country where the role is based (translate to English if needed)
  description      — clean body of the job posting: responsibilities + requirements.
                     Remove navigation menus, cookie banners, "apply now" buttons, and other page chrome.
  salary_range     — compensation if explicitly stated (e.g. "€50,000–€70,000/yr"), else null
  work_model       — exactly one of: "On-site", "Remote", "Hybrid" — infer from context when not stated
  position         — seniority: one of "Intern", "Junior", "Mid", "Senior", "Lead", "Manager" — infer when possible, else null
  years_of_experience — {{ "min": <int>, "max": <int> }} when a range is mentioned, else null
  required_skills  — array of technical skills, tools, languages, and frameworks explicitly required or strongly preferred

STEP 3 — If is_job_page is false, return all other fields as null / [].

<page_url>{url}</page_url>

<page_text>
{page}
</page_text>

Return exactly this shape:
{{
  "is_job_page": true,
  "title": "...",
  "company": "...",
  "location": "...",
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
        data = json.loads(text)

        def _in_resume_text(skill: str) -> bool:
            """Word-boundary search against the raw resume text — the only reliable ground truth."""
            try:
                pattern = r'(?<![A-Za-z0-9])' + re.escape(skill) + r'(?![A-Za-z0-9])'
                return bool(re.search(pattern, resume_text, re.IGNORECASE))
            except re.error:
                return skill.lower() in resume_text.lower()

        matched = [s for s in data.get('matched_skills', []) if _in_resume_text(s)]

        return ATSReport(
            score=float(data['score']),
            matched_skills=matched,
            missing_skills=data.get('missing_skills', []),
            suggestions=data.get('suggestions', []),
        )

    async def extract_job_from_page(self, page_text: str, url: str) -> dict:
        """Extract structured job data from raw page text. Returns is_job_page + fields."""
        text = await self.complete(
            system=_JOB_EXTRACT_SYSTEM,
            user=_JOB_EXTRACT_USER.format(url=url, page=page_text[:14000]),
            max_tokens=2048,
        )
        return json.loads(text)

    async def extract_skills_from_resume(self, resume_text: str) -> list[str]:
        try:
            text = await self.complete(
                system=_SKILL_SYSTEM,
                user=_SKILL_USER.format(cv=resume_text),
                max_tokens=512,
            )
            return json.loads(text)
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
