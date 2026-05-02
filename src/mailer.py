"""
mailer.py — email delivery

Sends certificate to subject via Gmail SMTP.
Styled like Coursera — certificate as attachment + inline summary.
"""

import smtplib
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from pathlib import Path


GMAIL_USER = ""
GMAIL_APP_PASSWORD = ""

EMAIL_HTML = """
<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<style>
  body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
         background: #f5f5f5; margin: 0; padding: 0; }}
  .container {{ max-width: 600px; margin: 40px auto; background: white;
                border-radius: 8px; overflow: hidden;
                box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
  .header {{ background: #1a1a1a; color: white; padding: 32px 40px; text-align: center; }}
  .header h1 {{ margin: 0; font-size: 28px; letter-spacing: 4px; font-weight: 300; }}
  .header p {{ margin: 8px 0 0; font-size: 13px; color: #999; letter-spacing: 1px; }}
  .body {{ padding: 40px; }}
  .greeting {{ font-size: 18px; color: #1a1a1a; margin-bottom: 16px; }}
  .cert-box {{ background: #f9f9f9; border-left: 3px solid #1a1a1a;
               padding: 16px 20px; margin: 20px 0; border-radius: 0 4px 4px 0; }}
  .cert-name {{ font-weight: 600; font-size: 15px; color: #1a1a1a; margin-bottom: 6px; }}
  .cert-stmt {{ font-size: 13px; color: #555; line-height: 1.6; }}
  .meta {{ font-size: 12px; color: #999; margin-top: 24px; border-top: 1px solid #eee;
           padding-top: 16px; }}
  .doi {{ font-family: monospace; font-size: 12px; color: #333; }}
  .disclaimer {{ font-size: 11px; color: #bbb; margin-top: 20px; line-height: 1.5; }}
  .footer {{ background: #f9f9f9; padding: 24px 40px; text-align: center;
             font-size: 12px; color: #999; }}
</style>
</head>
<body>
<div class="container">
  <div class="header">
    <h1>IMPRIMATUR</h1>
    <p>Model-Evaluated Competency Certificate</p>
  </div>
  <div class="body">
    <div class="greeting">Congratulations, {name}.</div>
    <p style="color:#555;font-size:14px;line-height:1.6;">
      An independent AI review model has evaluated your session and issued
      the following certificate{plural}:
    </p>

    {cert_blocks}

    <div class="meta">
      <p>Issued: <strong>{issued}</strong></p>
      <p>Working model: <strong>{working_model}</strong></p>
      <p>Review model: <strong>{review_model}</strong></p>
      {doi_line}
      <p>Certificate ID: <code>{cert_id}</code></p>
    </div>

    <p style="color:#555;font-size:13px;margin-top:20px;">
      Your certificate is attached as a PDF. The JSON machine-readable version
      is included for use with AI model context.
    </p>

    <div class="disclaimer">{no_obligations}</div>
  </div>
  <div class="footer">
    imprimatur · the model certifies the human
  </div>
</div>
</body>
</html>
"""

CERT_BLOCK = """
    <div class="cert-box">
      <div class="cert-name">{label}</div>
      <div class="cert-stmt">{statement}</div>
    </div>
"""


def send(cert_json: dict, pdf_path: str, to_email: str) -> bool:
    """Send certificate email with PDF + JSON attachments."""

    certs = cert_json["certificates"]
    plural = "s" if len(certs) > 1 else ""

    cert_blocks = "".join(
        CERT_BLOCK.format(label=c["label"], statement=c["statement"])
        for c in certs
    )

    doi_line = (
        f'<p>DOI: <span class="doi">{cert_json["doi"]}</span></p>'
        if cert_json.get("doi") else ""
    )

    html = EMAIL_HTML.format(
        name=cert_json["subject"]["name"],
        plural=plural,
        cert_blocks=cert_blocks,
        issued=cert_json["issued_at"][:10],
        working_model=cert_json["working_model"],
        review_model=cert_json["review_model"],
        doi_line=doi_line,
        cert_id=cert_json["id"],
        no_obligations=cert_json["no_obligations"],
    )

    cert_labels = ", ".join(c["label"] for c in certs)
    subject = f"Imprimatur Certificate: {cert_labels}"

    msg = MIMEMultipart("mixed")
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    msg["Subject"] = subject

    msg.attach(MIMEText(html, "html"))

    with open(pdf_path, "rb") as f:
        pdf_part = MIMEApplication(f.read(), _subtype="pdf")
        pdf_part.add_header("Content-Disposition", "attachment",
                            filename=f"{cert_json['id']}.pdf")
        msg.attach(pdf_part)

    json_part = MIMEApplication(
        json.dumps(cert_json, indent=2).encode(),
        _subtype="json"
    )
    json_part.add_header("Content-Disposition", "attachment",
                         filename=f"{cert_json['id']}.json")
    msg.attach(json_part)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        server.sendmail(GMAIL_USER, to_email, msg.as_string())

    return True
