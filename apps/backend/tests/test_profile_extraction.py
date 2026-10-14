import asyncio
import json

from src.schemas.profile import ExperienceEntry, ExtractedProfile
from src.services import llm
from src.services.redaction import contacts_from, redact


def _profile(*jobs: tuple[str, str | None, str | None]) -> ExtractedProfile:
    return ExtractedProfile(experience=[ExperienceEntry(title=t, start=s, end=e) for t, s, e in jobs])


def test_current_role_is_the_ongoing_one():
    p = _profile(('Lead', '2021-01', '2023-06'), ('Staff', '2023-07', None), ('Dev', '2015-01', '2020-12'))
    assert p.current_role().title == 'Staff'


def test_current_role_falls_back_to_latest_start():
    p = _profile(('Dev', '2015-01', '2020-12'), ('Lead', '2021-01', '2023-06'))
    assert p.current_role().title == 'Lead'


def test_current_role_none_without_experience():
    assert ExtractedProfile().current_role() is None


def test_contacts_keep_account_email_primary():
    found = redact(
        'jane.doe@gmail.com · +49 151 23456789 · linkedin.com/in/janedoe · github.com/jdoe · https://jane.dev'
    )
    assert contacts_from(found, 'jane@work.com') == {
        'email': 'jane@work.com',
        'secondary_email': 'jane.doe@gmail.com',
        'phone': '+4915123456789',
        'linkedin_url': 'linkedin.com/in/janedoe',
        'github_url': 'github.com/jdoe',
        'portfolio_url': 'https://jane.dev',
    }


def test_contacts_use_cv_email_when_account_has_none():
    assert contacts_from(redact('Reach me: jane.doe@gmail.com'), None) == {'email': 'jane.doe@gmail.com'}


def _fake(replies: list[str]):
    class Fake(llm.LLMProvider):
        async def _call(self, system, user, max_tokens):
            return replies.pop(0), 1

    return Fake()


def test_extract_profile_retries_invalid_json_once():
    good = json.dumps({'headline': 'Backend engineer', 'experience': [{'title': 'Dev', 'end': None}]})
    result = asyncio.run(_fake(['not json', good]).extract_profile('[NAME] Backend engineer'))
    assert result is not None and result.headline == 'Backend engineer'


def test_extract_profile_reads_languages_certifications_awards():
    reply = json.dumps(
        {
            'languages': [{'name': 'German', 'level': 'C1'}, {'name': 'English', 'level': 'Native'}],
            'certifications': [{'name': 'AWS Solutions Architect – Associate', 'issuer': 'AWS', 'year': 2023}],
            'awards': [{'title': 'Hackathon winner', 'year': 2021}],
        }
    )
    result = asyncio.run(_fake([reply]).extract_profile('cv'))
    assert result is not None
    assert [(lang.name, lang.level) for lang in result.languages] == [('German', 'C1'), ('English', 'Native')]
    assert result.certifications[0].issuer == 'AWS'
    assert result.awards[0].issuer is None


def test_extract_profile_gives_up_after_two_bad_replies():
    assert asyncio.run(_fake(['nope', '{"experience": "wrong shape"}']).extract_profile('cv')) is None


def test_location_is_read_from_the_reply():
    reply = json.dumps({'location': {'city': None, 'country': 'Germany'}})
    result = asyncio.run(_fake([reply]).extract_profile('cv'))
    assert result is not None and result.location is not None and result.location.country == 'Germany'


def test_contacts_skip_project_links():
    found = redact(
        'linkedin.com/in/janedoe github.com/jdoe/some-repo github.com/jdoe https://acme.com https://shop.example.org '
        'http://localhost:5173'
    )
    got = contacts_from(found, 'jane@work.com')
    assert got['github_url'] == 'github.com/jdoe'
    assert got['linkedin_url'] == 'linkedin.com/in/janedoe'
    assert 'portfolio_url' not in got
