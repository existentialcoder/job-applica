import logging
import unicodedata
from functools import cache
from pathlib import Path
from urllib.parse import unquote

import httpx
from pydantic import BaseModel

from ..core.countries import COUNTRIES

logger = logging.getLogger(__name__)

NOMINATIM_URL = 'https://nominatim.openstreetmap.org/reverse'
# Cities of 15,000+ people from GeoNames (CC BY 4.0, https://www.geonames.org), most populous first:
# name, country code, population. Built from cities15000.txt, dropping city sections and historical places.
CITIES_FILE = Path(__file__).parent.parent / 'core' / 'data' / 'cities.tsv'


class DetectedLocale(BaseModel):
    country_code: str | None = None
    country: str | None = None
    city: str | None = None
    currency: str | None = None


def locale_from_cloudflare(country_code: str | None, city: str | None) -> DetectedLocale:
    """Country (and city, when the zone sends it) from Cloudflare's visitor-location headers.

    CF-IPCountry is 'XX' when unknown and 'T1' for Tor; both mean nothing was detected. Outside Cloudflare
    (local dev) the headers are absent.
    """
    code = (country_code or '').upper()
    if code not in COUNTRIES:
        return DetectedLocale()
    name, currency = COUNTRIES[code]
    return DetectedLocale(country_code=code, country=name, city=unquote(city) if city else None, currency=currency)


async def locale_from_coordinates(lat: float, lng: float) -> DetectedLocale:
    """Local-dev stand-in for Cloudflare's headers: reverse-geocode browser coordinates with OpenStreetMap."""
    # ~1 km precision is plenty for a city and keeps the exact position off the request.
    params: dict[str, float | int | str] = {
        'lat': round(lat, 2),
        'lon': round(lng, 2),
        'format': 'jsonv2',
        'zoom': 10,
        'accept-language': 'en',
    }
    try:
        async with httpx.AsyncClient(timeout=5.0, headers={'User-Agent': 'job-applica-local-dev'}) as client:
            r = await client.get(NOMINATIM_URL, params=params)
            r.raise_for_status()
            address = r.json().get('address', {})
    except (httpx.HTTPError, ValueError):
        logger.warning('Reverse geocoding failed')
        return DetectedLocale()
    city = address.get('city') or address.get('town') or address.get('village')
    return locale_from_cloudflare(address.get('country_code'), city)


def _fold(text: str) -> str:
    """Lowercase without accents or hyphens, so 'koln' finds Köln and 'aix en' finds Aix-en-Provence."""
    plain = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore').decode()
    return plain.casefold().replace('-', ' ')


@cache
def _cities() -> list[tuple[str, str, str]]:
    """(folded name, name, country code), most populous first."""
    rows = (line.split('\t') for line in CITIES_FILE.read_text(encoding='utf-8').splitlines())
    return [(_fold(name), name, code) for name, code, _ in rows]


def search_cities(query: str, limit: int = 10) -> list[DetectedLocale]:
    """Cities whose name, or a word in it, starts with the query; names that start with it come first.

    Names are as GeoNames spells them, so some are local (Köln) and some English (Munich).
    """
    # ponytail: linear scan of ~30k names (a few ms); move to a Postgres trigram index if it shows up in latency.
    q = _fold(query).strip()
    if len(q) < 2:
        return []
    starts, words = [], []
    for key, name, code in _cities():
        if key.startswith(q):
            starts.append((name, code))
        elif f' {q}' in key:
            words.append((name, code))
        if len(starts) >= limit:
            break
    return [locale_from_cloudflare(code, name) for name, code in (starts + words)[:limit]]
