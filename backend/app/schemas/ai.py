from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PrepMode = Literal["stub", "anthropic"]
PrepSeverity = Literal["low", "medium", "high", "critical"]


class AIPrepIssue(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    title: str
    severity: PrepSeverity
    detail: str
    confidence: Literal["weak", "medium", "strong"]
    playbook_check_id: str | None = Field(default=None, serialization_alias="playbookCheckId")
    playbook_check_key: str | None = Field(default=None, serialization_alias="playbookCheckKey")


class AIPrepResult(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    matter_id: str = Field(serialization_alias="matterId")
    mode: PrepMode
    summary: str
    issues: list[AIPrepIssue]
    created_at: datetime = Field(serialization_alias="createdAt")


class AttorneyAIPrepResponse(BaseModel):
    prep: AIPrepResult
