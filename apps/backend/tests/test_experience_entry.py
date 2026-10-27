from src.schemas.profile import ExperienceEntry


def test_role_fields_accept_loose_spellings():
    e = ExperienceEntry(title='SDR', work_model='onsite', job_type='full time', seniority='SENIOR')
    assert (e.work_model, e.job_type, e.seniority) == ('On-site', 'Full-time', 'Senior')


def test_unknown_role_values_are_dropped_not_rejected():
    e = ExperienceEntry(title='SDR', work_model='Flexible', job_type='Freelance', seniority=3)
    assert (e.work_model, e.job_type, e.seniority) == (None, None, None)


def test_role_fields_are_optional():
    assert ExperienceEntry(title='SDR').work_model is None
