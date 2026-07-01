from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

PlaybookSeverity = Literal["low", "medium", "high", "critical"]


class PlaybookCheckCreate(BaseModel):
    key: str = Field(min_length=2, max_length=128)
    title: str = Field(min_length=2, max_length=256)
    detection: str = Field(min_length=2)
    severity: PlaybookSeverity
    remediation_intent: str = Field(min_length=2)
    preferred_language: str = Field(min_length=2)
    acceptable_fallback: str = Field(min_length=2)
    unacceptable_fallback: str = Field(min_length=2)


class PlaybookCreate(BaseModel):
    name: str = Field(min_length=2, max_length=256)
    contract_type: str = Field(min_length=2, max_length=128)
    jurisdiction: str = Field(default="general", min_length=2, max_length=128)


class PlaybookCheck(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    key: str
    title: str
    detection: str
    severity: PlaybookSeverity
    remediation_intent: str = Field(serialization_alias="remediationIntent")
    preferred_language: str = Field(serialization_alias="preferredLanguage")
    acceptable_fallback: str = Field(serialization_alias="acceptableFallback")
    unacceptable_fallback: str = Field(serialization_alias="unacceptableFallback")
    accuracy_correct: int = Field(serialization_alias="accuracyCorrect")
    accuracy_total: int = Field(serialization_alias="accuracyTotal")
    created_at: datetime = Field(serialization_alias="createdAt")


class Playbook(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    id: str
    name: str
    contract_type: str = Field(serialization_alias="contractType")
    jurisdiction: str
    created_at: datetime = Field(serialization_alias="createdAt")
    checks: list[PlaybookCheck] = []
