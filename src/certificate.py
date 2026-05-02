"""
certificate.py — certificate generator

Produces JSON (machine layer) and PDF (human layer) from review output.
"""

import json
import hashlib
import uuid
from datetime import datetime, timezone
from pathlib import Path
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, Table, TableStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register DejaVu fonts for full Unicode/UTF-8 support (Croatian chars etc.)
_FONT_DIR = "/usr/share/fonts/truetype/dejavu"
pdfmetrics.registerFont(TTFont("DejaVu", f"{_FONT_DIR}/DejaVuSans.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", f"{_FONT_DIR}/DejaVuSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DejaVu-Italic", f"{_FONT_DIR}/DejaVuSans-Oblique.ttf"))
pdfmetrics.registerFontFamily("DejaVu", normal="DejaVu", bold="DejaVu-Bold", italic="DejaVu-Italic")


def _cert_id(session_hash: str) -> str:
    return "imp_" + session_hash[:16]


def build_json(
    subject_name: str,
    subject_email: str,
    session_transcript: str,
    review_result: dict,
    working_model: str,
    review_model: str,
    doi: str = "",
    ipfs_cid: str = "",
) -> dict:
    session_hash = hashlib.sha256(session_transcript.encode()).hexdigest()
    email_hash = "hash:" + hashlib.sha256(subject_email.lower().encode()).hexdigest()
    now = datetime.now(timezone.utc).isoformat()

    certs = []
    for c in review_result.get("certificates", []):
        entry = {
            "type": c["type"],
            "label": c["label"],
            "model_agnostic": c.get("model_agnostic", True),
            "statement": c["statement"],
            "issued_at": now,
        }
        if c["type"] == "project_record":
            entry["issuing_model"] = working_model
            entry["projects"] = c.get("projects", [])
            entry["model_agnostic"] = False
        certs.append(entry)

    cert = {
        "schema_version": "1.1",
        "id": _cert_id(session_hash),
        "subject": {
            "name": subject_name,
            "email": email_hash,
            "declaration": "I confirm this is my own interaction — I am personally at this keyboard, and this work is mine.",
        },
        "issued_at": now,
        "working_model": working_model,
        "review_model": review_model,
        "trust_tier": 0,
        "certificates": certs,
        "session_hash": session_hash,
        "doi": doi,
        "ipfs_cid": ipfs_cid,
        "no_obligations": (
            "This certificate reflects the independent judgment of an AI model. "
            "It carries no obligations, warranties, or representations by any company "
            "or organization. The issuing model attests only to what it observed."
        ),
    }

    # certificate_hash covers the full JSON including assessment — detects post-issuance tampering
    # computed over cert without the hash field itself
    cert_for_hashing = {k: v for k, v in cert.items() if k != "certificate_hash"}
    cert["certificate_hash"] = hashlib.sha256(
        json.dumps(cert_for_hashing, sort_keys=True).encode()
    ).hexdigest()

    return cert


