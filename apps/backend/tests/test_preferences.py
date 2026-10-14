import pytest
from pydantic import ValidationError

from src.schemas.preferences import JobPreferences


def test_reuses_tracker_enums():
    prefs = JobPreferences(work_models=['Remote', 'Hybrid'], seniority=['Senior'], job_types=['Full-time'])
    assert prefs.model_dump(mode='json')['work_models'] == ['Remote', 'Hybrid']


def test_rejects_unknown_work_model():
    with pytest.raises(ValidationError):
        JobPreferences(work_models=['Anywhere'])


def test_salary_needs_currency():
    with pytest.raises(ValidationError):
        JobPreferences(salary_min=60000)
    assert JobPreferences(salary_min=60000, salary_currency='EUR', salary_period='year').salary_min == 60000
