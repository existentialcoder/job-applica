import asyncio

import pytest

from src.services import llm
from src.services.redaction import RedactionLeak, assert_clean, redact


@pytest.mark.parametrize(
    'phone',
    [
        '+49 151 23456789',
        '0151 23456789',
        '0151/2345678',
        '+1 (415) 555-0132',
        '(415) 555-0132',
        '+44 20 7946 0958',
        '+91 98765 43210',
        '+33 6 12 34 56 78',
    ],
)
def test_phone_formats(phone):
    r = redact(f'Call me on {phone} any time.')
    assert r.text == 'Call me on [PHONE] any time.'
    assert len(r.phones) == 1 and r.phones[0].startswith('+')


def test_dates_and_years_are_not_phones():
    text = (
        'Backend Engineer, 2019 - 2023, 01.03.2019 - 31.12.2023, 2019-03-01, 04/2024 – 09/2024, 06/2019 - 10/2021, '
        '03.2020 – 12.2022. Grew revenue 30% to 1,200,000 EUR.'
    )
    assert redact(text).text == text


@pytest.mark.parametrize('email', ['jane.doe+jobs@example.co.uk', 'mailto:jane@example.com'])
def test_emails(email):
    r = redact(f'Email: {email}')
    assert r.text == 'Email: [EMAIL]'
    assert r.emails == [email.removeprefix('mailto:')]


@pytest.mark.parametrize(
    ('url', 'placeholder'),
    [
        ('https://www.linkedin.com/in/jane-doe', '[LINKEDIN]'),
        ('linkedin.com/in/jane-doe', '[LINKEDIN]'),
        ('www.linkedin.com/in/jane-doe/', '[LINKEDIN]'),
        ('github.com/janedoe', '[GITHUB]'),
        ('gitlab.com/janedoe', '[GITHUB]'),
        ('stackoverflow.com/users/123/jane', '[PROFILE]'),
        ('x.com/janedoe', '[PROFILE]'),
        ('https://janedoe.dev/portfolio', '[WEBSITE]'),
        ('janedoe.dev', '[WEBSITE]'),
        ('jane-doe.me/work', '[WEBSITE]'),
    ],
)
def test_urls(url, placeholder):
    r = redact(f'Profile: {url} (updated)')
    assert r.text == f'Profile: {placeholder} (updated)'
    assert r.urls == [url]


def test_url_keeps_trailing_punctuation_out():
    r = redact('See https://acme.example/careers. Or linkedin.com/in/jane, janedoe.dev!')
    assert r.text == 'See [WEBSITE]. Or [LINKEDIN], [WEBSITE]!'
    assert r.urls == ['https://acme.example/careers', 'linkedin.com/in/jane', 'janedoe.dev']


def test_company_domains_and_skills_stay():
    text = 'Worked at Booking.com and Amazon.com on Socket.io, Node.js and ASP.NET services.'
    assert redact(text).text == text


def test_disguised_email():
    assert redact('mail jane.doe [at] example [dot] com').text == 'mail [EMAIL]'


@pytest.mark.parametrize(
    'line',
    ['Date of birth: 01.02.1990', 'DOB: 1990-02-01', '• Geburtsdatum: 01.02.1990', 'geb.: 01.02.1990'],
)
def test_dob_lines(line):
    assert redact(f'Jane\n{line}\nSkills').text == 'Jane\n[DOB]\nSkills'


def test_dob_inline_and_employment_dates_stay():
    r = redact('Jane Doe, geb. 01.02.1990, born in 1990. Acme 01.03.2019 - 31.12.2023')
    assert r.text == 'Jane Doe, [DOB], [DOB]. Acme 01.03.2019 - 31.12.2023'


def test_own_name_whole_words_only():
    r = redact('JANE DOE, Senior Engineer. Jane led Doering GmbH migrations.', names=('Jane', 'Doe'))
    assert r.text == '[NAME] [NAME], Senior Engineer. [NAME] led Doering GmbH migrations.'


def test_leak_check_blocks_and_passes():
    assert_clean('Senior Engineer with [EMAIL] and [PHONE]')
    with pytest.raises(RedactionLeak):
        assert_clean('reach me at jane@example.com')
    with pytest.raises(RedactionLeak):
        assert_clean('ok', 'call +49 151 23456789')


def test_ids_in_urls_are_not_phones():
    assert_clean('Job page: https://www.linkedin.com/jobs/view/4459203782/?refId=abc')
    with pytest.raises(RedactionLeak):
        assert_clean('https://example.com/jobs call +1 (415) 555-0132')


def test_prompt_templates_pass_leak_check():
    for template in (
        llm._ATS_SYSTEM,
        llm._ATS_USER,
        llm._SKILL_SYSTEM,
        llm._SKILL_USER,
        llm._JOB_EXTRACT_SYSTEM,
        llm._JOB_EXTRACT_USER,
        llm._TRANSLATE_SYSTEM,
    ):
        assert_clean(template)


def test_provider_never_called_on_leak():
    calls = []

    class Fake(llm.LLMProvider):
        async def _call(self, system, user, max_tokens):
            calls.append(user)
            return '[]', 1

    with pytest.raises(RedactionLeak):
        asyncio.run(Fake().complete('sys', 'cv with jane@example.com'))
    assert calls == []


def test_name_glued_to_neighbouring_words():
    r = redact('Learn moreJane and millions use PremiumJaneDoe. Doering GmbH', names=('Jane', 'Doe'))
    assert r.text == 'Learn more[NAME] and millions use Premium[NAME][NAME]. Doering GmbH'


def test_names_never_touch_placeholders():
    r = redact('Mail: jane@example.com, linkedin.com/in/x. Link Name here.', names=('Name', 'Link', 'Email'))
    assert r.text == 'Mail: [EMAIL], [LINKEDIN]. [NAME] [NAME] here.'


@pytest.mark.parametrize(
    'address',
    ['Musterstraße 12, 56068 Koblenz', 'Hauptstr. 5a', 'Rosenweg 3 10115 Berlin', '221 Baker Street', '1600 Pennsylvania Ave.'],
)
def test_street_addresses(address):
    assert redact(f'Lives at {address}\nSkills').text == 'Lives at [ADDRESS]\nSkills'


def test_non_addresses_stay():
    text = 'Grew revenue to 50000 EUR, 3 Senior Engineers, Ring buffer, 10 Downing roles. Koblenz, Germany'
    assert redact(text).text == text
