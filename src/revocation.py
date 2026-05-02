"""
revocation.py — certificate revocation list

Revoked certificates are stored in revocation.json.
Verifier checks this list before declaring a certificate VALID.

Revocation is manual — requires access to this file.
A revoked certificate remains on Zenodo but is flagged as invalid by the verifier.
"""

import json
from datetime import datetime, timezone
from pathlib import Path


DEFAULT_REVOCATION_FILE = "revocation.json"


def _load(revocation_file: str) -> dict:
    if Path(revocation_file).exists():
        with open(revocation_file) as f:
            return json.load(f)
    return {"revoked": []}


def is_revoked(cert_id: str, revocation_file: str = DEFAULT_REVOCATION_FILE) -> tuple[bool, str]:
    """Returns (is_revoked: bool, reason: str)."""
    data = _load(revocation_file)
    for entry in data.get("revoked", []):
        if entry["id"] == cert_id:
            return True, entry.get("reason", "revoked")
    return False, ""


def revoke(cert_id: str, reason: str, revocation_file: str = DEFAULT_REVOCATION_FILE):
    """Add a certificate to the revocation list."""
    data = _load(revocation_file)
    if not any(e["id"] == cert_id for e in data["revoked"]):
        data["revoked"].append({
            "id": cert_id,
            "reason": reason,
            "revoked_at": datetime.now(timezone.utc).isoformat(),
        })
    with open(revocation_file, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Revoked: {cert_id}")
