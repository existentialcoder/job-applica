import os
import aiofiles
from fastapi import HTTPException, UploadFile
from typing import Optional
import aiobotocore.session

from ..core.config import settings

CHUNK_SIZE = 256 * 1024  # 256 KB


class FileUploader:
    def __init__(self, destination_path: str, file: Optional[UploadFile] = None, max_size_mb: int = 0):
        self.file = file
        self.destination_path = destination_path
        self.max_size_bytes = max_size_mb * 1024 * 1024

    async def _read_file(self) -> tuple[bytes, int]:
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

    async def delete_file_from_local(self) -> None:
        if os.path.exists(self.destination_path):
            os.remove(self.destination_path)

    async def delete_file_from_cloudflare(self, bucket: str, key: str) -> None:
        session = aiobotocore.session.AioSession()
        async with session.create_client(
            's3',
            endpoint_url=f'https://{settings.CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
            region_name='auto',
        ) as client:
            await client.delete_object(
                Bucket=bucket,
                Key=key
            )

    async def upload_local(self) -> int:
        data, size = await self._read_file()
        os.makedirs(os.path.dirname(self.destination_path), exist_ok=True)
        async with aiofiles.open(self.destination_path, 'wb') as f:
            await f.write(data)
        return size

    async def upload_to_cloudflare(self, bucket: str, key: str) -> int:
        data, size = await self._read_file()
        session = aiobotocore.session.AioSession()
        async with session.create_client(
            's3',
            endpoint_url=f'https://{settings.CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
            region_name='auto',
        ) as client:
            await client.put_object(
                Bucket=bucket,
                Key=key,
                Body=data,
                ContentType=self.file.content_type or 'application/octet-stream',
            )
        return size

    async def upload_disk_to_cloudflare(self, bucket: str, key: str, content_type: str) -> None:
        """Upload an already-saved local file to R2. Use after upload_local() so the
        file bytes don't need to be re-read from the (exhausted) UploadFile stream."""
        async with aiofiles.open(self.destination_path, 'rb') as f:
            data = await f.read()
        session = aiobotocore.session.AioSession()
        async with session.create_client(
            's3',
            endpoint_url=f'https://{settings.CLOUDFLARE_ACCOUNT_ID}.r2.cloudflarestorage.com',
            aws_access_key_id=settings.CLOUDFLARE_R2_ACCESS_KEY_ID,
            aws_secret_access_key=settings.CLOUDFLARE_R2_SECRET_ACCESS_KEY,
            region_name='auto',
        ) as client:
            await client.put_object(
                Bucket=bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
            )