def build_pdf(cert_json: dict, output_path: str) -> str:
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    styles = getSampleStyleSheet()
    W = A4[0] - 40 * mm

    title_style = ParagraphStyle("title", fontSize=22, alignment=TA_CENTER,
                                  spaceAfter=2 * mm, textColor=colors.HexColor("#1a1a1a"),
                                  fontName="DejaVu-Bold")
    sub_style = ParagraphStyle("sub", fontSize=11, alignment=TA_CENTER,
                                spaceAfter=4 * mm, textColor=colors.HexColor("#555555"),
                                fontName="DejaVu", leading=16)
    subject_style = ParagraphStyle("subject", fontSize=16, alignment=TA_CENTER,
                                    spaceAfter=4 * mm, fontName="DejaVu-Bold",
                                    textColor=colors.HexColor("#1a1a1a"), leading=22)
    label_style = ParagraphStyle("label", fontSize=13, spaceBefore=4 * mm, spaceAfter=3 * mm,
                                  fontName="DejaVu-Bold", leading=18,
                                  textColor=colors.HexColor("#1a1a1a"))
    body_style = ParagraphStyle("body", fontSize=10, spaceAfter=6 * mm,
                                 leading=15, alignment=TA_JUSTIFY,
                                 fontName="DejaVu",
                                 textColor=colors.HexColor("#333333"))
    small_style = ParagraphStyle("small", fontSize=8, textColor=colors.HexColor("#888888"),
                                  alignment=TA_CENTER, leading=12, fontName="DejaVu")
    doi_style = ParagraphStyle("doi", fontSize=9, fontName="DejaVu-Bold",
                                 alignment=TA_CENTER, textColor=colors.HexColor("#1a1a1a"),
                                 spaceAfter=3 * mm)

    story = []

    story.append(Spacer(1, 6 * mm))
    story.append(Paragraph("IMPRIMATUR", title_style))
    story.append(Paragraph("Model-Evaluated Competency Certificate", sub_style))
    story.append(HRFlowable(width=W, thickness=1, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 6 * mm))

    story.append(Paragraph("This certificate is issued to", sub_style))
    story.append(Paragraph(cert_json["subject"]["name"], subject_style))
    story.append(Spacer(1, 4 * mm))

    issued = cert_json["issued_at"][:10]
    story.append(Paragraph(f"Issued: {issued}", sub_style))
    story.append(Paragraph(
        f"Working model: {cert_json['working_model']} · "
        f"Review model: {cert_json['review_model']}", sub_style))
    tier = cert_json.get("trust_tier", 0)
    tier_label = {0: "single session · single model", 1: "multi-session · same model family", 2: "multi-model consensus"}.get(tier, "unknown")
    story.append(Paragraph(f"Trust tier: {tier} ({tier_label})", small_style))

    story.append(Spacer(1, 6 * mm))
    story.append(HRFlowable(width=W, thickness=0.5, color=colors.HexColor("#eeeeee")))
    story.append(Spacer(1, 4 * mm))

    for c in cert_json["certificates"]:
        story.append(Paragraph(c["label"], label_style))
        if not c.get("model_agnostic", True):
            story.append(Paragraph(
                f"<i>Model-specific · Issuing model: {c.get('issuing_model', cert_json['working_model'])}</i>",
                ParagraphStyle("italic", fontSize=9, textColor=colors.HexColor("#888888"),
                                spaceAfter=2 * mm)
            ))
        story.append(Paragraph(c["statement"], body_style))

        if c.get("projects"):
            for p in c["projects"]:
                story.append(Paragraph(
                    f"<b>{p['name']}</b> — {p['description']}",
                    ParagraphStyle("proj", fontSize=9, leftIndent=10,
                                   spaceAfter=2 * mm, textColor=colors.HexColor("#444444"))
                ))
        story.append(Spacer(1, 3 * mm))

    story.append(Spacer(1, 4 * mm))
    story.append(HRFlowable(width=W, thickness=1, color=colors.HexColor("#cccccc")))
    story.append(Spacer(1, 4 * mm))

    if cert_json.get("doi"):
        story.append(Paragraph(f"DOI: {cert_json['doi']}", doi_style))

    story.append(Paragraph(
        f"Certificate ID: {cert_json['id']} · "
        f"Session hash: ...{cert_json['session_hash'][-8:]}",
        small_style
    ))
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph(cert_json["no_obligations"], small_style))

    doc.build(story)
    return output_path


def generate(
    subject_name: str,
    subject_email: str,
    session_transcript: str,
    review_result: dict,
    working_model: str,
    review_model: str,
    doi: str = "",
    ipfs_cid: str = "",
    output_dir: str = "certificates",
) -> tuple[dict, str]:
    """
    Returns (cert_json, pdf_path).
    """
    Path(output_dir).mkdir(exist_ok=True)

    cert_json = build_json(
        subject_name, subject_email, session_transcript,
        review_result, working_model, review_model, doi, ipfs_cid
    )

    pdf_path = str(Path(output_dir) / f"{cert_json['id']}.pdf")
    build_pdf(cert_json, pdf_path)

    json_path = str(Path(output_dir) / f"{cert_json['id']}.json")
    with open(json_path, "w") as f:
        json.dump(cert_json, f, indent=2)

    return cert_json, pdf_path
