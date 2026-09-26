import os
import uuid

import aiobotocore.session
import aiofiles
from fastapi import HTTPException, UploadFile

from ..core.config import settings

CHUNK_SIZE = 256 * 1024
# Local files live under uploads/users/ so pre-refactor files and stored avatar URLs keep resolving.
LOCAL_BASE = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'uploads', 'users'))


class FileStorage:
    def __init__(
        self,
        destination_path: str = '',
        file: UploadFile | None = None,
        max_size_mb: int = 5,
        stored_name: str | None = None,
    ):
        self.file = file
        self.destination_path = destination_path
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.stored_name = stored_name

    async def _read_file(self) -> tuple[bytes, int]:
        assert self.file is not None  # upload() is only called on instances built with a file
        chunks, size = [], 0
        while chunk := await self.file.read(CHUNK_SIZE):
            size += len(chunk)
            if size > self.max_size_bytes:
                raise HTTPException(
                    status_code=413,
                    detail=f'File exceeds {self.max_size_bytes // (1024 * 1024)} MB limit',
                )
            chunks.append(chunk)
        return b''.join(chunks), size

    def _get_key(self) -> str:
        assert self.file is not None
        if self.stored_name is None:
            ext = os.path.splitext(self.file.filename or '')[1]
            self.stored_name = f'{uuid.uuid4().hex}{ext}'
        return f'{self.destination_path}/{self.stored_name}'

    async def upload(self) -> tuple[str, int]:
        raise NotImplementedError

    async def delete_file(self, key: str) -> None:
        raise NotImplementedError


class LocalFileStorage(FileStorage):
    async def upload(self) -> tuple[str, int]:
        data, size = await self._read_file()
        key = self._get_key()
        file_dest = os.path.join(LOCAL_BASE, key)
        os.makedirs(os.path.dirname(file_dest), exist_ok=True)
        async with aiofiles.open(file_dest, 'wb') as f:
            await f.write(data)
        return key, size

    async def delete_file(self, key: str) -> None:
        path = os.path.join(LOCAL_BASE, key)
        if os.path.exists(path):
            os.remove(path)


class R2FileStorage(FileStorage):
    def _client(self):
        return aiobotocore.session.AioSession().create_client(
            's3',
            endpoint_url=f'https://{settings.CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
            region_name='auto',
        )

    async def upload(self) -> tuple[str, int]:
        assert self.file is not None
        data, size = await self._read_file()
        key = self._get_key()
        async with self._client() as client:
            await client.put_object(
                Bucket=settings.CLOUDFLARE_R2_BUCKET_NAME,
                Key=key,
                Body=data,
                ContentType=self.file.content_type or 'application/octet-stream',
            )
        return key, size

    async def delete_file(self, key: str) -> None:
        async with self._client() as client:
            await client.delete_object(Bucket=settings.CLOUDFLARE_R2_BUCKET_NAME, Key=key)


def get_file_storage_factory() -> type[FileStorage]:
    return R2FileStorage if settings.APP_ENV != 'local' else LocalFileStorage
