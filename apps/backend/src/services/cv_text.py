"""Plain text from an uploaded CV file."""

import io
from typing import Any

import pdfplumber
from docx import Document
from docx.opc.constants import RELATIONSHIP_TYPE

# A gutter counts as a column break when at most this share of the page's words straddle it…
MAX_CROSSING_SHARE = 0.02
# …and each side holds at least this share of the words (a narrow contact sidebar can be ~10%).
MIN_SIDE_SHARE = 0.05


def column_split(words: list[dict[str, Any]], width: float) -> float | None:
    """x of the gutter in a two-column page, or None for a single column.

    A vertical line through single-column text lands on a word in most lines, so it never qualifies.
    """
    if len(words) < 40:
        return None
    best: tuple[int, float] | None = None
    for x in range(int(width * 0.15), int(width * 0.6), 2):
        crossing = sum(1 for w in words if w['x0'] < x < w['x1'])
        left = sum(1 for w in words if w['x1'] <= x)
        right = len(words) - left - crossing
        if crossing <= max(2, len(words) * MAX_CROSSING_SHARE) and min(left, right) >= len(words) * MIN_SIDE_SHARE:
            if best is None or crossing < best[0]:
                best = (crossing, x)
    return best[1] if best else None


def _page_text(page: Any) -> str:
    # Read line by line, a two-column CV interleaves its columns ("Germany" lands mid-sentence in a job).
    split = column_split(page.extract_words(), page.width)
    if split is None:
        text = page.extract_text() or ''
    else:
        left = page.crop((0, 0, split, page.height)).extract_text() or ''
        right = page.crop((split, 0, page.width, page.height)).extract_text() or ''
        text = f'{left}\n{right}'
    # "LinkedIn" / "GitHub" are often just labels on clickable links; the URLs live in the link annotations.
    uris = [link['uri'] for link in page.hyperlinks if link.get('uri')]
    return '\n'.join([text, *dict.fromkeys(uris)])


def cv_text(content_type: str | None, data: bytes) -> str:
    if content_type == 'application/pdf':
        with pdfplumber.open(io.BytesIO(data)) as pdf:
            return '\n'.join(_page_text(page) for page in pdf.pages)
    doc = Document(io.BytesIO(data))
    uris = [r.target_ref for r in doc.part.rels.values() if r.reltype == RELATIONSHIP_TYPE.HYPERLINK]
    return '\n'.join([*(p.text for p in doc.paragraphs), *dict.fromkeys(uris)])
