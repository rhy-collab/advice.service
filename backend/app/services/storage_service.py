from dataclasses import dataclass
from datetime import timedelta
import os
from typing import Literal

from google.cloud import storage


@dataclass(frozen=True)
class UploadTargetData:
    method: Literal["PUT"]
    url: str
    bucket: str
    object_name: str
    content_type: str
    mode: Literal["gcs", "demo"]


class StorageService:
    def bucket_name(self) -> str:
        return os.getenv("GCS_BUCKET", "charter-law-contracts-dev")

    def create_upload_target(self, matter_id: str, file_name: str) -> UploadTargetData:
        bucket_name = self.bucket_name()
        object_name = f"matters/{matter_id}/source/{file_name}"
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            client = storage.Client()
            bucket = client.bucket(bucket_name)
            blob = bucket.blob(object_name)
            ttl_minutes = int(os.getenv("GCS_SIGNED_URL_TTL_MINUTES", "15"))
            url = blob.generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=ttl_minutes),
                method="PUT",
                content_type=content_type,
            )
            return UploadTargetData(
                method="PUT",
                url=url,
                bucket=bucket_name,
                object_name=object_name,
                content_type=content_type,
                mode="gcs",
            )

        return UploadTargetData(
            method="PUT",
            url=f"https://storage.googleapis.com/demo-upload/{object_name}",
            bucket=bucket_name,
            object_name=object_name,
            content_type=content_type,
            mode="demo",
        )


storage_service = StorageService()
