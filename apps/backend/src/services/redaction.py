"""Removes contact details from text before it reaches an LLM, and checks outgoing prompts for leftovers."""

import logging
import re
from collections.abc import Iterable
from dataclasses import dataclass, field

import phonenumbers

logger = logging.getLogger(__name__)

_PHONE_REGIONS = ('DE', 'US', 'GB', 'IN', 'FR', 'NL', 'AT', 'CH', 'ES', 'IT', 'CA', 'AU')

_EMAIL = re.compile(
    r'(?:mailto:)?[\w.+-]+@[\w-]+(?:\.[\w-]+)+'
    r'|[\w.+-]+\s*[\[(]\s*at\s*[\])]\s*[\w-]+(?:\s*[\[(]\s*dot\s*[\])]\s*[\w-]+)+',
    re.IGNORECASE,
)

_PROFILE_SITES = {
    'linkedin.com': '[LINKEDIN]',
    'github.com': '[GITHUB]',
    'gitlab.com': '[GITHUB]',
    'xing.com': '[PROFILE]',
    'stackoverflow.com': '[PROFILE]',
    'kaggle.com': '[PROFILE]',
    'medium.com': '[PROFILE]',
    'behance.net': '[PROFILE]',
    'dribbble.com': '[PROFILE]',
    'twitter.com': '[PROFILE]',
    'x.com': '[PROFILE]',
    'instagram.com': '[PROFILE]',
    't.me': '[PROFILE]',
}
_SITES = '|'.join(re.escape(s) for s in _PROFILE_SITES)
# A URL never ends in sentence punctuation ("see acme.dev/jobs.").
_PATH = r'[^\s<>()"\']*[^\s<>()"\'.,;:!?]'
_URL = re.compile(
    rf'(?:https?://|www\.){_PATH}|\b(?:[\w-]+\.)*(?:{_SITES})/(?:{_PATH})?',
    re.IGNORECASE,
)
_PERSONAL_DOMAIN = re.compile(rf'\b[\w-]+(?:\.[\w-]+)*\.(?:dev|me|page|site|portfolio)\b(?:/(?:{_PATH})?)?', re.I)

_DOB_LINE = re.compile(
    r'^[ \t•*·\-–]*(?:date of birth|birth ?date|d\.?o\.?b\.?|born|geburtsdatum|geboren|geb\.)\s*:\s*\S.*$',
    re.IGNORECASE | re.MULTILINE,
)
_DOB_INLINE = re.compile(
    r'\b(?:born|geb\.|geboren)\s*(?:on|am)?\s*\d{1,2}[./-]\s?\d{1,2}[./-]\s?\d{2,4}|\b(?:born|geboren)\s+(?:in\s+)?\d{4}\b',
    re.IGNORECASE,
)

# ponytail: street + house number (DE/EN style), optionally followed by postcode + city; other formats pass through.
_ADDRESS = re.compile(
    r"(?:\b[\wäöüß.-]*(?:straße|strasse|str\.|weg|allee|platz|gasse|damm|ring)\s+\d+\s?[a-z]?\b"
    r"|\b\d+[a-z]?\s+(?:[A-Z][\w.'-]*\s+){1,3}(?:Street|St\.|Avenue|Ave\.|Road|Rd\.|Lane|Ln\.|Drive|Dr\.|Boulevard|Blvd\.))"
    r"(?:,?\s*\d{4,5}\s+[A-ZÄÖÜ][\wäöüß-]+)?",
    re.IGNORECASE,
)


class RedactionLeak(Exception):
    """An outgoing prompt still contains an email or phone number."""


@dataclass
class Redacted:
    text: str
    emails: list[str] = field(default_factory=list)
    phones: list[str] = field(default_factory=list)
    urls: list[str] = field(default_factory=list)


# Some regions' rules accept dates and CV date ranges ("01.03.2019", "2019-03-01", "04/2024 – 09/2024") as phone
# numbers; a match containing one is never a phone.
_DATE = re.compile(
    r'\d{1,2}[./-]\d{1,2}[./-]\d{2,4}|\d{4}[./-]\d{1,2}[./-]\d{1,2}|(?<!\d)(?:0?[1-9]|1[0-2])[./](?:19|20)\d{2}(?!\d)'
)


def _phone_spans(text: str) -> list[tuple[int, int, str]]:
    # IDs in URLs (e.g. linkedin.com/jobs/view/4459203782) look like phone numbers to the matcher.
    urls = [m.span() for m in _URL.finditer(text)]
    spans: dict[tuple[int, int], str] = {}
    for region in _PHONE_REGIONS:
        for match in phonenumbers.PhoneNumberMatcher(text, region):
            if _DATE.search(match.raw_string) or any(s <= match.start and match.end <= e for s, e in urls):
                continue
            spans.setdefault(
                (match.start, match.end),
                phonenumbers.format_number(match.number, phonenumbers.PhoneNumberFormat.E164),
            )
    # Different regions can match overlapping slices of one number; keep the longest.
    kept: list[tuple[int, int, str]] = []
    for (start, end), number in sorted(spans.items(), key=lambda s: (s[0][0], -(s[0][1] - s[0][0]))):
        if not kept or start >= kept[-1][1]:
            kept.append((start, end, number))
    return kept


def url_placeholder(url: str) -> str:
    host = re.sub(r'^(?:https?://)?(?:www\.)?', '', url.lower()).split('/')[0]
    for site, placeholder in _PROFILE_SITES.items():
        if host == site or host.endswith('.' + site):
            return placeholder
    return '[WEBSITE]'


def redact(text: str, names: Iterable[str] = ()) -> Redacted:
    """Replace emails, phones, street addresses, profile links, birth dates and the given names with placeholders."""
    result = Redacted(text=text)

    def email(m: re.Match) -> str:
        result.emails.append(m.group(0).removeprefix('mailto:'))
        return '[EMAIL]'

    def url(m: re.Match) -> str:
        result.urls.append(m.group(0))
        return url_placeholder(m.group(0))

    out = _DOB_LINE.sub('[DOB]', text)
    out = _DOB_INLINE.sub('[DOB]', out)
    out = _ADDRESS.sub('[ADDRESS]', out)
    out = _EMAIL.sub(email, out)
    out = _URL.sub(url, out)
    out = _PERSONAL_DOMAIN.sub(url, out)

    for start, end, number in reversed(_phone_spans(out)):
        result.phones.insert(0, number)
        out = f'{out[:start]}[PHONE]{out[end:]}'

    if wanted := sorted({n.strip() for n in names if len(n.strip()) > 1}, key=len, reverse=True):
        alts = '|'.join(re.escape(n) for n in wanted)
        # Placeholders are matched first and kept, so a name like "Name" or "Link" can't eat "[NAME]"/"[LINKEDIN]".
        # Scraped text glues elements together ("and moreJane and"), so lowercase-to-Capital also counts as an edge.
        pattern = rf'(\[[A-Z]+\])|(?:\b|(?<=[a-z]))(?i:{alts})(?:\b|(?=[A-Z]))'
        out = re.sub(pattern, lambda m: m.group(1) or '[NAME]', out)

    result.text = out
    return result


def assert_clean(*texts: str) -> None:
    """Raise RedactionLeak if any email or phone number survives in the text about to be sent."""
    for text in texts:
        kinds = [kind for kind, found in (('email', _EMAIL.search(text)), ('phone', _phone_spans(text))) if found]
        if kinds:
            logger.error('Blocked LLM call: outgoing prompt contains %s', ', '.join(kinds))
            raise RedactionLeak(kinds)
