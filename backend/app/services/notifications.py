from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import os


@dataclass(frozen=True)
class NotificationRecord:
    matter_id: str
    organisation_id: str
    status: str
    channel: str
    subject: str
    body: str
    sent_at: datetime


class NotificationService:
    def __init__(self) -> None:
        self.sent_notifications: list[NotificationRecord] = []

    def notify_status_change(self, matter_id: str, organisation_id: str, status: str) -> NotificationRecord:
        record = NotificationRecord(
            matter_id=matter_id,
            organisation_id=organisation_id,
            status=status,
            channel=notification_channel(),
            subject=status_subject(status),
            body=status_body(status),
            sent_at=datetime.now(timezone.utc),
        )
        self.sent_notifications.append(record)
        return record


def notification_channel() -> str:
    if os.getenv("RESEND_API_KEY"):
        return "email"
    return "log"


def status_subject(status: str) -> str:
    if status == "delivered":
        return "Your Charter Law review is ready"
    return "Your Charter Law matter status changed"


def status_body(status: str) -> str:
    if status == "delivered":
        return "Your attorney-approved review is ready in the Charter Law portal."
    return f"Your Charter Law matter moved to {status}."


notification_service = NotificationService()
