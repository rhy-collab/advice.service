from dataclasses import dataclass
from datetime import timedelta
import os
from typing import Literal


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

    def _blob(self, bucket: str, object_name: str):
        from google.cloud import storage  # lazy import keeps tests light

        return storage.Client().bucket(bucket).blob(object_name)

    def _ttl(self) -> int:
        return int(os.getenv("GCS_SIGNED_URL_TTL_MINUTES", "15"))

    def create_upload_target(self, matter_id: str, file_name: str) -> UploadTargetData:
        bucket_name = self.bucket_name()
        object_name = f"matters/{matter_id}/source/{file_name}"
        content_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            url = self._blob(bucket_name, object_name).generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=self._ttl()),
                method="PUT",
                content_type=content_type,
            )
            return UploadTargetData("PUT", url, bucket_name, object_name, content_type, "gcs")

        return UploadTargetData(
            "PUT",
            f"https://storage.googleapis.com/demo-upload/{object_name}",
            bucket_name,
            object_name,
            content_type,
            "demo",
        )

    def create_download_url(self, bucket: str, object_name: str) -> str:
        """Short-lived SIGNED GET url for a confidential deliverable.

        Never returns a public object url for real files; only a clearly-marked
        demo url when no GCS credentials are configured.
        """
        if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
            return self._blob(bucket, object_name).generate_signed_url(
                version="v4",
                expiration=timedelta(minutes=self._ttl()),
                method="GET",
            )
        return f"https://storage.googleapis.com/demo-download/{bucket}/{object_name}"


storage_service = StorageService()
