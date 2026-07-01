from __future__ import annotations

from dataclasses import dataclass
import re
from xml.etree import ElementTree
from zipfile import BadZipFile, ZipFile
from io import BytesIO

from fastapi import HTTPException

from app.schemas.public import ContractCheckFinding, ContractCheckResponse

MAX_CHECK_BYTES = 5 * 1024 * 1024
STANDARD_SECTIONS = {
    "confidential": "Confidentiality",
    "indemn": "Indemnity",
    "liabil": "Limitation of liability",
    "terminat": "Termination",
    "governing law": "Governing law",
}
COMMON_TYPOS = {
    "teh": "the",
    "recieve": "receive",
    "seperate": "separate",
    "liabilty": "liability",
    "indemnificaiton": "indemnification",
}


@dataclass(frozen=True)
class DocumentText:
    paragraphs: list[str]

    @property
    def text(self) -> str:
        return "\n".join(self.paragraphs)

    @property
    def word_count(self) -> int:
        return len(re.findall(r"\b[\w'-]+\b", self.text))


class DocumentChecker:
    def check_docx(self, file_name: str, content: bytes) -> ContractCheckResponse:
        if not file_name.lower().endswith(".docx"):
            raise HTTPException(status_code=400, detail="Only .docx files can be checked")
        if len(content) > MAX_CHECK_BYTES:
            raise HTTPException(status_code=413, detail="Document is too large for the free checker")

        document = extract_docx_text(content)
        if document.word_count == 0:
            raise HTTPException(status_code=400, detail="No readable Word document text was found")

        findings = [
            *find_possible_typos(document),
            *find_broken_cross_references(document),
            *find_unused_defined_terms(document),
            *find_missing_standard_sections(document),
        ]

        return ContractCheckResponse(
            file_name=file_name,
            stored=False,
            word_count=document.word_count,
            findings=findings[:20],
            disclaimer="Free preparation check only. This is not legal advice and no contract is saved or stored.",
            next_step="For a legal review, submit the contract for an attorney-approved Charter Law redline.",
        )


def extract_docx_text(content: bytes) -> DocumentText:
    try:
        with ZipFile(BytesIO(content)) as docx:
            xml = docx.read("word/document.xml")
    except (BadZipFile, KeyError) as exc:
        raise HTTPException(status_code=400, detail="The uploaded file is not a readable .docx document") from exc

    root = ElementTree.fromstring(xml)
    namespace = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs: list[str] = []

    for paragraph in root.findall(".//w:p", namespace):
        text = "".join(node.text or "" for node in paragraph.findall(".//w:t", namespace)).strip()
        if text:
            paragraphs.append(text)

    return DocumentText(paragraphs=paragraphs)


def find_possible_typos(document: DocumentText) -> list[ContractCheckFinding]:
    findings: list[ContractCheckFinding] = []
    lower_text = document.text.lower()

    for typo, correction in COMMON_TYPOS.items():
        if re.search(rf"\b{re.escape(typo)}\b", lower_text):
            findings.append(
                ContractCheckFinding(
                    type="possible_typo",
                    severity="warning",
                    title=f"Possible typo: {typo}",
                    detail=f"Check whether `{typo}` should be `{correction}`.",
                    evidence=typo,
                )
            )

    return findings


def find_broken_cross_references(document: DocumentText) -> list[ContractCheckFinding]:
    text = document.text
    referenced_sections = set(re.findall(r"\b(?:Section|Clause)\s+(\d+(?:\.\d+)*)", text, flags=re.IGNORECASE))
    present_sections = set()

    for paragraph in document.paragraphs:
        match = re.match(r"^\s*(\d+(?:\.\d+)*)[\).\s-]+", paragraph)
        if match:
            present_sections.add(match.group(1))

    missing = sorted(section for section in referenced_sections if section not in present_sections)

    return [
        ContractCheckFinding(
            type="broken_cross_reference",
            severity="warning",
            title=f"Referenced section {section} was not found",
            detail=f"The document refers to Section {section}, but no matching numbered heading was detected.",
            evidence=f"Section {section}",
        )
        for section in missing[:8]
    ]


def find_unused_defined_terms(document: DocumentText) -> list[ContractCheckFinding]:
    text = document.text
    terms = set(re.findall(r'["“]([A-Z][A-Za-z0-9& -]{2,40})["”]', text))
    findings: list[ContractCheckFinding] = []

    for term in sorted(terms):
        occurrences = len(re.findall(rf"\b{re.escape(term)}\b", text))
        if occurrences <= 1:
            findings.append(
                ContractCheckFinding(
                    type="unused_defined_term",
                    severity="info",
                    title=f"Defined term may be unused: {term}",
                    detail="This quoted capitalised term appears only once. If it is a defined term, it may be unused.",
                    evidence=term,
                )
            )

    return findings[:8]


def find_missing_standard_sections(document: DocumentText) -> list[ContractCheckFinding]:
    lower_text = document.text.lower()
    findings: list[ContractCheckFinding] = []

    for marker, section_name in STANDARD_SECTIONS.items():
        if marker not in lower_text:
            findings.append(
                ContractCheckFinding(
                    type="missing_standard_section",
                    severity="info",
                    title=f"Standard section not detected: {section_name}",
                    detail=f"No obvious {section_name.lower()} wording was detected. This may be fine, but it is worth checking.",
                    evidence=None,
                )
            )

    return findings


document_checker = DocumentChecker()
