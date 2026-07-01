import json

from app.services.ai_prep_service import AIPrepService


class FakeAnthropicClient:
    def __init__(self, text: str) -> None:
        self.text = text
        self.payloads: list[dict] = []

    def create_message(self, payload: dict) -> dict:
        self.payloads.append(payload)
        return {"content": [{"type": "text", "text": self.text}]}


def test_ai_prep_uses_anthropic_when_key_is_set(monkeypatch) -> None:
    fake = FakeAnthropicClient(
        json.dumps(
            {
                "summary": "Attorney-facing AI summary.",
                "issues": [
                    {
                        "title": "Check warranty scope",
                        "severity": "medium",
                        "detail": "Warranty wording is broader than expected.",
                        "confidence": "strong",
                        "playbook_check_id": "check_123",
                        "playbook_check_key": "warranty_scope",
                    }
                ],
            }
        )
    )
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    service = AIPrepService(anthropic_client=fake)  # type: ignore[arg-type]

    prep = service.generate_for_uploaded_contract("contract.docx", "standard_redline")

    assert prep.mode == "anthropic"
    assert prep.summary == "Attorney-facing AI summary."
    assert prep.issues[0].playbook_check_key == "warranty_scope"
    assert fake.payloads
    assert fake.payloads[0]["messages"][0]["content"][0]["text"]


def test_ai_prep_anthropic_parse_falls_back_to_safe_stub(monkeypatch) -> None:
    fake = FakeAnthropicClient("not-json")
    monkeypatch.setenv("ANTHROPIC_API_KEY", "test-key")
    service = AIPrepService(anthropic_client=fake)  # type: ignore[arg-type]

    prep = service.generate_for_uploaded_contract("contract.docx", "standard_redline")

    assert prep.mode == "anthropic"
    assert "Internal preparation summary" in prep.summary
    assert prep.issues
