from io import BytesIO
from zipfile import ZipFile

import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient

from app.main import app
from app.services.document_checker import document_checker


def make_docx(paragraphs: list[str]) -> bytes:
    body = "".join(
        f"<w:p><w:r><w:t>{paragraph}</w:t></w:r></w:p>"
        for paragraph in paragraphs
    )
    xml = f"""<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
  <w:body>{body}</w:body>
</w:document>"""
    buffer = BytesIO()
    with ZipFile(buffer, "w") as archive:
        archive.writestr("word/document.xml", xml)
    return buffer.getvalue()


def test_contract_checker_returns_non_persistent_report() -> None:
    content = make_docx(
        [
            '1. Confidentiality. "Unused Term" means the trial copy.',
            "2. Payment. See Section 9.1 for the seperate payment schedule.",
        ]
    )

    report = document_checker.check_docx("vendor-agreement.docx", content)

    assert report.stored is False
    assert report.word_count > 0
    assert "not legal advice" in report.disclaimer
    assert any(finding.type == "possible_typo" for finding in report.findings)
    assert any(finding.type == "broken_cross_reference" for finding in report.findings)
    assert any(finding.type == "unused_defined_term" for finding in report.findings)
    assert any(finding.type == "missing_standard_section" for finding in report.findings)


def test_contract_checker_rejects_non_docx_extension() -> None:
    with pytest.raises(HTTPException) as exc_info:
        document_checker.check_docx("contract.pdf", b"not a word document")

    assert exc_info.value.status_code == 400


def test_public_contract_checker_endpoint() -> None:
    client = TestClient(app)
    response = client.post(
        "/v1/public/check-contract",
        files={
            "file": (
                "sample.docx",
                make_docx(["1. Services. The parties recieve the document."]),
                "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            )
        },
    )

    assert response.status_code == 200
    payload = response.json()
    assert payload["fileName"] == "sample.docx"
    assert payload["stored"] is False
    assert payload["wordCount"] > 0
