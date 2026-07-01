from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PrepMode = Literal["stub", "anthropic"]
PrepSeverity = Literal["low", "medium", "high", "critical"]
PrepFeedbackAction = Literal["apply", "dismiss", "edit"]


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


class AIPrepFeedbackRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    issue_index: int = Field(ge=0, validation_alias="issueIndex")
    action: PrepFeedbackAction
    reason_tag: str = Field(validation_alias="reasonTag", min_length=2, max_length=128)
    corrected_detail: str | None = Field(default=None, validation_alias="correctedDetail")


class AIPrepFeedbackResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    matter_id: str = Field(serialization_alias="matterId")
    issue_title: str = Field(serialization_alias="issueTitle")
    action: PrepFeedbackAction
    reason_tag: str = Field(serialization_alias="reasonTag")
    playbook_check_id: str | None = Field(default=None, serialization_alias="playbookCheckId")
    accuracy_correct: int | None = Field(default=None, serialization_alias="accuracyCorrect")
    accuracy_total: int | None = Field(default=None, serialization_alias="accuracyTotal")
