from fastapi import APIRouter, Header, Query

from ....core.config import settings
from ....services.geo import DetectedLocale, locale_from_cloudflare, locale_from_coordinates, search_cities

router = APIRouter(prefix='/geo')


@router.get('/locale', response_model=DetectedLocale, description="The caller's country, city and currency")
async def detect_locale(
    lat: float | None = None,
    lng: float | None = None,
    cf_ipcountry: str | None = Header(None),
    cf_ipcity: str | None = Header(None),  # only sent when the zone has "Add visitor location headers" on
):
    found = locale_from_cloudflare(cf_ipcountry, cf_ipcity)
    # Locally there's no Cloudflare in front, so fall back to the browser's coordinates. Never in other
    # environments: coordinates would go to a third-party geocoder.
    if found.country is None and settings.APP_ENV == 'local' and lat is not None and lng is not None:
        found = await locale_from_coordinates(lat, lng)
    return found


@router.get('/cities', response_model=list[DetectedLocale], description='Cities matching the query, largest first')
async def find_cities(q: str = Query(..., max_length=100)):
    return search_cities(q)
