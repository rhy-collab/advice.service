import os
from collections.abc import Iterator

import pytest

# Tests must be hermetic: never let a developer's backend/.env (loaded by
# app.config) route AI-prep or board calls to the real Anthropic API.
os.environ.pop("ANTHROPIC_API_KEY", None)


@pytest.fixture(autouse=True)
def _no_real_anthropic(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("ANTHROPIC_API_KEY", raising=False)
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db.session import Base
import app.models.board  # noqa: F401
import app.models.intake  # noqa: F401
import app.models.matter  # noqa: F401
import app.models.playbook  # noqa: F401
from app.services.matter_service import MatterService
from app.services.storage_service import UploadTargetData


class FakeStorageService:
    def bucket_name(self) -> str:
        return "test-bucket"

    def create_upload_target(self, matter_id: str, file_name: str) -> UploadTargetData:
        return UploadTargetData(
            method="PUT",
            url=f"https://storage.example.test/{matter_id}/{file_name}",
            bucket="test-bucket",
            object_name=f"matters/{matter_id}/source/{file_name}",
            content_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            mode="demo",
        )

    def create_download_url(self, bucket: str, object_name: str) -> str:
        return f"https://storage.example.test/download/{object_name}"


@pytest.fixture
def session_factory() -> Iterator[sessionmaker[Session]]:
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    factory = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)
    yield factory
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def matter_service(session_factory: sessionmaker[Session]) -> MatterService:
    return MatterService(session_factory, storage=FakeStorageService(), seed_demo=True)
