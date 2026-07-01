from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, EmailStr, Field

FindingSeverity = Literal["info", "warning"]
FindingType = Literal[
    "broken_cross_reference",
    "missing_standard_section",
    "possible_typo",
    "unused_defined_term",
]


class ContractCheckFinding(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    type: FindingType
    severity: FindingSeverity
    title: str
    detail: str
    evidence: str | None = None


class ContractCheckResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    file_name: str = Field(serialization_alias="fileName")
    stored: bool
    word_count: int = Field(serialization_alias="wordCount")
    findings: list[ContractCheckFinding]
    disclaimer: str
    next_step: str = Field(serialization_alias="nextStep")


PublicIntakeTier = Literal["simple_review", "standard_redline", "full_negotiation"]
PublicIntakeUrgency = Literal["standard", "rush", "not_sure"]


class PublicIntakeRequest(BaseModel):
    model_config = ConfigDict(populate_by_name=True, str_strip_whitespace=True)

    name: str = Field(min_length=2, max_length=256)
    email: EmailStr = Field(max_length=320)
    company: str = Field(min_length=2, max_length=256)
    contract_type: str = Field(validation_alias="contractType", min_length=2, max_length=128)
    urgency: PublicIntakeUrgency
    service_tier: PublicIntakeTier = Field(validation_alias="serviceTier")
    notes: str = Field(default="", max_length=4000)


class PublicIntakeResponse(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    intake_id: str = Field(serialization_alias="intakeId")
    status: str
    created_at: datetime = Field(serialization_alias="createdAt")
    message: str
