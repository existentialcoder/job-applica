"""
All LLM calls centralised here.

New providers: subclass LLMProvider, implement _call(), add to _REGISTRY.
Provider selection per-operation is driven entirely by config — no code changes needed.

Config keys (all optional, fall back to LLM_PROVIDER / LLM_MODEL):
  LLM_PROVIDER          — global default provider
  LLM_ATS_PROVIDER      — override for ATS scoring
  LLM_PROFILE_PROVIDER  — override for CV profile extraction
  LLM_MODEL             — global default model (empty = provider default)
  LLM_ATS_MODEL         — override model for ATS scoring
  LLM_PROFILE_MODEL     — override model for CV profile extraction
"""

from __future__ import annotations

import json
import logging
import re
from abc import ABC, abstractmethod

from ..schemas.ats import ATSReport
from ..schemas.profile import ExtractedProfile
from . import prompts
from .redaction import assert_clean

logger = logging.getLogger(__name__)


def _parse_json(text: str):
    text = text.strip()
    if text.startswith('```'):
        text = re.sub(r'^```(?:json)?\s*', '', text)
        text = re.sub(r'\s*```$', '', text.strip())
    return json.loads(text.strip())


class LLMProvider(ABC):
    """
    Subclasses implement _call() only.
    All prompt logic and response parsing lives here in the base class.
    """

    @abstractmethod
    async def _call(self, system: str, user: str, max_tokens: int) -> tuple[str, int]:
        """Call the model; return raw text and the prompt token count."""
        ...

    async def complete(self, system: str, user: str, max_tokens: int = 1024) -> str:
        assert_clean(system, user)
        text, prompt_tokens = await self._call(system, user, max_tokens)
        logger.info('LLM call %s: %d prompt tokens', type(self).__name__, prompt_tokens)
        return text

    async def translate_to_english(self, text: str) -> str:
        """Translate text to English; returns it unchanged if already English."""
        if not text or not text.strip():
            return text
        # Token budget: ~1.5× word count to handle expansions, cap at 8192
        max_tokens = min(max(len(text.split()) * 2, 512), 8192)
        return await self.complete(system=prompts.TRANSLATE_SYSTEM, user=text, max_tokens=max_tokens)

    async def ats_score_report(
        self,
        resume_text: str,
        job_description: str,
        required_skills: list[str],
    ) -> ATSReport:
        skills_hint = f'The role explicitly requires: {", ".join(required_skills)}.\n\n' if required_skills else ''
        text = await self.complete(
            system=prompts.ATS_SYSTEM,
            user=prompts.ATS_USER.format(jd=job_description, cv=resume_text, skills_hint=skills_hint),
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
            system=prompts.JOB_EXTRACT_SYSTEM,
            user=prompts.JOB_EXTRACT_USER.format(url=url, page=page_text[:14000]),
            max_tokens=2048,
        )
        return _parse_json(text)

    async def extract_profile(self, cv_text: str) -> ExtractedProfile | None:
        """Structure a redacted CV; None when the model returns invalid JSON twice."""
        for attempt in (1, 2):
            text = await self.complete(
                system=prompts.PROFILE_SYSTEM,
                user=prompts.PROFILE_USER.format(cv=cv_text),
                max_tokens=4096,
            )
            try:
                return ExtractedProfile.model_validate(_parse_json(text))
            except ValueError:  # bad JSON or a schema mismatch (pydantic's ValidationError is a ValueError)
                logger.warning('Profile extraction returned invalid JSON (attempt %d)', attempt)
        return None


class AnthropicProvider(LLMProvider):
    DEFAULT_MODEL = 'claude-haiku-4-5-20251001'

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model

    async def _call(self, system: str, user: str, max_tokens: int) -> tuple[str, int]:
        import anthropic
        from anthropic.types import TextBlock

        client = anthropic.AsyncAnthropic()
        msg = await client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            system=system,
            messages=[{'role': 'user', 'content': user}],
        )
        block = msg.content[0]
        assert isinstance(block, TextBlock)  # no tool use / thinking is requested above
        return block.text, msg.usage.input_tokens


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

    async def _call(self, system: str, user: str, max_tokens: int) -> tuple[str, int]:
        from openai import AsyncOpenAI
        from openai.types.chat import ChatCompletionMessageParam

        from ..core.config import settings

        client = AsyncOpenAI(api_key=settings.DEEPSEEK_API_KEY, base_url=self._BASE_URL)
        messages: list[ChatCompletionMessageParam] = []
        if system and self.use_cache:
            messages.append({'role': 'system', 'content': system})
        messages.append({'role': 'user', 'content': user})

        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or '', response.usage.prompt_tokens if response.usage else 0


# ── Gemini ────────────────────────────────────────────────────────────────────


class GeminiProvider(LLMProvider):
    DEFAULT_MODEL = 'gemini-2.0-flash'  # free tier: 1500 req/day, 15 req/min
    _BASE_URL = 'https://generativelanguage.googleapis.com/v1beta/openai/'

    def __init__(self, model: str = DEFAULT_MODEL):
        self.model = model

    def _client(self):
        from openai import AsyncOpenAI

        from ..core.config import settings

        return AsyncOpenAI(api_key=settings.GEMINI_API_KEY, base_url=self._BASE_URL)

    async def _call(self, system: str, user: str, max_tokens: int) -> tuple[str, int]:
        from openai.types.chat import ChatCompletionMessageParam

        client = self._client()
        messages: list[ChatCompletionMessageParam] = []
        if system:
            messages.append({'role': 'system', 'content': system})
        messages.append({'role': 'user', 'content': user})

        response = await client.chat.completions.create(
            model=self.model,
            messages=messages,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content or '', response.usage.prompt_tokens if response.usage else 0


class OllamaProvider(GeminiProvider):
    # Context length is set in the Ollama model itself (Modelfile num_ctx); its OpenAI API can't change it.
    DEFAULT_MODEL = 'qwen3-4b-12k'

    def _client(self):
        from openai import AsyncOpenAI

        from ..core.config import settings

        return AsyncOpenAI(api_key='ollama', base_url=settings.OLLAMA_BASE_URL)


# ── Registry & factory ─────────────────────────────────────────────────────────

_REGISTRY: dict[str, type[LLMProvider]] = {
    'anthropic': AnthropicProvider,
    'deepseek': DeepSeekProvider,
    'gemini': GeminiProvider,
    'ollama': OllamaProvider,
}


def get_provider(purpose: str = '') -> LLMProvider:
    """
    Return the LLMProvider for a given purpose ('ats' | 'profile' | 'extract' | '').
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
    if cls in (GeminiProvider, OllamaProvider):
        return cls(model=model or cls.DEFAULT_MODEL)
    return AnthropicProvider(model=model or AnthropicProvider.DEFAULT_MODEL)


async def ats_score_report(
    resume_text: str,
    job_description: str,
    required_skills: list[str],
) -> ATSReport:
    return await get_provider('ats').ats_score_report(resume_text, job_description, required_skills)


async def extract_profile(cv_text: str) -> ExtractedProfile | None:
    return await get_provider('profile').extract_profile(cv_text)


async def extract_job_from_page(page_text: str, url: str) -> dict:
    return await get_provider('extract').extract_job_from_page(page_text, url)
