import asyncio
import io

import pytest
from fastapi import HTTPException, UploadFile
from starlette.datastructures import Headers

from src.services import resume as resume_service

DOCX = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'


def test_unreadable_file_is_rejected_and_removed(monkeypatch):
    deleted = []

    class Storage:
        stored_name = 'x.docx'

        def __init__(self, **_):
            pass

        async def upload(self):
            return 'key', 4

        async def delete_file(self, key):
            deleted.append(key)

    monkeypatch.setattr(resume_service, 'get_file_storage_factory', lambda: Storage)
    file = UploadFile(io.BytesIO(b'junk'), filename='cv.docx', headers=Headers({'content-type': DOCX}))

    with pytest.raises(HTTPException) as err:
        asyncio.run(resume_service.upload_resume(None, 1, file))  # type: ignore[arg-type]

    assert err.value.status_code == 422
    assert deleted == ['key']
