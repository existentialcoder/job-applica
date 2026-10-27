from src.services.geo import locale_from_cloudflare, search_cities


def test_country_and_currency_from_code():
    found = locale_from_cloudflare('de', 'M%C3%BCnchen')
    assert (found.country, found.city, found.currency) == ('Germany', 'München', 'EUR')


def test_names_match_the_frontend_country_list():
    assert locale_from_cloudflare('CZ', None).country == 'Czech Republic'
    assert locale_from_cloudflare('TR', None).country == 'Turkey'


def test_unknown_tor_and_missing_detect_nothing():
    for code in ('XX', 'T1', None, ''):
        assert locale_from_cloudflare(code, 'Berlin').country is None


def test_city_search_matches_prefixes_and_words_largest_first():
    names = [(c.city, c.country) for c in search_cities('ber')]
    assert names[0] == ('Berlin', 'Germany')
    assert all(city.lower().startswith('ber') for city, _ in names)
    assert ('Köln', 'Germany') in [(c.city, c.country) for c in search_cities('koln')]
    assert any(c.city == 'New York City' for c in search_cities('york'))
    assert search_cities('Munich')[0].currency == 'EUR'


def test_city_search_needs_two_letters():
    assert search_cities('b') == [] and search_cities(' ') == []
