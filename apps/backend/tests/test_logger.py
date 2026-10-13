import json
import logging
import sys

from src.core.logger import JsonFormatter


def test_json_formatter_includes_extras_and_exceptions():
    try:
        raise ValueError('boom')
    except ValueError:
        record = logging.makeLogRecord(
            {'name': 'x', 'levelname': 'ERROR', 'msg': 'hi %s', 'args': ('there',), 'job_id': 7}
        )
        record.exc_info = sys.exc_info()
    entry = json.loads(JsonFormatter().format(record))
    assert entry['msg'] == 'hi there'
    assert entry['level'] == 'ERROR'
    assert entry['job_id'] == 7
    assert 'ValueError: boom' in entry['exc']
    assert 'args' not in entry
